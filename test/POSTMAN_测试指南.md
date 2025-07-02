# Postman API 测试指南

## 🚀 快速开始

### 1. 启动后端服务
```bash
cd d:\canteen-score
python run.py
```

确保看到服务器启动成功的提示信息。

### 2. 导入Postman集合

在Postman中：
1. 点击 **Import** 按钮
2. 选择文件导入，导入以下两个文件：
   - `postman_collection.json` - API测试集合
   - `postman_environment.json` - 环境变量

### 3. 设置环境

1. 在Postman右上角选择 **"校园食堂系统环境"**
2. 确保 `base_url` 设置为 `http://localhost:5000`

## 📋 测试流程

### 第一步：用户认证测试

#### 1.1 管理员登录 ⭐ **首先执行**
- 请求：`POST /api/login`
- 用户名：`admin`
- 密码：`admin123`
- **重要**：这会自动保存 `admin_token` 到环境变量

#### 1.2 用户注册
- 请求：`POST /api/register`
- 测试新用户注册功能

#### 1.3 用户登录
- 请求：`POST /api/login`
- 使用刚注册的用户信息登录
- **重要**：这会自动保存 `user_token` 到环境变量

### 第二步：基础数据浏览

#### 2.1 获取食堂列表
- 请求：`GET /api/canteens`
- 查看系统中的所有食堂
- **自动保存**：第一个食堂的ID到 `canteen_id`

#### 2.2 获取菜品列表
- 请求：`GET /api/dishes`
- 查看所有可用菜品
- **自动保存**：第一个菜品的ID到 `dish_id`

#### 2.3 获取食堂详情
- 请求：`GET /api/canteens/{{canteen_id}}`
- 查看特定食堂的详细信息

### 第三步：评价系统测试

#### 3.1 创建菜品评价 ⭐ **需要用户token**
- 请求：`POST /api/dishes/{{dish_id}}/reviews`
- 测试多维度评分功能
- **自动保存**：评价ID到 `review_id`

#### 3.2 获取评价列表
- 请求：`GET /api/dishes/{{dish_id}}/reviews`
- 查看刚创建的评价

#### 3.3 点赞评价
- 请求：`POST /api/reviews/{{review_id}}/like`
- 测试点赞功能

#### 3.4 回复评价
- 请求：`POST /api/reviews/{{review_id}}/replies`
- 测试回复功能

### 第四步：用户功能测试

#### 4.1 获取用户信息
- 请求：`GET /api/user/info`
- 查看当前登录用户信息

#### 4.2 更新用户信息
- 请求：`PUT /api/user/info`
- 测试用户信息修改

#### 4.3 获取评价历史
- 请求：`GET /api/user/reviews`
- 查看用户的评价历史

### 第五步：管理员功能测试 ⭐ **需要管理员token**

#### 5.1 用户管理
- 请求：`GET /api/admin/users`
- 查看所有用户列表

#### 5.2 创建食堂
- 请求：`POST /api/admin/canteens`
- 测试管理员创建食堂功能

#### 5.3 创建窗口
- 请求：`POST /api/admin/windows`
- 测试管理员创建窗口功能

#### 5.4 创建菜品
- 请求：`POST /api/admin/dishes`
- 测试管理员创建菜品功能

#### 5.5 管理员统计
- 请求：`GET /api/admin/stats/detailed`
- 查看详细统计数据

### 第六步：统计功能测试

#### 6.1 系统概览
- 请求：`GET /api/stats/overview`
- 查看系统整体统计

#### 6.2 热门菜品
- 请求：`GET /api/stats/popular-dishes`
- 查看热门菜品排行

#### 6.3 评分分布
- 请求：`GET /api/stats/rating-distribution`
- 查看评分分布统计

## 🔧 高级功能

### 文件上传测试

#### 上传图片
- 请求：`POST /api/upload`
- 选择一个图片文件上传
- **注意**：需要设置 `Content-Type` 为 `multipart/form-data`

### 搜索功能测试

#### 搜索菜品
- 请求：`GET /api/dishes?search=宫保&category=川菜`
- 测试按关键词和分类搜索

## 🏗️ 测试技巧

### 1. 自动化Token管理
集合中的登录请求已经配置了自动保存token的脚本：
```javascript
// 在登录请求的Tests标签页中
if (pm.response.code === 200) {
    const responseJson = pm.response.json();
    pm.environment.set('user_token', responseJson.data.token);
}
```

### 2. 环境变量使用
在请求中使用 `{{variable_name}}` 来引用环境变量：
- `{{user_token}}` - 用户JWT token
- `{{admin_token}}` - 管理员JWT token
- `{{dish_id}}` - 菜品ID
- `{{review_id}}` - 评价ID

### 3. 批量测试
1. 选择整个集合或文件夹
2. 点击 **Run** 按钮
3. 配置运行参数
4. 点击 **Run 校园食堂菜品打分系统API**

## 📊 期望结果

### 成功响应格式
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    // 具体数据
  }
}
```

### 错误响应格式
```json
{
  "code": 400,
  "message": "错误描述"
}
```

## 🐛 常见问题

### 1. Token过期
- **现象**：返回401错误
- **解决**：重新执行登录请求

### 2. 权限不足
- **现象**：返回403错误
- **解决**：确保使用了正确的token（用户/管理员）

### 3. 服务器连接失败
- **现象**：请求超时或连接被拒绝
- **解决**：确保Flask服务器正在运行

### 4. 数据不存在
- **现象**：返回404错误
- **解决**：确保测试数据已经创建，检查ID是否正确

## 📈 测试报告

执行完整测试后，您应该能看到：

✅ **用户功能**
- 注册、登录、信息管理
- 评价创建、修改、删除
- 点赞、回复功能

✅ **管理员功能**
- 用户管理
- 食堂、窗口、菜品管理
- 数据统计

✅ **系统功能**
- 文件上传
- 搜索筛选
- 统计分析

## 🎯 下一步

1. **性能测试**：使用Collection Runner进行批量测试
2. **安全测试**：测试无效token、SQL注入等
3. **边界测试**：测试极限数据、空值等情况
4. **集成测试**：测试完整的用户使用流程

---

**提示**：建议按照上述顺序执行测试，因为某些请求依赖于前面请求的结果（如需要先登录获取token）。
