from django.shortcuts import render
from django.http import JsonResponse
from django.core.cache import cache
from django.conf import settings
from django.db.models import Q
import json
import re
import traceback
import datetime

try:
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

try:
    from app01.models import MedicalKnowledge
    MODELS_AVAILABLE = True
except Exception:
    MODELS_AVAILABLE = False


def search_medical_knowledge(symptoms_str: str) -> list:
    if not MODELS_AVAILABLE:
        return []
    try:
        keywords = [k.strip() for k in symptoms_str.split('，') + symptoms_str.split(',') if k.strip()]
        if not keywords:
            return []
        query = Q()
        for kw in keywords:
            query |= Q(symptoms__icontains=kw) | Q(disease__icontains=kw)
        results = MedicalKnowledge.objects.filter(query).distinct()[:3]
        return list(results.values('disease', 'symptoms', 'description', 'treatment', 'prevention'))
    except Exception:
        return []


def ai_diagnosis(request):
    """
    AI 问诊
    GET:  渲染问诊页面
    POST: 处理问诊请求，返回 AI 建议
    """
    session_id = request.session.session_key
    if not session_id:
        request.session.create()
        session_id = request.session.session_key

    cache_key = f'dialogue_{session_id}'

    if request.method == 'GET':
        history = cache.get(cache_key, [])
        return render(request, 'app01/agent.html', {'history': history})

    try:
        data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
        symptoms = data.get('symptoms', '').strip()
        if not symptoms:
            return JsonResponse({'code': 400, 'msg': '请描述您的症状'})

        knowledge = search_medical_knowledge(symptoms)
        knowledge_text = ''
        if knowledge:
            knowledge_text = '\n'.join([
                f"【{k['disease']}】症状：{k['symptoms']}；建议：{k.get('treatment', '请就医')}"
                for k in knowledge
            ])
        else:
            knowledge_text = '暂无精确匹配的知识库条目，请根据通用医学知识作答。'

        history = cache.get(cache_key, [])
        history_text = '\n'.join([
            f"用户：{h['user']}\nAI：{h['ai']}"
            for h in history[-20:]
        ])

        if LANGCHAIN_AVAILABLE:
            chat_model = ChatOpenAI(
                model='qwen-plus',
                api_key=settings.DEEPSEEK_API_KEY,
                openai_api_base=settings.BASE_URL,
                max_tokens=1000,
            )
            prompt = ChatPromptTemplate.from_messages([
                ('system', (
                    '你是一位专业的 AI 全科医生助手。\n'
                    '以下是相关医疗知识库内容：\n{knowledge}\n\n'
                    '以下是历史对话记录：\n{history}\n\n'
                    '请根据上述背景，对用户的症状进行分析，给出结构化输出：\n'
                    '1. 可能病因\n2. 建议检查\n3. 健康建议\n\n'
                    '注意：必须提醒用户本分析仅供参考，请及时就医。'
                )),
                ('human', '用户症状：{symptoms}'),
            ])
            chain = prompt | chat_model
            result = chain.invoke({
                'knowledge': knowledge_text,
                'history': history_text,
                'symptoms': symptoms,
            })
            ai_answer = result.content
        else:
            ai_answer = (
                f"【可能病因】根据您描述的症状「{symptoms}」，可能与以下情况有关：\n"
                "- 呼吸道感染（如感冒、流感）\n- 消化系统疾病\n- 过敏反应\n\n"
                "【建议检查】建议进行血常规、胸部X光等基础检查，必要时做专项检查。\n\n"
                "【健康建议】注意休息，保持充足睡眠，多饮水。如症状持续或加重，"
                "请及时前往医院就诊。\n\n"
                "⚠️ 本分析仅供参考，不能替代专业医生诊断，请及时就医。"
            )

        history.append({'user': symptoms, 'ai': ai_answer})
        cache.set(cache_key, history, timeout=3600)

        return JsonResponse({
            'code': 200,
            'msg': 'success',
            'data': {
                'answer': ai_answer,
                'history': history,
                'knowledge_count': len(knowledge),
            }
        })

    except Exception as e:
        traceback.print_exc()
        return JsonResponse({
            'code': 500,
            'msg': '服务暂时不可用，请稍后重试',
            'error': str(e)
        })


def generate_report(request):
    """根据问诊对话生成结构化医学报告"""
    if request.method != 'POST':
        return JsonResponse({'code': 405, 'msg': 'Method not allowed'})

    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'code': 400, 'msg': '请求格式错误'})

    # history 格式：[{'user': '...', 'ai': '...'}, ...]  来自 cache
    history = data.get('history', [])

    if not history:
        return JsonResponse({'code': 400, 'msg': '请先进行问诊对话'})

    # 把 {'user':..., 'ai':...} 格式转成对话文本
    dialog_text = '\n'.join([
        f"患者: {h.get('user', '')}\nAI医生: {h.get('ai', '')}"
        for h in history
    ])

    now_str = datetime.datetime.now().strftime('%Y年%m月%d日 %H:%M')

    prompt = f"""你是一名专业的医学文书助手。请根据以下问诊对话，生成一份规范的医学问诊报告。

问诊对话：
{dialog_text}

请严格按以下JSON格式返回，不要包含其他文字或markdown代码块：
{{
  "report_time": "{now_str}",
  "chief_complaint": "主诉（患者主要症状，30字以内）",
  "present_illness": "现病史（症状描述、起病时间、加重缓解因素等，100字以内）",
  "preliminary_diagnosis": "初步诊断（可能的诊断，多个用顿号分隔）",
  "differential_diagnosis": "需排除疾病（鉴别诊断，多个用顿号分隔）",
  "suggestions": ["建议1", "建议2", "建议3"],
  "further_examination": ["建议检查项目1", "建议检查项目2"],
  "risk_level": "风险等级（低风险/中风险/高风险/危急）",
  "disclaimer": "本报告由AI辅助生成，仅供参考，不能替代医生诊断，请及时就诊。"
}}"""

    try:
        from openai import OpenAI
        client = OpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.BASE_URL,
        )
        resp = client.chat.completions.create(
            model='qwen-plus',
            messages=[{'role': 'user', 'content': prompt}],
            max_tokens=1000,
        )
        raw = resp.choices[0].message.content.strip()
        raw = re.sub(r'```json|```', '', raw).strip()
        report = json.loads(raw)
        return JsonResponse({'code': 200, 'report': report})

    except json.JSONDecodeError:
        return JsonResponse({'code': 500, 'msg': 'AI返回格式异常，请重试'})
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'code': 500, 'msg': str(e)})
