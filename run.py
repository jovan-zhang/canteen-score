#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
校园食堂菜品打分系统启动脚本
"""

import os
from flask_migrate import Migrate
from app import app, db
from models import User, Canteen, Window, Dish, Review, ReviewReply, Like
from config import config

# 获取配置环境
config_name = os.getenv('FLASK_CONFIG') or 'default'
app.config.from_object(config[config_name])
config[config_name].init_app(app)

# 数据库迁移
migrate = Migrate(app, db)


def create_admin():
    """创建默认管理员账户"""
    from werkzeug.security import generate_password_hash
    
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            nickname='系统管理员',
            password_hash=generate_password_hash('admin123'),
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        print("✓ 已创建默认管理员账户: admin/admin123")
        return True
    else:
        print("✓ 管理员账户已存在")
        return False



@app.shell_context_processor
def make_shell_context():
    """为Flask shell提供上下文"""
    return {
        'db': db,
        'User': User,
        'Canteen': Canteen,
        'Window': Window,
        'Dish': Dish,
        'Review': Review,
        'ReviewReply': ReviewReply,
        'Like': Like
    }


def run_app():
    """运行应用"""
    with app.app_context():
        # 创建数据库表
        db.create_all()
        print("✓ 数据库表创建完成")
        
        # 创建管理员账户
        create_admin()
        

        print("\n" + "="*50)
        print("🍽️  校园食堂菜品打分系统")
        print("="*50)
        print(f"📍 服务地址: http://localhost:5000")
        print(f"👤 管理员账户: admin")
        print(f"🔑 管理员密码: admin123")
        print(f"📚 API文档: 请查看需求文档.md")
        print("="*50)
    
    # 导入路由模块
    import routes
    import admin_routes
    
    # 启动应用
    app.run(
        debug=app.config.get('DEBUG', False),
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000))
    )


if __name__ == '__main__':
    run_app()
