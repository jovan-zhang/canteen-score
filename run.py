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


def init_sample_data():
    """初始化示例数据"""
    if Canteen.query.count() == 0:
        print("正在创建示例数据...")
        
        # 创建食堂
        canteen1 = Canteen(
            name="第一食堂",
            location="学校东区",
            business_hours="06:30-21:00",
            contact="123-456-7890",
            description="学校最大的食堂，提供多种美食选择"
        )
        
        canteen2 = Canteen(
            name="第二食堂",
            location="学校西区", 
            business_hours="07:00-20:30",
            contact="123-456-7891",
            description="以地方特色菜为主的食堂"
        )
        
        db.session.add_all([canteen1, canteen2])
        db.session.commit()
        
        # 创建窗口
        window1 = Window(
            canteen_id=canteen1.id,
            name="川菜窗口",
            description="正宗川菜，麻辣鲜香",
            business_hours="11:00-13:30, 17:00-19:30"
        )
        
        window2 = Window(
            canteen_id=canteen1.id,
            name="粤菜窗口", 
            description="精致粤菜，清淡爽口",
            business_hours="11:00-13:30, 17:00-19:30"
        )
        
        window3 = Window(
            canteen_id=canteen2.id,
            name="面食窗口",
            description="各式面条，汤面干面应有尽有",
            business_hours="07:00-09:00, 11:00-13:30, 17:00-19:30"
        )
        
        db.session.add_all([window1, window2, window3])
        db.session.commit()
        
        # 创建菜品
        dishes = [
            Dish(window_id=window1.id, name="宫保鸡丁", price=12.0, category="川菜", description="经典川菜，鸡丁爽嫩，花生酥脆"),
            Dish(window_id=window1.id, name="麻婆豆腐", price=10.0, category="川菜", description="麻辣鲜香，豆腐嫩滑"),
            Dish(window_id=window1.id, name="水煮鱼", price=18.0, category="川菜", description="鱼肉鲜嫩，汤底麻辣"),
            
            Dish(window_id=window2.id, name="白切鸡", price=15.0, category="粤菜", description="皮爽肉嫩，清香淡雅"),
            Dish(window_id=window2.id, name="蒸蛋羹", price=8.0, category="粤菜", description="嫩滑如丝，营养丰富"),
            Dish(window_id=window2.id, name="糖醋排骨", price=16.0, category="粤菜", description="酸甜可口，色泽诱人"),
            
            Dish(window_id=window3.id, name="兰州拉面", price=12.0, category="面食", description="汤清面白，牛肉香浓"),
            Dish(window_id=window3.id, name="炸酱面", price=10.0, category="面食", description="酱香浓郁，面条劲道"),
            Dish(window_id=window3.id, name="西红柿鸡蛋面", price=9.0, category="面食", description="酸甜开胃，营养均衡")
        ]
        
        db.session.add_all(dishes)
        db.session.commit()
        
        print("✓ 示例数据创建完成")
        print(f"  - 食堂: {Canteen.query.count()}个")
        print(f"  - 窗口: {Window.query.count()}个") 
        print(f"  - 菜品: {Dish.query.count()}个")


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
        
        # 创建示例数据
        init_sample_data()
        
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
