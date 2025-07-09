#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
校园食堂菜品打分系统 - 主程序
Flask + SQLite + JWT 实现
"""

from flask import Flask, request, jsonify, g
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
import uuid
import json
from functools import wraps

# 创建Flask应用
app = Flask(__name__)

# 配置
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///canteen_score.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'jwt-secret-string-change-in-production'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB限制

# 初始化扩展
db = SQLAlchemy(app)
jwt = JWTManager(app)

# 创建上传目录
os.makedirs('static/uploads/canteens', exist_ok=True)
os.makedirs('static/uploads/windows', exist_ok=True)
os.makedirs('static/uploads/dishes', exist_ok=True)
os.makedirs('static/uploads/avatars', exist_ok=True)
os.makedirs('static/uploads/temp', exist_ok=True)  # 临时文件目录

# 允许的图片格式
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 管理员权限装饰器
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        from models import User  # 避免循环导入
        user = User.query.get(current_user_id)
        if not user or user.role != 'admin':
            return jsonify({'code': 403, 'message': '需要管理员权限'}), 403
        return f(*args, **kwargs)
    return decorated_function

# 导入模型
from models import User, Canteen, Window, Dish, Review, ReviewReply, Like

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # 创建默认管理员账户
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                nickname='系统管理员',
                password_hash=generate_password_hash('admin123'),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print("已创建默认管理员账户: admin/admin123")
    
    # 导入路由模块
    import routes
    import admin_routes
    
    app.run(debug=True, host='0.0.0.0', port=5000)
