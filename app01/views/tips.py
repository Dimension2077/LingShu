from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from openai import OpenAI
import json
import requests
# Qwen 客户端
client = OpenAI(
    api_key=settings.DEEPSEEK_API_KEY,
    base_url=settings.BASE_URL,
)

def _ask_qwen(prompt: str, max_tokens: int = 800) -> str:
    """调用 Qwen 生成内容，返回纯文本"""
    resp = client.chat.completions.create(
        model='qwen-plus',
        messages=[{'role': 'user', 'content': prompt}],
        max_tokens=max_tokens,
    )
    return resp.choices[0].message.content.strip()


def _ask_qwen_json(prompt: str, max_tokens: int = 1000) -> list:
    """调用 Qwen 生成 JSON 列表内容"""
    resp = client.chat.completions.create(
        model='qwen-plus',
        messages=[
            {
                'role': 'system',
                'content': '你是一个专业的健康科普助手。只返回 JSON 数组，不要返回任何其他文字、解释或 markdown 代码块。'
            },
            {'role': 'user', 'content': prompt}
        ],
        max_tokens=max_tokens,
    )
    raw = resp.choices[0].message.content.strip()
    # 去掉可能的 markdown 代码块
    raw = raw.replace('```json', '').replace('```', '').strip()
    return json.loads(raw)


# ===== 页面视图 =====

def health(request):
    return render(request, 'app01/health.html')


def medical(request):
    return render(request, 'app01/medical.html')


def protect(request):
    return render(request, 'app01/protect.html')


# ===== 数据接口 =====

def get_tips(request):
    """健康小贴士 —— 根据天气生成针对性内容"""
    # 接收前端传来的天气参数
    weather = request.GET.get('weather', '')
    temperature = request.GET.get('temperature', '')
    area = request.GET.get('area', '')

    if weather and temperature:
        prompt = (
            f'当前{area}天气{weather}，温度{temperature}°C。'
            f'请生成6条结合当前天气的健康小贴士，'
            f'每条包含 title（标题10字以内）和 content（内容50字以内）。'
            f'以 JSON 数组返回：[{{"title":"...","content":"..."}}]'
        )
    else:
        prompt = (
            '请生成6条实用的日常健康小贴士，'
            '每条包含 title（标题10字以内）和 content（内容50字以内）。'
            '以 JSON 数组返回：[{"title":"...","content":"..."}]'
        )

    try:
        tips = _ask_qwen_json(prompt)
        return JsonResponse({'code': 200, 'msg': 'success', 'result': tips})
    except Exception as e:
        return JsonResponse({'code': 200, 'msg': 'success', 'result': MOCK_TIPS})


def get_medical(request):
    """药品科普查询 —— Qwen 生成"""
    if request.method != 'POST':
        return JsonResponse({'code': 405, 'msg': 'Method not allowed'})

    name = request.POST.get('name', '').strip()
    if not name:
        return JsonResponse({'code': 400, 'msg': '请输入药品名称'})

    try:
        result = _ask_qwen_json(
            f'请介绍药品"{name}"的详细信息，以 JSON 数组返回，包含一个对象，字段为：'
            'name（药品名）、gongneng（功能主治）、yongfa（用法用量）、'
            'buliangfanying（不良反应）、zhuyi（注意事项）。'
            '每个字段内容控制在100字以内。'
        )
        return JsonResponse({'code': 200, 'msg': 'success', 'result': result})
    except Exception as e:
        return JsonResponse({
            'code': 200, 'msg': 'success',
            'result': [{
                'name': name,
                'gongneng': f'{name}用于治疗相关疾病，具体请咨询医生。',
                'yongfa': '请遵医嘱服用，不可自行调整剂量。',
                'buliangfanying': '可能出现轻微不适，如有异常请立即停药就医。',
                'zhuyi': '请在医生指导下使用，孕妇及儿童需特别注意。',
            }]
        })


