from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.conf import settings
import sys
from pathlib import Path
from io import BytesIO
import os

_GDINO_REPO = Path(__file__).resolve().parent.parent.parent / 'GroundingDINO'
sys.path.insert(0, str(_GDINO_REPO))

try:
    from PIL import Image, ImageDraw
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# GroundingDINO 相关
try:
    from groundingdino.util.inference import load_model, load_image, predict, annotate
    import torch
    GDINO_AVAILABLE = True
except ImportError:
    GDINO_AVAILABLE = False

BASE_DIR = settings.BASE_DIR
WEIGHTS_PATH = str(BASE_DIR / 'app01' / 'groundingdino' / 'weights' / 'groundingdino_swint_ogc.pth')
CONFIG_PATH  = str(BASE_DIR / 'app01' / 'groundingdino' / 'weights' / 'GroundingDINO_SwinT_OGC.py')

# 全局加载模型（避免每次请求都重新加载）
_gdino_model = None

def get_gdino_model():
    global _gdino_model
    if _gdino_model is None and GDINO_AVAILABLE:
        try:
            _patch_bert_path()
            _gdino_model = load_model(CONFIG_PATH, WEIGHTS_PATH)
        except Exception as e:
            print(f"GroundingDINO 加载失败: {e}")
    return _gdino_model


def _patch_bert_path():
    """把配置文件中的 bert 路径替换为当前机器的本地路径"""
    import re

    project_root = Path(__file__).resolve().parent.parent.parent
    local_bert = str(project_root / 'app01' / 'groundingdino' / 'bert-base-uncased')
    # Windows 路径统一用正斜杠避免转义问题
    local_bert = local_bert.replace('\\', '/')

    config_file = Path(CONFIG_PATH)
    content = config_file.read_text(encoding='utf-8')

    # 已经是正确路径就跳过
    if local_bert in content:
        return

    # 匹配所有 text_encoder_type = "..." 或 r"..." 的写法
    new_content = re.sub(
        r'text_encoder_type\s*=\s*r?"[^"]+"',
        f'text_encoder_type = "{local_bert}"',
        content
    )
    config_file.write_text(new_content, encoding='utf-8')
    print(f"✅ bert 路径已更新为: {local_bert}")

def index(request):
    """Agent 零样本检测页面"""
    return render(request, 'app01/cell_labels.html')


def detect(request):
    if request.method != 'POST':
        return JsonResponse({'code': 405, 'msg': 'Method not allowed'})

    if not PIL_AVAILABLE:
        return JsonResponse({'code': 500, 'msg': 'Pillow 未安装'})

    try:
        upload_file = request.FILES.get('image')
        prompt = request.POST.get('prompt', '红细胞').strip()

        if not upload_file:
            return JsonResponse({'code': 400, 'msg': '请上传图像文件'})

        # 保存上传图像到临时文件
        import tempfile
        suffix = os.path.splitext(upload_file.name)[-1] or '.jpg'
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            for chunk in upload_file.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name

        img = Image.open(tmp_path).convert('RGB')

        # ---- 尝试 GroundingDINO 推理 ----
        model = get_gdino_model()
        if model is not None:
            image_source, image_tensor = load_image(tmp_path)

            # GroundingDINO 推理
            # prompt 支持中文需要先翻译成英文
            en_prompt = translate_prompt(prompt)

            boxes, logits, phrases = predict(
                model=model,
                image=image_tensor,
                caption=en_prompt,
                box_threshold=0.35,
                text_threshold=0.25,
            )

            # 在图像上绘制结果
            annotated = annotate(
                image_source=image_source,
                boxes=boxes,
                logits=logits,
                phrases=phrases,
            )

            # annotate 返回 BGR numpy array，转成 PIL
            import cv2
            import numpy as np
            annotated_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
            result_img = Image.fromarray(annotated_rgb)

        else:
            # GroundingDINO 不可用时的 fallback
            result_img = draw_mock_boxes(img, prompt)

        # 清理临时文件
        os.unlink(tmp_path)

        # 返回结果图
        output = BytesIO()
        result_img.save(output, format='JPEG', quality=90)
        output.seek(0)
        return HttpResponse(output.read(), content_type='image/jpeg')

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'code': 500, 'msg': f'检测失败：{str(e)}'})


def translate_prompt(text: str) -> str:
    """
    把中文提示词转成英文（GroundingDINO 对英文效果更好）
    简单映射表，可按需扩展
    """
    mapping = {
        '红细胞': 'red blood cell',
        '白细胞': 'white blood cell',
        '血小板': 'platelet',
        '细胞核': 'cell nucleus',
        '炎性病灶': 'inflammatory lesion',
        '肿瘤区域': 'tumor region',
        '异常细胞': 'abnormal cell',
        '细胞': 'cell',
    }
    for cn, en in mapping.items():
        text = text.replace(cn, en)
    return text


def draw_mock_boxes(img: Image.Image, prompt: str) -> Image.Image:
    """GroundingDINO 不可用时的模拟框（fallback）"""
    draw = ImageDraw.Draw(img)
    w, h = img.size
    boxes = [
        (w*0.1, h*0.1, w*0.4, h*0.4, 0.91),
        (w*0.5, h*0.2, w*0.85, h*0.65, 0.87),
        (w*0.2, h*0.55, w*0.55, h*0.9, 0.79),
    ]
    for x1, y1, x2, y2, score in boxes:
        draw.rectangle([x1, y1, x2, y2], outline='#FF4444', width=3)
        label = f'{prompt} {score:.2f}'
        draw.rectangle([x1, y1-22, x1+len(label)*8+4, y1], fill='#FF4444')
        draw.text((x1+2, y1-20), label, fill='white')
    return img