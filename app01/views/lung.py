from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
import os
import random
import shutil

BASE_DIR = settings.BASE_DIR
LUNG_DIR = BASE_DIR / 'app01' / 'lung'
INPUT_PATH = LUNG_DIR / 'data' / 'images' / 'input.png'

CATEGORIES = {
    0: {'name': '正常', 'tips': '检测为正常，细胞形态未见明显异常', 'color': '#52c41a'},
    1: {'name': '锯齿状', 'tips': '检测到锯齿状细胞，建议进一步检查是否存在遗传性球形红细胞症等', 'color': '#faad14'},
    2: {'name': '腺癌', 'tips': '检测为腺癌细胞，请立即前往医院进行专业诊断和治疗', 'color': '#f5222d'},
    3: {'name': '腺瘤', 'tips': '检测到腺瘤特征，建议尽快就医进行确诊', 'color': '#fa8c16'},
}


def lungkonw(request):
    """MedMamba 原理/科普页面"""
    return render(request, 'app01/lungKonw.html')


def lung_index(request):
    """血细胞图像分类主界面"""
    return render(request, 'app01/lung_index.html')


def lung_upload(request):
    """接收上传的血细胞图像"""
    if request.method != 'POST':
        return JsonResponse({'status': False, 'msg': 'Method not allowed'})

    try:
        upload_file = request.FILES.get('uploadImage')
        if not upload_file:
            return JsonResponse({'status': False, 'msg': '未接收到图像文件'})

        os.makedirs(INPUT_PATH.parent, exist_ok=True)

        with open(INPUT_PATH, 'wb') as f:
            for chunk in upload_file.chunks():
                f.write(chunk)

        return JsonResponse({'status': True})

    except Exception as e:
        return JsonResponse({'status': False, 'msg': str(e)})


def lung_detect(request):
    """
    返回血细胞分类结果
    当前为模拟结果，便于前端联调；后续可替换为真实 MedMamba 模型输出
    """
    if request.method != 'POST':
        return JsonResponse({'status': False, 'msg': 'Method not allowed'})

    try:
        # TODO: 替换为真实 MedMamba 模型推理
        # from app01.lung.model import MedMambaClassifier
        # result = MedMambaClassifier().predict(INPUT_PATH)

        # 模拟分类结果
        rate = round(random.uniform(0.75, 0.96), 4)
        kind = random.randint(0, 3)
        category = CATEGORIES[kind]

        return JsonResponse({
            'status': True,
            'name': category['name'],
            'rate': rate,
            'kind': kind,
            'tips': category['tips'],
            'color': category['color'],
        })

    except Exception as e:
        return JsonResponse({'status': False, 'msg': str(e)})
