# AI菜品识别模块Postman测试指南

## 概述

本文档介绍如何使用Postman测试AI菜品识别功能。AI识别模块是一个独立的功能，不需要用户认证。

## 测试前准备

### 1. 导入测试集合

1. 打开Postman
2. 点击"Import"按钮
3. 选择并导入以下文件：
   - `postman_collection.json` - 测试集合
   - `postman_environment.json` - 测试环境

### 2. 选择测试环境

在Postman右上角的环境选择器中选择"校园食堂系统环境"。

### 3. 准备测试图片

准备一些菜品图片用于测试，支持的格式：
- PNG
- JPG/JPEG  
- GIF

建议图片特点：
- 清晰度高
- 菜品主体突出
- 光线充足
- 尺寸建议224x224像素或更大

## 测试步骤

### 1. 启动服务器

确保Flask服务器正在运行：
```bash
cd d:\canteen-score
python run.py
```

### 2. 执行AI识别测试

1. 在Postman集合中找到"7. AI菜品识别"文件夹
2. 选择"菜品图片识别"请求
3. 在Body标签页中，点击"image"字段的"Select Files"
4. 选择一张菜品图片
5. 点击"Send"发送请求

### 3. 检查响应结果

#### 成功响应示例：
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

#### 错误响应示例：
```json
{
  "code": 400,
  "message": "请上传图片文件"
}
```

## 自动化测试

### 测试脚本说明

Postman测试集合包含以下自动化测试：

1. **状态码检查**：验证HTTP状态码为200
2. **响应格式检查**：验证响应包含必需字段
3. **数据类型检查**：验证置信度为数字且在0-100范围内

### 执行批量测试

1. 选择"7. AI菜品识别"文件夹
2. 点击"Run"按钮
3. 在弹出的Runner窗口中点击"Run AI菜品识别"
4. 查看测试结果

## 测试用例

### 正常测试用例

| 测试场景 | 预期结果 |
|---------|---------|
| 上传清晰的米饭图片 | 返回"rice"相关识别结果 |
| 上传炒饭图片 | 返回"fried rice"相关识别结果 |
| 上传寿司图片 | 返回"sushi"相关识别结果 |
| 上传披萨图片 | 返回"pizza"相关识别结果 |

### 异常测试用例

| 测试场景 | 预期结果 |
|---------|---------|
| 不上传任何文件 | 400错误："请上传图片文件" |
| 上传非图片文件 | 400错误："不支持的文件格式" |
| 上传损坏的图片 | 500错误：AI识别过程出错 |

## 性能测试

### 响应时间基准

- **正常情况**：< 2秒
- **大图片**：< 5秒
- **并发请求**：根据服务器配置

### 置信度评估

- **高置信度** (>80%)：识别结果非常可信
- **中等置信度** (60-80%)：识别结果较为可信  
- **低置信度** (<60%)：建议重新拍摄

## 故障排除

### 常见问题

1. **连接失败**
   - 检查服务器是否启动
   - 确认端口5000未被占用

2. **AI模型错误**
   - 检查`resnet_classifier/model.pth`文件是否存在
   - 检查PyTorch是否正确安装

3. **文件上传失败**
   - 确认图片格式正确
   - 检查文件大小不超过限制

### 调试技巧

1. **查看服务器日志**：观察Flask控制台输出
2. **检查响应Headers**：确认Content-Type正确
3. **验证文件路径**：确保临时文件目录可写

## 扩展测试

### 批量图片测试

可以编写脚本批量测试多张图片：

```javascript
// Postman Pre-request Script 示例
const fs = require('fs');
const path = require('path');

// 设置测试图片列表
const testImages = [
    'rice.jpg',
    'pizza.jpg', 
    'sushi.jpg'
];

// 随机选择一张图片进行测试
const randomImage = testImages[Math.floor(Math.random() * testImages.length)];
pm.environment.set('test_image', randomImage);
```

### 性能监控

在Tests标签页添加性能监控脚本：

```javascript
// 记录响应时间
pm.test('响应时间小于2秒', function () {
    pm.expect(pm.response.responseTime).to.be.below(2000);
});

// 记录置信度分布
const responseJson = pm.response.json();
if (responseJson.code === 200) {
    const confidence = responseJson.data.confidence;
    pm.environment.set('last_confidence', confidence);
    
    if (confidence > 80) {
        pm.test('高置信度识别', function () {
            pm.expect(confidence).to.be.above(80);
        });
    }
}
```

## 总结

AI菜品识别模块的测试重点：

1. **功能验证**：确保能正确识别各类菜品
2. **错误处理**：验证异常情况的正确处理
3. **性能检查**：确保响应时间满足要求
4. **独立性验证**：确认无需认证即可使用

通过完整的测试确保AI识别模块的稳定性和可靠性。
