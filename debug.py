# 项目根目录运行: python debug_gdino.py
import sys
sys.path.insert(0, 'app01')

print("=== 第一步：检查 Pillow ===")
try:
    from PIL import Image
    print("✅ Pillow OK")
except ImportError as e:
    print(f"❌ Pillow 缺失: {e}")

print("\n=== 第二步：检查 GroundingDINO 安装 ===")
try:
    from groundingdino.util.inference import load_model, load_image, predict, annotate
    print("✅ GroundingDINO 导入 OK")
except ImportError as e:
    print(f"❌ GroundingDINO 导入失败: {e}")

print("\n=== 第三步：检查权重文件 ===")
from pathlib import Path
weights = Path('app01/groundingdino/weights/groundingdino_swint_ogc.pth')
config  = Path('app01/groundingdino/weights/GroundingDINO_SwinT_OGC.py')
print(f"{'✅' if weights.exists() else '❌'} 权重文件: {weights} {'存在' if weights.exists() else '不存在'}")
print(f"{'✅' if config.exists() else '❌'} 配置文件: {config}  {'存在' if config.exists() else '不存在'}")

print("\n=== 第四步：检查 torch ===")
try:
    import torch
    print(f"✅ PyTorch {torch.__version__}")
    print(f"   GPU可用: {torch.cuda.is_available()}")
except ImportError as e:
    print(f"❌ PyTorch 缺失: {e}")

print("\n=== 第五步：尝试加载模型 ===")
try:
    from groundingdino.util.inference import load_model
    model = load_model(str(config), str(weights))
    print("✅ 模型加载成功")
except Exception as e:
    print(f"❌ 模型加载失败: {e}")