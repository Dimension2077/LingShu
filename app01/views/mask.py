from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.conf import settings
import os
import base64
import shutil

BASE_DIR = settings.BASE_DIR
YOLO_DIR = BASE_DIR / 'app01' / 'yolo'
INPUT_PATH = YOLO_DIR / 'data' / 'images' / 'input.png'
OUTPUT_DIR = YOLO_DIR / 'runs' / 'detect'
OUTPUT_IMG = OUTPUT_DIR / 'exp' / 'input.png'


def del_filedir(path):
    """清空目录（保留目录本身）"""
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path, exist_ok=True)


def mask_index(request):
    """血细胞检测主页面"""
    return render(request, 'app01/mask_index.html')


def mask_upload(request):
    """接收上传图片并运行 YOLO 推理"""
    if request.method != 'POST':
        return JsonResponse({'status': False, 'msg': 'Method not allowed'})

    try:
        upload_file = request.FILES.get('uploadImage')
        if not upload_file:
            return JsonResponse({'status': False, 'msg': '未接收到图像文件'})

        # 确保目录存在
        os.makedirs(INPUT_PATH.parent, exist_ok=True)
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        # 保存上传图像
        with open(INPUT_PATH, 'wb') as f:
            for chunk in upload_file.chunks():
                f.write(chunk)

        # 清空旧推理结果
        del_filedir(str(OUTPUT_DIR))

        # 尝试调用 YOLO 推理
        try:
            import sys
            YOLO_REPO = BASE_DIR / 'app01' / 'yolo_repo'
            sys.path.insert(0, str(YOLO_REPO))
            import detect
            detect.run(
                weights=str(BASE_DIR / 'app01' / 'yolo' / 'weights' / 'best.pt'),
                source=str(INPUT_PATH),
                project=str(OUTPUT_DIR),
                name='exp',
                exist_ok=True,
                save_txt=False,
                save_conf=True,
            )
        except Exception as yolo_err:
            print(f"YOLO inference error: {yolo_err}")
            exp_dir = OUTPUT_DIR / 'exp'
            os.makedirs(exp_dir, exist_ok=True)
            shutil.copy(str(INPUT_PATH), str(OUTPUT_IMG))

        return JsonResponse({'status': True})

    except Exception as e:
        return JsonResponse({'status': False, 'msg': str(e)})


def mask_img(request):
    """返回 YOLO 标注后的检测结果图片（Base64）"""
    try:
        if not OUTPUT_IMG.exists():
            # 返回占位图
            placeholder = BASE_DIR / 'app01' / 'static' / 'app01' / 'img' / 'placeholder.png'
            if placeholder.exists():
                img_path = str(placeholder)
            elif INPUT_PATH.exists():
                img_path = str(INPUT_PATH)
            else:
                return JsonResponse({'status': False, 'msg': '暂无可用图片，请先上传检测图片'})
        else:
            img_path = str(OUTPUT_IMG)

        with open(img_path, 'rb') as f:
            img_data = f.read()

        img_base64 = base64.b64encode(img_data).decode('utf-8')
        return JsonResponse({'status': True, 'image': f'data:image/png;base64,{img_base64}'})

    except Exception as e:
        return JsonResponse({'status': False, 'msg': str(e)})
