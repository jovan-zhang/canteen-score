# AI菜品图片识别API接口文档

## 概述
本文档描述了AI菜品图片识别功能的API接口。该功能是一个独立的模块，使用ResNet深度学习模型对上传的菜品图片进行自动识别，返回菜品名称和置信度。

## 重要说明
- **独立模块**: AI识别功能完全独立，不依赖于主系统的用户认证和数据库
- **简单易用**: 只需上传图片，返回识别结果
- **无需认证**: 该接口不需要用户登录认证

## 接口详情

### 菜品图片识别接口

**接口地址**: `POST /api/classify-dish`

**功能说明**: 上传菜品图片，返回AI识别的菜品名称和置信度

**请求参数**:
- **Headers**: 
  - `Content-Type`: multipart/form-data

- **Body参数**:
  - `image`: 图片文件 (必需，支持PNG、JPG、JPEG、GIF格式)

**请求示例**:
```bash
curl -X POST \
  http://localhost:5000/api/classify-dish \
  -H 'Content-Type: multipart/form-data' \
  -F 'image=@/path/to/your/dish.jpg'
```

**成功响应示例**:
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

**响应字段说明**:
- `dish_name`: AI识别的菜品名称
- `confidence`: 识别置信度（百分比，0-100）

- **Body参数**:
## 错误响应

**错误响应格式**:
```json
{
  "code": 错误码,
  "message": "错误信息"
}
```

**常见错误码**:
- `400`: 请求参数错误
  - `请上传图片文件`: 请求中没有包含image字段
  - `未选择文件`: 文件名为空
  - `不支持的文件格式，请上传 PNG、JPG、JPEG 或 GIF 格式的图片`: 文件格式不支持
  - `文件保存失败`: 服务器存储问题

- `500`: 服务器内部错误
  - `AI模型未正确安装或配置，请联系管理员`: AI模型加载失败
  - `AI识别失败: {具体错误}`: AI识别过程出错
  - `AI识别过程中出错: {具体错误}`: 图片处理或模型推理异常

## 图片要求

- **支持格式**: PNG、JPG、JPEG、GIF
- **建议尺寸**: 224x224像素或更大（模型训练尺寸）
- **图片质量**: 清晰度越高，识别准确率越高
- **文件大小**: 建议不超过10MB
- **拍摄建议**: 
  - 从正上方或45度角拍摄
  - 保证充足光线，避免阴影
  - 背景简洁，主体突出

## 使用示例

### Python示例（使用requests库）

```python
import requests

# 直接上传图片进行识别（无需认证）
with open('dish_image.jpg', 'rb') as f:
    files = {'image': f}
    
    response = requests.post(
        'http://localhost:5000/api/classify-dish',
        files=files
    )
    
    if response.status_code == 200:
        result = response.json()
        if result['code'] == 200:
            data = result['data']
            print(f"识别结果: {data['dish_name']}")
            print(f"置信度: {data['confidence']}%")
        else:
            print(f"识别失败: {result['message']}")
    else:
        print(f"请求失败: {response.status_code}")
```

### JavaScript示例（使用fetch）

```javascript
// 假设已经有token
const token = 'your_access_token';

// 上传图片进行分类
async function classifyDish(imageFile) {
    const formData = new FormData();
    formData.append('image', imageFile);
    
    const response = await fetch('/api/classify-dish', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`
        },
        body: formData
    });
    
    const result = await response.json();
    return result;
}

// 使用示例
document.getElementById('fileInput').addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (file) {
        const result = await classifyDish(file);
        console.log('识别结果:', result);
    }
});
```

## 注意事项

1. **文件大小限制**: 上传的图片文件不能超过5MB
2. **文件格式**: 只支持jpg, jpeg, png, gif格式的图片
3. **认证要求**: 所有接口都需要用户登录并提供有效的JWT token
4. **临时文件**: 上传的图片会被保存到临时目录，识别完成后自动删除
// 上传图片进行识别（无需认证）
async function classifyDish(imageFile) {
    const formData = new FormData();
    formData.append('image', imageFile);
    
    try {
        const response = await fetch('http://localhost:5000/api/classify-dish', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (response.ok && result.code === 200) {
            console.log('识别结果:', result.data.dish_name);
            console.log('置信度:', result.data.confidence + '%');
        } else {
            console.error('识别失败:', result.message);
        }
    } catch (error) {
        console.error('请求失败:', error);
    }
}

// 使用示例
const fileInput = document.getElementById('imageInput');
fileInput.addEventListener('change', (event) => {
    const file = event.target.files[0];
    if (file) {
        classifyDish(file);
    }
});
```

### cURL示例

```bash
# 上传图片进行识别
curl -X POST \
  http://localhost:5000/api/classify-dish \
  -H 'Content-Type: multipart/form-data' \
  -F 'image=@/path/to/your/dish.jpg'
```

## 技术说明

1. **AI模型**: 基于ResNet-50深度学习模型
2. **识别能力**: 可识别100种不同菜品类别
3. **处理流程**: 图片上传 → 预处理 → AI推理 → 返回结果 → 清理临时文件
4. **独立性**: 完全独立的模块，不依赖用户认证或数据库
5. **性能**: 识别速度通常在2秒内（取决于服务器性能）

## 部署说明

1. **依赖安装**:
   ```bash
   pip install torch torchvision pillow
   ```

2. **模型文件**: 确保以下文件存在
   - `resnet_classifier/model.pth` (AI模型文件)
   - `resnet_classifier/id_name_mapping.txt` (类别映射文件)

3. **目录结构**:
   ```
   resnet_classifier/
   ├── model.pth
   ├── id_name_mapping.txt
   └── resnet_predict.py
   ```

4. **启动服务**:
   ```bash
   python run.py
   ```

## 测试

使用提供的测试脚本验证功能：

```bash
# 自动测试（查找已有图片）
python test_ai_classification.py

# 指定图片测试
python test_ai_classification.py /path/to/test/image.jpg
```
