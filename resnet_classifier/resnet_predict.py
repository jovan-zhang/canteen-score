# resnet_predict.py
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image

# 模型路径 & 类别映射
import os
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(CURRENT_DIR, 'model.pth')
ID_NAME_PATH = os.path.join(CURRENT_DIR, 'id_name_mapping.txt')
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# 数据预处理
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# 加载类别映射
def load_id2name():
    id2name = {}
    with open(ID_NAME_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip() and not line.startswith('id'):
                parts = line.strip().split('\t')
                if len(parts) == 2:
                    id2name[int(parts[0]) - 1] = parts[1]  # ImageFolder 从 0 开始编号
    return id2name

id2name = load_id2name()

# 加载模型
def load_model():
    model = models.resnet50(pretrained=False)
    model.fc = nn.Linear(model.fc.in_features, 100)
    model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
    model.eval()
    return model.to(DEVICE)

model = load_model()

# 预测函数
def predict_image(image_path):
    """
    预测图片中的菜品
    Args:
        image_path: 图片的绝对路径或相对路径
    Returns:
        dict: {'name': 菜品名称, 'confidence': 置信度} 或 {'error': 错误信息}
    """
    try:
        # 确保图片路径存在
        if not os.path.exists(image_path):
            return {'error': f'图片文件不存在: {image_path}'}
        
        # 加载并预处理图片
        img = Image.open(image_path).convert('RGB')
        img_tensor = transform(img).unsqueeze(0).to(DEVICE)
        
        # 执行预测
        with torch.no_grad():
            outputs = model(img_tensor)
            probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
            confidence, pred = torch.max(probabilities, 0)
            pred_id = pred.item()
            pred_name = id2name.get(pred_id, "unknown")
            
            return {
                'name': pred_name, 
                'confidence': float(confidence.item())
            }
            
    except Exception as e:
        return {'error': f'预测过程中出错: {str(e)}'}


def get_available_classes():
    """
    获取所有可识别的菜品类别
    Returns:
        list: 菜品名称列表
    """
    return list(id2name.values())

if __name__ == "__main__":
    # 测试示例
    test_image = "test_image.jpg"  # 替换为实际的测试图片路径
    if os.path.exists(test_image):
        result = predict_image(test_image)
        if 'error' in result:
            print(f"识别失败: {result['error']}")
        else:
            print(f"识别结果: {result['name']}, 置信度: {result['confidence']:.2%}")
    else:
        print("请提供有效的测试图片路径")
    
    # 显示所有可识别的类别
    print(f"\n可识别的菜品类别 ({len(id2name)} 种):")
    for i, name in enumerate(id2name.values(), 1):
        print(f"{i:2d}. {name}")
