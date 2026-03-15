# 灵枢智医 · LingShu AI

> 基于人工智能的智慧医疗综合可视化平台

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Django](https://img.shields.io/badge/Django-4.2-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-lightgrey)

---

## 项目简介

**灵枢智医（LingShu AI）** 是一个面向医疗影像分析与健康管理的综合智慧医疗平台，结合目标检测、图像分类、自然语言处理、时序预测等前沿 AI 技术，为医生和患者提供直观的数据可视化与辅助诊断支持。

本项目为计算机设计大赛参赛作品，采用 Django 全栈框架开发，前端使用 ECharts 5 进行数据可视化，AI 能力由阿里云通义千问（Qwen）大模型与 GroundingDINO 零样本检测模型支撑。

---

## 功能模块

### 🤖 AI 诊断
| 功能 | 说明 | 技术 |
|------|------|------|
| AI 智能问诊 | 基于症状描述进行多轮对话式问诊，给出可能病因、检查建议 | LangChain + Qwen |
| 智能报告生成 | 根据问诊对话自动生成结构化医学问诊报告，支持打印 | Qwen-Plus |
| 皮肤病 AI 分类 | 上传皮肤图像，识别11类常见皮肤病，给出就医建议 | Qwen-VL |

### 🔬 影像检测
| 功能 | 说明 | 技术 |
|------|------|------|
| 血细胞目标检测 | 上传血细胞显微图，检测并标注 RBC/WBC/Platelets | YOLOv5 |
| Agent 零样本检测 | 输入自然语言提示词，对任意医学图像进行零样本目标检测 | GroundingDINO |
| 白肺 CT 检测 | 上传胸部CT影像，检测肺部病变区域（白肺/肺炎/胸腔积液） | GroundingDINO |
| 血细胞分类分析 | 上传血细胞图像，基于 MedMamba 模型进行细胞类型分类 | MedMamba |

### 📊 数据大屏
| 功能 | 说明 | 技术 |
|------|------|------|
| 疾病大数据可视化 | 多维度疾病统计数据展示，含地图、柱状图、饼图等 | ECharts 5 |
| 疾病趋势预测 | 基于历史数据预测未来90天疾病发展趋势，含置信区间 | Prophet + ECharts |

### 💚 健康教育
| 功能 | 说明 | 技术 |
|------|------|------|
| 健康小贴士 | 实时生成结合当前天气的健康建议 | Qwen + 高德天气API |
| 药品科普 | 输入药品名称，AI 生成功效、用法、注意事项 | Qwen |
| 健康小妙招 | 按关键词搜索生活健康小技巧 | Qwen |

---

## 技术栈

### 后端
- **框架**：Django 4.2
- **AI 推理**：LangChain + OpenAI SDK（兼容阿里云百炼）
- **目标检测**：YOLOv5、GroundingDINO
- **时序预测**：Prophet
- **图像处理**：Pillow、OpenCV

### 前端
- **UI 框架**：Bootstrap 5
- **数据可视化**：ECharts 5
- **字体**：Noto Serif SC / Noto Sans SC
- **图标**：Font Awesome 6

### AI 服务
- **语言模型**：阿里云通义千问 `qwen-plus`
- **视觉模型**：阿里云通义千问 `qwen-vl-plus`
- **目标检测**：GroundingDINO（本地部署）
- **天气数据**：高德地图 Web API

---

## 目录结构

```
LingShu-AI/
├── LingShu-AI/                     # Django 项目配置
│   ├── settings.py                 # 全局配置（API Key 等）
│   ├── urls.py                     # 全局路由
│   └── wsgi.py
├── app01/                          # 核心应用
│   ├── views/                      # 视图层
│   │   ├── index.py                # 首页
│   │   ├── agent.py                # AI 问诊 + 报告生成
│   │   ├── mask.py                 # YOLOv5 血细胞检测
│   │   ├── cell.py                 # Agent 零样本检测
│   │   ├── white_lung.py           # 白肺 CT 检测
│   │   ├── skin.py                 # 皮肤病分类
│   │   ├── lung.py                 # MedMamba 血细胞分类
│   │   ├── screen.py               # 疾病大屏 + 趋势预测
│   │   └── tips.py                 # 健康教育模块
│   ├── templates/app01/            # HTML 模板
│   ├── static/app01/css/
│   │   └── base.css                # 全局样式（深青医典风格）
│   ├── groundingdino/
│   │   └── weights/                # ⚠️ 需手动下载，见下方说明
│   │       ├── groundingdino_swint_ogc.pth
│   │       └── GroundingDINO_SwinT_OGC.py
│   └── yolo/
│       └── weights/                # ⚠️ 需手动下载，见下方说明
│           └── best.pt
├── GroundingDINO/                  # ⚠️ 需手动克隆，见下方说明
├── manage.py
├── requirements.txt
└── README.md
```

---

## 快速开始

### 环境要求

- Python 3.10+
- CUDA 11.8+（推荐，CPU 模式也可运行但速度较慢）
- Windows 10/11 或 Linux
- conda 环境管理（推荐）

> ⚠️ **重要**：项目路径和 GroundingDINO 安装目录均不能含有中文字符，否则会因编码错误导致安装失败。

### 1. 克隆项目

```bash
git clone https://github.com/Dimension2077/LingShu.git
cd LingShu-AI
```

### 2. 创建虚拟环境

```bash
conda create -n lingshu python=3.10
conda activate lingshu
```

### 3. 安装依赖

```bash
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

### 4. 克隆并安装 GroundingDINO

> ⚠️ 必须克隆到项目根目录，目录名保持 `GroundingDINO`

```bash
git clone https://github.com/IDEA-Research/GroundingDINO.git
cd GroundingDINO
pip install -e . -i https://mirrors.aliyun.com/pypi/simple/
cd ..
```

### 5. 下载模型权重

#### GroundingDINO 权重（约 700MB）

下载以下两个文件，放到 `app01/groundingdino/weights/` 目录：

```bash
# 方式一：直接下载（需要网络）
# groundingdino_swint_ogc.pth
https://github.com/IDEA-Research/GroundingDINO/releases/download/v0.1.0-alpha/groundingdino_swint_ogc.pth

# GroundingDINO_SwinT_OGC.py（配置文件）
https://raw.githubusercontent.com/IDEA-Research/GroundingDINO/main/groundingdino/config/GroundingDINO_SwinT_OGC.py
```

```bash
# 方式二：通过 Python 脚本下载
python -c "
import urllib.request, os
os.makedirs('app01/groundingdino/weights', exist_ok=True)
print('下载权重文件...')
urllib.request.urlretrieve(
    'https://github.com/IDEA-Research/GroundingDINO/releases/download/v0.1.0-alpha/groundingdino_swint_ogc.pth',
    'app01/groundingdino/weights/groundingdino_swint_ogc.pth'
)
print('下载配置文件...')
urllib.request.urlretrieve(
    'https://raw.githubusercontent.com/IDEA-Research/GroundingDINO/main/groundingdino/config/GroundingDINO_SwinT_OGC.py',
    'app01/groundingdino/weights/GroundingDINO_SwinT_OGC.py'
)
print('完成！')
"
```

#### YOLOv5 血细胞检测权重

将训练好的 `best.pt` 放到 `app01/yolo/weights/best.pt`。

如果没有训练好的权重，可使用 YOLOv5 官方预训练权重进行功能演示：

```bash
python -c "
import urllib.request, os
os.makedirs('app01/yolo/weights', exist_ok=True)
urllib.request.urlretrieve(
    'https://github.com/ultralytics/yolov5/releases/download/v7.0/yolov5s.pt',
    'app01/yolo/weights/best.pt'
)
print('YOLOv5 权重下载完成')
"
```

### 6. 配置 API Key

编辑 `LingShu-AI/settings.py`，填写以下配置：

```python
# 阿里云百炼 API（通义千问）
# 获取地址：https://bailian.console.aliyun.com/
DEEPSEEK_API_KEY = 'your-aliyun-api-key'
BASE_URL = 'https://dashscope.aliyuncs.com/compatible-mode/v1'

# 高德地图 API（天气查询）
# 获取地址：https://lbs.amap.com/ → 控制台 → 创建应用（选 Web 服务）
AMAP_API_KEY = 'your-amap-api-key'
```

### 7. 数据库初始化

```bash
python manage.py migrate
```

### 8. 启动服务

```bash
python manage.py runserver
```

访问 http://127.0.0.1:8000 即可使用。

---

## 页面路由

| 路由 | 功能 |
|------|------|
| `/` | 首页（自动跳转） |
| `/index/` | 平台首页 |
| `/agent/` | AI 智能问诊 |
| `/agent/report/` | 医学报告生成（POST接口） |
| `/mask/` | YOLOv5 血细胞检测 |
| `/cell/` | Agent 零样本检测 |
| `/white_lung/` | 白肺 CT 检测 |
| `/skin/` | 皮肤病 AI 分类 |
| `/lung/` | MedMamba 血细胞分类 |
| `/screen/` | 疾病大数据大屏 |
| `/screen/trend/` | 疾病趋势预测（API） |
| `/health/` | 健康小贴士 |
| `/medical/` | 药品科普 |
| `/protect/` | 健康小妙招 |

---

## 注意事项

1. **中文路径问题**：GroundingDINO 安装目录及项目路径不能含有中文字符，否则 pip 安装会因编码错误失败。

2. **首次运行较慢**：GroundingDINO 模型在第一次请求时加载（约10~30秒），加载完成后后续请求速度正常。

3. **CPU 模式**：若未编译 CUDA 自定义算子，模型将运行在 CPU 模式下，推理速度较慢（约 10~30 秒/张），可通过编译加速：
   ```bash
   cd GroundingDINO
   pip install ninja
   python setup.py build_ext --inplace
   ```

4. **transformers 版本**：GroundingDINO 依赖 `transformers==4.48.0`，请勿升级到 5.x，否则会出现 `BertModel` 兼容性报错。

5. **API 免责声明**：本平台所有 AI 诊断结果仅供参考，不能替代专业医生诊断，请以医院诊断为准。

6. **趋势预测数据**：当前疾病趋势预测使用基于真实流行病学规律的模拟数据，如需接入真实数据，请参考国家卫健委法定传染病疫情月报（https://www.nhc.gov.cn/jkj/s3578/new_list.shtml）。

---

## 团队分工

| 角色 | 负责内容 |
|------|---------|
| 项目负责人 | 项目整体规划、进度把控、需求分析、团队协调 |
| 框架搭建 | Django 后端架构、AI 模型集成、API 接口设计、前端开发 |
| 数据采集 | 医疗数据集收集与预处理、模型训练数据构建、数据可视化 |

---

## 免责声明

本平台所有功能（AI 问诊、影像检测、皮肤病分类、白肺检测等）均为 **AI 辅助工具**，输出结果仅供参考，**不能替代专业医生的临床诊断**。如有健康问题，请及时前往正规医疗机构就诊。

---

## License

MIT License © 2026 灵枢智医 · LingShu Team
