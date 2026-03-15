import sys
import os
import json
import tempfile
import base64
from pathlib import Path
from io import BytesIO

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from PIL import Image

# 注册 GroundingDINO 路径
_GDINO_REPO = Path(__file__).resolve().parent.parent.parent / 'GroundingDINO'
sys.path.insert(0, str(_GDINO_REPO))

# 修正配置文件里的 bert 本地路径
def _patch_bert_path(config_path: str):
    import re
    project_root = Path(__file__).resolve().parent.parent.parent
    local_bert = str(project_root / 'app01' / 'groundingdino' / 'bert-base-uncased').replace('\\', '/')
    config_file = Path(config_path)
    if not config_file.exists():
        return
    content = config_file.read_text(encoding='utf-8')
    if local_bert in content:
        return
    new_content = re.sub(
        r'text_encoder_type\s*=\s*r?"[^"]+"',
        f'text_encoder_type = "{local_bert}"',
        content
    )
    config_file.write_text(new_content, encoding='utf-8')

try:
    from groundingdino.util.inference import load_model, load_image, predict, annotate
    import cv2
    import numpy as np
    GDINO_AVAILABLE = True
except ImportError:
    GDINO_AVAILABLE = False

BASE_DIR = settings.BASE_DIR
WEIGHTS_PATH = str(BASE_DIR / 'app01' / 'groundingdino' / 'weights' / 'groundingdino_swint_ogc.pth')
CONFIG_PATH  = str(BASE_DIR / 'app01' / 'groundingdino' / 'weights' / 'GroundingDINO_SwinT_OGC.py')

# 白肺检测专用提示词
LUNG_PROMPT = "white lung opacity . pulmonary consolidation . pneumonia . pleural effusion . ground glass opacity"

_model = None


def get_model():
    global _model
    if _model is None and GDINO_AVAILABLE:
        try:
            _patch_bert_path(CONFIG_PATH)
            _model = load_model(CONFIG_PATH, WEIGHTS_PATH)
            print("✅ 白肺检测模型加载成功")
        except Exception as e:
            print(f"❌ 白肺检测模型加载失败: {e}")
    return _model


def index(request):
    return render(request, 'app01/white_lung.html')


def detect(request):
    if request.method != 'POST':
        return JsonResponse({'code': 405, 'msg': 'Method not allowed'})

    upload_file = request.FILES.get('image')
    if not upload_file:
        return JsonResponse({'code': 400, 'msg': '请上传CT影像文件'})

    suffix = os.path.splitext(upload_file.name)[-1] or '.jpg'
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        for chunk in upload_file.chunks():
            tmp.write(chunk)
        tmp_path = tmp.name

    try:
        img = Image.open(tmp_path).convert('RGB')
        model = get_model()
        findings = []

        if model is not None:
            image_source, image_tensor = load_image(tmp_path)
            boxes, logits, phrases = predict(
                model=model,
                image=image_tensor,
                caption=LUNG_PROMPT,
                box_threshold=0.28,
                text_threshold=0.22,
            )
            if len(boxes) > 0:
                annotated = annotate(
                    image_source=image_source,
                    boxes=boxes,
                    logits=logits,
                    phrases=phrases,
                )
                annotated_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
                result_img = Image.fromarray(annotated_rgb)
            else:
                result_img = img

            for phrase, score in zip(phrases, logits.tolist()):
                score_pct = round(score * 100, 1)
                findings.append({
                    'label': phrase,
                    'confidence': score_pct,
                    'risk': '高风险' if score > 0.5 else ('中风险' if score > 0.35 else '低风险')
                })
        else:
            # GroundingDINO 不可用时返回原图
            result_img = img

        os.unlink(tmp_path)

        output = BytesIO()
        result_img.save(output, format='JPEG', quality=90)
        img_b64 = base64.b64encode(output.getvalue()).decode('utf-8')
        return JsonResponse({
            'code': 200,
            'image': f'data:image/jpeg;base64,{img_b64}',
            'findings': findings,
        })


        response = HttpResponse(output.read(), content_type='image/jpeg')
        response['X-Findings'] = json.dumps(findings, ensure_ascii=False)
        response['Access-Control-Expose-Headers'] = 'X-Findings'
        return response

    except Exception as e:
        import traceback
        traceback.print_exc()
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        return JsonResponse({'code': 500, 'msg': str(e)})