def get_air(request):
    """实时天气数据 —— 只返回高德数据，不调用 Qwen"""
    area = request.GET.get('area', '北京').strip()
    amap_key = getattr(settings, 'AMAP_API_KEY', '')

    try:
        # 城市名转 adcode
        geo_resp = requests.get(
            'https://restapi.amap.com/v3/geocode/geo',
            params={'address': area, 'key': amap_key},
            timeout=8
        ).json()

        if geo_resp.get('status') != '1' or not geo_resp.get('geocodes'):
            raise ValueError(f'城市"{area}"未找到')

        adcode = geo_resp['geocodes'][0]['adcode']

        # 查询实况天气
        weather_resp = requests.get(
            'https://restapi.amap.com/v3/weather/weatherInfo',
            params={'city': adcode, 'key': amap_key, 'extensions': 'base'},
            timeout=8
        ).json()

        if weather_resp.get('status') != '1' or not weather_resp.get('lives'):
            raise ValueError('天气数据获取失败')

        live = weather_resp['lives'][0]

        return JsonResponse({
            'code': 200,
            'msg': 'success',
            'result': [{
                'area': live.get('city', area),
                'weather': live.get('weather', '--'),
                'temperature': live.get('temperature', '--'),
                'humidity': live.get('humidity', '--'),
                'winddirection': live.get('winddirection', '--'),
                'windpower': live.get('windpower', '--'),
                'reporttime': live.get('reporttime', '--'),
            }]
        })

    except Exception as e:
        print(f"天气查询失败: {e}")
        return JsonResponse({'code': 500, 'msg': str(e), 'result': []})


def get_weather_suggest(request):
    """AI 健康建议 —— 单独接口，根据天气异步生成"""
    area = request.GET.get('area', '北京').strip()
    weather = request.GET.get('weather', '')
    temperature = request.GET.get('temperature', '')
    humidity = request.GET.get('humidity', '')
    winddirection = request.GET.get('winddirection', '')
    windpower = request.GET.get('windpower', '')

    try:
        suggest = _ask_qwen(
            f'当前{area}天气：{weather}，温度{temperature}°C，'
            f'湿度{humidity}%，{winddirection}风{windpower}级。'
            f'请给出一条今日健康出行建议，50字以内，直接给建议不要任何前缀。'
        )
        return JsonResponse({'code': 200, 'suggest': suggest})
    except Exception as e:
        return JsonResponse({'code': 500, 'suggest': '请注意天气变化，适时增减衣物，保持健康生活习惯。'})

def get_coup(request):
    """健康小妙招关键字查询 —— Qwen 生成"""
    keyword = request.POST.get('keyword', '').strip()
    topic = keyword if keyword else '日常健康'

    try:
        skills = _ask_qwen_json(
            f'请生成6条关于"{topic}"的健康小妙招，每条包含 title（标题，15字以内）和 content（内容，80字以内）。'
            f'以 JSON 数组格式返回：[{{"title":"...","content":"..."}}]'
        )
        return JsonResponse({'code': 200, 'msg': 'success', 'result': skills})
    except Exception as e:
        return JsonResponse({'code': 200, 'msg': 'success', 'result': MOCK_SKILLS})


# ===== Fallback Mock 数据 =====

MOCK_TIPS = [
    {'title': '每天喝够8杯水', 'content': '保持充足的水分摄入，有助于促进新陈代谢，保持皮肤水润健康。'},
    {'title': '规律作息，早睡早起', 'content': '保持规律的作息时间，成年人每天需要7-9小时的高质量睡眠。'},
    {'title': '适量运动，强健体魄', 'content': '每周至少150分钟中等强度有氧运动，如快走、游泳、骑自行车。'},
    {'title': '均衡饮食，五谷为养', 'content': '遵循膳食宝塔原则，多吃蔬菜水果，减少高脂高糖食物摄入。'},
    {'title': '定期体检，防患未然', 'content': '成年人每年进行一次全面体检，及时发现潜在健康问题。'},
]

MOCK_SKILLS = [
    {'title': '失眠调理小妙招', 'content': '睡前一小时远离手机，尝试腹式深呼吸，可用薰衣草精油助眠。'},
    {'title': '颈椎保健操', 'content': '每工作1小时起身活动，做"米字操"，顺逆时针转头各10次。'},
    {'title': '快速缓解头痛', 'content': '用大拇指按压合谷穴（虎口处）1-2分钟，或用凉毛巾敷额头。'},
]