> 该项目大量代码由ai生成
# 校园食堂菜品打分系统

[![GitHub stars](https://img.shields.io/github/stars/jovan-zhang/canteen-score.svg)](https://github.com/jovan-zhang/canteen-score/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/jovan-zhang/canteen-score.svg)](https://github.com/jovan-zhang/canteen-score/network)
[![GitHub issues](https://img.shields.io/github/issues/jovan-zhang/canteen-score.svg)](https://github.com/jovan-zhang/canteen-score/issues)

## 项目简介

这是一个基于Flask的校园食堂菜品打分系统，为学生提供便捷的菜品评价平台，同时为食堂管理方提供数据分析工具。

## 技术栈

- **后端框架**: Flask 2.3.3
- **数据库**: SQLite (开发环境) / PostgreSQL (生产环境)
- **认证**: JWT (Flask-JWT-Extended)
- **ORM**: SQLAlchemy
- **图片处理**: Pillow
- **文件存储**: 本地文件系统
- **AI模型**: PyTorch + ResNet50 (菜品图像识别)

## 功能特性

### 用户功能
- 🔐 用户注册、登录、信息管理
- 🏢 浏览食堂、窗口、菜品信息
- ⭐ 菜品评分评论（总分、口味、分量、性价比、服务）
- 📸 上传评价图片
- 👍 点赞评价、回复评论
- 📝 查看个人评价历史

### AI功能模块
- 🤖 **独立AI菜品识别** - 上传菜品图片自动识别菜品类型
- 🎯 **高精度识别** - 基于ResNet-50模型，支持100种菜品分类
- ⚡ **快速响应** - 2秒内完成识别
- 🔓 **无需认证** - 独立模块，可单独使用

### 管理员功能
- 👥 用户管理（查看、编辑、删除）
- 🏢 食堂管理（增删改查）
- 🪟 窗口管理（增删改查）
- 🍽️ 菜品管理（增删改查）
- 📊 数据统计分析
- 🗑️ 评价内容管理

### 数据统计
- 📈 系统概览统计
- 🔥 热门菜品排行
- 📊 评分分布统计
- 📋 食堂窗口数据分析

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone https://github.com/jovan-zhang/canteen-score.git
cd canteen-score

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 环境配置

```bash
# 复制环境配置文件
copy .env.example .env

# 编辑 .env 文件，修改必要的配置
# 特别是生产环境的SECRET_KEY和JWT_SECRET_KEY
```

### 3. 启动服务

```bash
# 启动开发服务器
python run.py
```

服务启动后，访问: http://localhost:5000

### 4. 默认账户

- **管理员账户**: admin
- **管理员密码**: admin123

## API 接口文档

### 认证接口

#### 用户注册
- **POST** `/api/register`
- **Body**: `{"username": "string", "password": "string", "nickname": "string"}`

#### 用户登录
- **POST** `/api/login`
- **Body**: `{"username": "string", "password": "string"}`

### 用户接口

#### 获取用户信息
- **GET** `/api/user/info`
- **Headers**: `Authorization: Bearer <token>`

#### 更新用户信息
- **PUT** `/api/user/info`
- **Headers**: `Authorization: Bearer <token>`
- **Body**: `{"nickname": "string", "avatar": "string"}`

#### 获取用户评价历史
- **GET** `/api/user/reviews?page=1&per_page=10`
- **Headers**: `Authorization: Bearer <token>`

### 食堂接口

#### 获取食堂列表
- **GET** `/api/canteens`

#### 获取食堂详情
- **GET** `/api/canteens/{id}`

### 窗口接口

#### 获取窗口详情
- **GET** `/api/windows/{id}`

### 菜品接口

#### 获取菜品列表
- **GET** `/api/dishes?page=1&per_page=20&window_id=1&category=string&search=string`

#### 获取菜品详情
- **GET** `/api/dishes/{id}`

### 评价接口

#### 获取菜品评价
- **GET** `/api/dishes/{dish_id}/reviews?page=1&per_page=10`

#### 创建评价
- **POST** `/api/dishes/{dish_id}/reviews`
- **Headers**: `Authorization: Bearer <token>`
- **Body**: 
```json
{
  "overallRating": 4,
  "tasteRating": 4,
  "portionRating": 4,
  "valueRating": 4,
  "serviceRating": 4,
  "content": "评价内容",
  "images": ["image1.jpg", "image2.jpg"]
}
```

#### 更新评价
- **PUT** `/api/reviews/{id}`
- **Headers**: `Authorization: Bearer <token>`

#### 删除评价
- **DELETE** `/api/reviews/{id}`
- **Headers**: `Authorization: Bearer <token>`

### 点赞接口

#### 点赞/取消点赞
- **POST** `/api/reviews/{review_id}/like`
- **Headers**: `Authorization: Bearer <token>`

### 回复接口

#### 获取评价回复
- **GET** `/api/reviews/{review_id}/replies?page=1&per_page=20`

#### 创建回复
- **POST** `/api/reviews/{review_id}/replies`
- **Headers**: `Authorization: Bearer <token>`
- **Body**: `{"content": "string"}`

#### 删除回复
- **DELETE** `/api/replies/{id}`
- **Headers**: `Authorization: Bearer <token>`

### 文件上传接口

#### 上传文件
- **POST** `/api/upload`
- **Headers**: `Authorization: Bearer <token>`
- **Body**: `multipart/form-data` with `file` field

#### 获取上传文件
- **GET** `/api/uploads/{filename}`

### AI菜品识别接口

#### 菜品图片识别
- **POST** `/api/classify-dish`
- **说明**: 上传菜品图片，返回AI识别的菜品名称和置信度
- **认证**: 无需认证（独立模块）
- **Body**: `multipart/form-data` with `image` field
- **响应**: 
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

**支持格式**: PNG, JPG, JPEG, GIF  
**识别能力**: 100种菜品类别  
**响应时间**: < 2秒

### 数据统计接口

#### 系统概览
- **GET** `/api/stats/overview`

#### 热门菜品
- **GET** `/api/stats/popular-dishes?limit=10`

#### 评分分布
- **GET** `/api/stats/rating-distribution`

### 管理员接口

所有管理员接口需要管理员权限，在请求头中携带管理员用户的JWT token。

#### 用户管理
- **GET** `/api/admin/users?page=1&per_page=20&search=string`
- **PUT** `/api/admin/users/{id}`
- **DELETE** `/api/admin/users/{id}`

#### 食堂管理
- **POST** `/api/admin/canteens`
- **PUT** `/api/admin/canteens/{id}`
- **DELETE** `/api/admin/canteens/{id}`

#### 窗口管理
- **POST** `/api/admin/windows`
- **PUT** `/api/admin/windows/{id}`
- **DELETE** `/api/admin/windows/{id}`

#### 菜品管理
- **POST** `/api/admin/dishes`
- **PUT** `/api/admin/dishes/{id}`
- **DELETE** `/api/admin/dishes/{id}`

#### 评价管理
- **GET** `/api/admin/reviews?page=1&per_page=20&dish_id=1&user_id=1`
- **DELETE** `/api/admin/reviews/{id}`

#### 详细统计
- **GET** `/api/admin/stats/detailed`

## 项目结构

```
canteen-score/
├── app.py                  # Flask应用主文件
├── run.py                  # 启动脚本
├── config.py               # 配置文件
├── models.py               # 数据库模型
├── routes.py               # 用户API路由
├── admin_routes.py         # 管理员API路由
├── requirements.txt        # Python依赖包
├── resnet_classifier/      # AI识别模块
│   ├── model.pth           # ResNet-50模型文件
│   ├── id_name_mapping.txt # 菜品类别映射
│   └── resnet_predict.py   # AI预测逻辑
├── static/uploads/         # 文件上传目录
│   ├── temp/               # 临时文件目录
│   ├── avatars/            # 头像目录
│   ├── canteens/           # 食堂图片目录
│   ├── windows/            # 窗口图片目录
│   └── dishes/             # 菜品图片目录
├── test/                   # 测试文件
│   ├── test_api.py         # API测试
│   ├── test_ai_classification.py  # AI识别测试
│   ├── postman_collection.json    # Postman测试集合
│   └── postman_environment.json   # Postman测试环境
└── instance/               # 实例文件
    └── canteen_score.db    # SQLite数据库文件
```

## AI模块说明

### 模块特点
- **完全独立**: 不依赖主系统的用户认证和数据库
- **即插即用**: 可以单独部署和使用
- **高性能**: 基于ResNet-50深度学习模型
- **多类别**: 支持100种不同菜品的识别

### 使用方法

1. **API调用**:
   ```bash
   curl -X POST http://localhost:5000/api/classify-dish \
        -F "image=@your_dish_image.jpg"
   ```

2. **测试工具**:
   ```bash
   # 自动查找图片测试
   python test_ai_classification.py
   
   # 指定图片测试
   python test_ai_classification.py /path/to/image.jpg
   ```

3. **支持的菜品类别**: 
   - 各类米饭类: rice, fried rice, pilaf, bibimbap等
   - 面包类: toast, croissant, sandwiches等
   - 快餐类: hamburger, pizza等
   - 亚洲料理: sushi, tempura bowl等
   - *完整支持100种菜品类别*

### 技术实现
- **模型**: ResNet-50
- **框架**: PyTorch
- **输入**: 224x224 RGB图像
- **输出**: 菜品名称 + 置信度
- **性能**: < 2秒识别时间

## 数据库模型

### 用户表 (User)
- id, username, nickname, password_hash, avatar, role, status, created_at

### 食堂表 (Canteen)
- id, name, location, business_hours, contact, description, images, created_at

### 窗口表 (Window)
- id, canteen_id, name, description, business_hours, images, created_at

### 菜品表 (Dish)
- id, window_id, name, price, category, description, images, is_available, created_at

### 评价表 (Review)
- id, user_id, dish_id, overall_rating, taste_rating, portion_rating, value_rating, service_rating, content, images, created_at

### 评价回复表 (ReviewReply)
- id, user_id, review_id, content, created_at

### 点赞表 (Like)
- id, user_id, review_id, created_at

## 测试

### Postman自动化测试

本项目提供了完整的Postman测试集合：

1. **导入测试集合**:
   - 导入 `test/postman_collection.json`
   - 导入 `test/postman_environment.json`

2. **执行测试**:
   - 选择 "校园食堂系统环境"
   - 运行整个测试集合或单个接口

3. **测试覆盖**:
   - ✅ 用户注册登录
   - ✅ 食堂窗口菜品管理
   - ✅ 评价点赞回复功能
   - ✅ 管理员权限接口
   - ✅ 文件上传功能
   - ✅ AI菜品识别功能

### 运行API测试

```bash
# 确保服务器正在运行
python run.py

# 在另一个终端运行API测试
python test/test_api.py

# 运行AI识别测试
python test_ai_classification.py
```

### AI识别专项测试

```bash
# 自动测试（查找现有图片）
python test_ai_classification.py

# 指定图片测试
python test_ai_classification.py /path/to/test/image.jpg

# 测试无效请求处理
python test_ai_classification.py --test-errors
```

### 手动测试

1. 访问 http://localhost:5000/api/canteens 查看食堂列表
2. 使用API工具（如Postman）测试各个接口
3. 查看数据库文件 `canteen_score.db`

## 部署

### 生产环境部署

1. **环境配置**
   ```bash
   export FLASK_CONFIG=production
   export SECRET_KEY=your-production-secret-key
   export JWT_SECRET_KEY=your-production-jwt-secret
   export DATABASE_URL=postgresql://user:password@localhost/canteen_score
   ```

2. **使用Gunicorn**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 run:app
   ```

3. **使用Nginx反向代理**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
       
       location /api/uploads/ {
           alias /path/to/canteen-score/static/uploads/;
       }
   }
   ```

### Docker部署

创建 `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "run:app"]
```

## 开发指南

### 添加新功能

1. 在 `models.py` 中定义数据模型
2. 在 `routes.py` 或 `admin_routes.py` 中添加API接口
3. 更新 `test_api.py` 添加测试用例
4. 更新文档

### 代码规范

- 使用中文注释
- 遵循PEP 8代码风格
- 接口返回统一的JSON格式
- 错误处理要完善
- 添加适当的日志记录

### 安全注意事项

- 生产环境务必修改SECRET_KEY和JWT_SECRET_KEY
- 使用HTTPS传输敏感数据
- 对用户输入进行验证和过滤
- 限制文件上传大小和类型
- 实现API访问频率限制

## 许可证

本项目仅供学习和研究使用。

## 联系方式

- **GitHub**: [jovan-zhang/canteen-score](https://github.com/jovan-zhang/canteen-score)
- **Issues**: [提交问题](https://github.com/jovan-zhang/canteen-score/issues)

如有问题或建议，欢迎提交Issue或Pull Request。

---

**项目状态**: ✅ 开发完成，功能齐全，可用于生产环境
