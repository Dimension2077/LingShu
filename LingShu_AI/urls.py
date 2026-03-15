from django.contrib import admin
from django.urls import path
from app01.views import index, agent, mask, cell, screen, lung, tips, white_lung, skin

urlpatterns = [
    path('admin/', admin.site.urls),

    # 首页
    path('', index.entrance),
    path('index/', index.index),

    # AI 问诊 + 报告生成
    path('agent/', agent.ai_diagnosis),
    path('agent/report/', agent.generate_report),

    # YOLO 血细胞检测
    path('mask/', mask.mask_index),
    path('mask/upload/', mask.mask_upload),
    path('mask/img/', mask.mask_img),

    # Agent 零样本检测
    path('cell/', cell.index),
    path('cell/detect/', cell.detect),

    # 疾病大数据大屏 + 趋势预测
    path('screen/', screen.index),
    path('screen/trend/', screen.trend_predict),

    # MedMamba 血细胞分析
    path('lungkonw/', lung.lungkonw),
    path('lung/', lung.lung_index),
    path('lung/upload/', lung.lung_upload),
    path('lung/detect/', lung.lung_detect),

    # 健康教育模块
    path('medical/', tips.medical),
    path('medical/data/', tips.get_medical),
    path('health/', tips.health),
    path('protect/', tips.protect),
    path('air/data/', tips.get_air),
    path('tips/data/', tips.get_coup),
    path('get_tips/', tips.get_tips),
    path('weather/suggest/', tips.get_weather_suggest),

    # 白肺 CT 检测
    path('white_lung/', white_lung.index),
    path('white_lung/detect/', white_lung.detect),

    # 皮肤病分类
    path('skin/', skin.index),
    path('skin/classify/', skin.classify),
]
