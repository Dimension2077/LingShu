from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from openai import OpenAI
from PIL import Image
from io import BytesIO
import base64
import json
import re
import traceback

client = OpenAI(
    api_key=settings.DEEPSEEK_API_KEY,
    base_url=settings.BASE_URL,
)

SKIN_DISEASES = [
    '湿疹', '银屑病（牛皮癣）', '荨麻疹', '黑色素瘤', '基底细胞癌',
    '脂溢性皮炎', '痤疮', '白癜风', '体癣', '接触性皮炎', '正常皮肤'
]


def index(request):
    return render(request, 'app01/skin.html', {'diseases': SKIN_DISEASES})


def classify(request):
    if request.method != 'POST':
        return JsonResponse({'code': 405, 'msg': 'Method not allowed'})

    upload_file = request.FILES.get('image')
    if not upload_file:
        return JsonResponse({'code': 400, 'msg': '请上传皮肤图像'})

    try:
        img_bytes = upload_file.read()
        img = Image.open(BytesIO(img_bytes)).convert('RGB')

        # 压缩图片，避免超出 token 限制
        output = BytesIO()
        img.thumbnail((800, 800))
        img.save(output, format='JPEG', quality=85)
        img_b64 = base64.b64encode(output.getvalue()).decode('utf-8')

        disease_list = '、'.join(SKIN_DISEASES)
        prompt = f"""你是一名皮肤科AI辅助诊断系统。请仔细分析这张皮肤图像，从以下类别中判断最可能的皮肤状况：
{disease_list}

请严格按照以下JSON格式返回结果，不要包含任何其他文字或markdown代码块：
{{
  "diagnosis": "诊断类别名称（必须是上面列表中的一个）",
  "confidence": 置信度百分比数字(0-100之间的整数),
  "description": "该皮肤状况的简要描述（50字以内）",
  "symptoms": ["典型症状1", "典型症状2", "典型症状3"],
  "suggestion": "就医建议（50字以内）",
  "urgency": "紧急程度（只能是：立即就医、尽快就医、定期观察、无需就医 之一）"
}}"""

        response = client.chat.completions.create(
            model='qwen-vl-plus',
            messages=[{
                'role': 'user',
                'content': [
                    {
                        'type': 'image_url',
                        'image_url': {'url': f'data:image/jpeg;base64,{img_b64}'}
                    },
                    {'type': 'text', 'text': prompt}
                ]
            }],
            max_tokens=600,
        )

        raw = response.choices[0].message.content.strip()
        raw = re.sub(r'```json|```', '', raw).strip()
        result = json.loads(raw)

        # 确保必要字段存在
        result.setdefault('diagnosis', '无法识别')
        result.setdefault('confidence', 0)
        result.setdefault('description', '图像分析失败，请上传更清晰的图像。')
        result.setdefault('symptoms', [])
        result.setdefault('suggestion', '请前往皮肤科就诊，由专业医生诊断。')
        result.setdefault('urgency', '定期观察')

        return JsonResponse({'code': 200, 'result': result})

    except json.JSONDecodeError:
        return JsonResponse({'code': 200, 'result': {
            'diagnosis': '图像质量不足',
            'confidence': 0,
            'description': '无法从图像中识别皮肤特征，请上传清晰的皮肤患处照片。',
            'symptoms': [],
            'suggestion': '请在自然光下拍摄清晰照片，或直接前往皮肤科就诊。',
            'urgency': '定期观察'
        }})
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'code': 500, 'msg': str(e)})
