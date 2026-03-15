from django.shortcuts import render
from django.http import JsonResponse
import json


def ai_chat(request):
    """早期 AI 聊天页面"""
    return render(request, 'app01/ai_chat.html')


def ai_process(request):
    """处理聊天请求（旧版接口）"""
    if request.method != 'POST':
        return JsonResponse({'code': 405, 'msg': 'Method not allowed'})

    try:
        data = json.loads(request.body)
        user_input = data.get('message', '').strip()
        if not user_input:
            return JsonResponse({'code': 400, 'msg': '请输入内容'})

        # 简单 fallback 回复（可替换为 Spark API 等）
        reply = (
            f"您好！关于您提到的「{user_input}」，建议您保持良好的作息规律，"
            "均衡饮食，适当运动。如有持续不适，请及时就医。本回答仅供参考。"
        )
        return JsonResponse({'code': 200, 'msg': 'success', 'data': {'reply': reply}})

    except Exception as e:
        return JsonResponse({'code': 500, 'msg': str(e)})
