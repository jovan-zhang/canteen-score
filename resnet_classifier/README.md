# AI菜品识别模块

## 简介

这是一个独立的AI菜品识别模块，基于ResNet-50深度学习模型，可以识别100种不同的菜品类别。该模块完全独立于主系统，可以单独使用。

## 特点

- 🤖 **高精度识别**: 基于ResNet-50深度学习模型
- ⚡ **快速响应**: 通常在2秒内完成识别
- 🔓 **无需认证**: 独立模块，无需用户登录
- 📦 **即插即用**: 可以独立部署和使用
- 🎯 **多类别支持**: 支持100种菜品分类

## 文件结构

```
resnet_classifier/
├── model.pth           # 训练好的ResNet-50模型文件
├── id_name_mapping.txt # 类别ID到菜品名称的映射文件
└── resnet_predict.py   # 预测逻辑的核心代码
```

## 安装依赖

```bash
pip install torch torchvision pillow
```

## 使用方法

### 1. 作为Python模块使用

```python
from resnet_predict import predict_image

# 预测单张图片
result = predict_image("path/to/your/image.jpg")

if 'error' in result:
    print(f"识别失败: {result['error']}")
else:
    print(f"识别结果: {result['name']}")
    print(f"置信度: {result['confidence']:.2%}")
```

### 2. 通过API接口使用

```bash
# 上传图片进行识别
curl -X POST http://localhost:5000/api/classify-dish \
     -F "image=@your_dish_image.jpg"
```

### 3. 命令行测试

```bash
# 运行内置测试
python resnet_predict.py

# 使用专门的测试脚本
python ../test_ai_classification.py
```

## API响应格式

### 成功响应
```json
{
  "code": 200,
  "message": "识别成功",
  "data": {
    "dish_name": "fried rice",
    "confidence": 89.25
  }
}
```

### 错误响应
```json
{
  "code": 500,
  "message": "AI识别失败: 图片文件不存在"
}
```

## 支持的菜品类别

本模型支持识别以下100种菜品（部分示例）：

### 主食类
- rice (米饭)
- fried rice (炒饭)
- pilaf (抓饭)
- bibimbap (石锅拌饭)
- eels on rice (鳗鱼饭)
- chicken-'n'-egg on rice (亲子丼)
- pork cutlet on rice (猪排饭)
- tempura bowl (天妇罗丼)

### 面包类
- toast (吐司)
- croissant (羊角面包)
- roll bread (餐包)
- raisin bread (葡萄干面包)
- sandwiches (三明治)

### 快餐类
- hamburger (汉堡包)
- pizza (披萨)
- chip butty (薯条三明治)

### 其他
- sushi (寿司)
- beef curry (牛肉咖喱)

*完整的类别列表请查看 `id_name_mapping.txt` 文件*

## 使用建议

### 图片要求
- **格式**: PNG, JPG, JPEG, GIF
- **尺寸**: 建议224x224像素或更大
- **质量**: 清晰度越高，识别准确率越高
- **光线**: 充足的光线条件

### 拍摄技巧
- 从正上方或45度角拍摄菜品
- 确保菜品占据画面主要部分
- 避免复杂背景干扰
- 保证充足光线，避免阴影

### 置信度解读
- **> 80%**: 识别结果非常可信
- **60-80%**: 识别结果较为可信
- **< 60%**: 建议重新拍摄更清晰的图片

## 技术详情

### 模型架构
- **基础模型**: ResNet-50
- **输入尺寸**: 224 x 224 RGB
- **输出类别**: 100种菜品
- **模型大小**: ~100MB

### 预处理流程
1. 图片加载和RGB转换
2. 尺寸调整到224x224
3. 张量转换和标准化
4. 模型推理
5. Softmax概率计算
6. 返回最高概率的类别

### 性能指标
- **识别速度**: < 2秒 (CPU)
- **模型精度**: 基于训练数据集的准确率
- **内存占用**: ~500MB (模型加载后)

## 故障排除

### 常见问题

1. **ModuleNotFoundError: No module named 'torch'**
   ```bash
   pip install torch torchvision
   ```

2. **FileNotFoundError: model.pth not found**
   - 确保模型文件存在于正确路径
   - 检查文件权限

3. **CUDA相关错误**
   - 模型会自动检测并使用CPU
   - 如需GPU加速，安装CUDA版本的PyTorch

4. **图片格式不支持**
   - 使用PIL支持的格式: PNG, JPG, JPEG, GIF
   - 确保图片文件没有损坏

### 调试模式

在 `resnet_predict.py` 中启用调试信息：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 扩展开发

### 添加新的菜品类别
1. 更新训练数据集
2. 重新训练模型
3. 更新 `id_name_mapping.txt` 文件
4. 替换 `model.pth` 文件

### 模型优化
- 使用量化技术减小模型大小
- 使用TensorRT等推理引擎加速
- 实现批量处理支持

### 部署优化
- 使用模型服务框架（如TorchServe）
- 实现模型缓存机制
- 添加负载均衡支持

## 许可证

本模块使用与主项目相同的许可证。

## 贡献

欢迎提交Issue和Pull Request来改进这个模块。
