from django.http import JsonResponse
from django.shortcuts import render
from datetime import datetime, timedelta
import random


def index(request):
    return render(request, 'app01/screen.html')


def trend_predict(request):
    """疾病趋势预测接口 —— Prophet 时序模型"""
    disease = request.GET.get('disease', '流感')

    try:
        from prophet import Prophet
        import pandas as pd

        base = {'流感': 320, '肺炎': 180, '高血压': 450, '糖尿病': 380, '新冠': 260}
        base_val = base.get(disease, 300)

        dates, values = [], []
        rng = random.Random(hash(disease) % 10000)  # 固定随机种子，同疾病结果一致
        for i in range(365):
            d = datetime.now() - timedelta(days=365 - i)
            seasonal = 80 * (1 + 0.5 * (d.month in [1, 2, 12]))
            noise = rng.gauss(0, 20)
            val = max(0, base_val + seasonal + noise + i * 0.1)
            dates.append(d.strftime('%Y-%m-%d'))
            values.append(round(val))

        df = pd.DataFrame({'ds': pd.to_datetime(dates), 'y': values})

        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=False,
            daily_seasonality=False,
            changepoint_prior_scale=0.05,
        )
        model.fit(df)

        future = model.make_future_dataframe(periods=90)
        forecast = model.predict(future)

        history_df = df.tail(60)
        pred_df = forecast[forecast['ds'] > df['ds'].max()][
            ['ds', 'yhat', 'yhat_lower', 'yhat_upper']
        ]

        return JsonResponse({
            'code': 200,
            'disease': disease,
            'history': {
                'dates': history_df['ds'].dt.strftime('%Y-%m-%d').tolist(),
                'values': history_df['y'].tolist(),
            },
            'forecast': {
                'dates': pred_df['ds'].dt.strftime('%Y-%m-%d').tolist(),
                'values': [round(v) for v in pred_df['yhat'].tolist()],
                'lower':  [max(0, round(v)) for v in pred_df['yhat_lower'].tolist()],
                'upper':  [round(v) for v in pred_df['yhat_upper'].tolist()],
            }
        })

    except ImportError:
        return JsonResponse({'code': 500, 'msg': 'Prophet 未安装，请运行: pip install prophet'})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'code': 500, 'msg': str(e)})
