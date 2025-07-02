from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash

from app import app, db, admin_required
from models import User, Canteen, Window, Dish, Review, ReviewReply, Like


# ================== 管理员用户管理接口 ==================

@app.route('/api/admin/users', methods=['GET'])
@jwt_required()
@admin_required
def admin_get_users():
    """管理员获取用户列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        per_page = min(per_page, 50)
        
        search = request.args.get('search')
        
        query = User.query
        
        if search:
            query = query.filter(
                db.or_(
                    User.username.contains(search),
                    User.nickname.contains(search)
                )
            )
        
        users = query.order_by(User.created_at.desc())\
                    .paginate(page=page, per_page=per_page, error_out=False)
        
        result = []
        for user in users.items:
            # 获取用户统计信息
            review_count = Review.query.filter_by(user_id=user.id).count()
            
            result.append({
                'id': user.id,
                'username': user.username,
                'nickname': user.nickname,
                'avatar': user.avatar,
                'is_admin': user.is_admin,
                'created_at': user.created_at.isoformat(),
                'review_count': review_count
            })
        
        return jsonify({
            'code': 200,
            'data': {
                'users': result,
                'pagination': {
                    'page': users.page,
                    'per_page': users.per_page,
                    'total': users.total,
                    'pages': users.pages
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500


@app.route('/api/admin/users/<int:user_id>', methods=['PUT'])
@jwt_required()
@admin_required
def admin_update_user(user_id):
    """管理员更新用户信息"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'code': 404, 'message': '用户不存在'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'code': 400, 'message': '请求数据不能为空'}), 400
        
        # 更新昵称
        if 'nickname' in data:
            nickname = data['nickname'].strip()
            if nickname:
                user.nickname = nickname
        
        # 更新管理员状态
        if 'is_admin' in data:
            is_admin = bool(data['is_admin'])
            user.role = 'admin' if is_admin else 'student'
        
        # 重置密码
        if 'reset_password' in data and data['reset_password']:
            new_password = data.get('new_password', '123456')
            user.password_hash = generate_password_hash(new_password)
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '更新成功',
            'data': {
                'id': user.id,
                'username': user.username,
                'nickname': user.nickname,
                'is_admin': user.is_admin
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500


@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def admin_delete_user(user_id):
    """管理员删除用户"""
    try:
        current_user_id = get_jwt_identity()
        
        if int(current_user_id) == user_id:
            return jsonify({'code': 400, 'message': '不能删除自己'}), 400
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'code': 404, 'message': '用户不存在'}), 404
        
        # 删除用户相关的数据
        Review.query.filter_by(user_id=user_id).delete()
        ReviewReply.query.filter_by(user_id=user_id).delete()
        Like.query.filter_by(user_id=user_id).delete()
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '删除成功'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500


# ================== 管理员食堂管理接口 ==================

@app.route('/api/admin/canteens', methods=['POST'])
@jwt_required()
@admin_required
def admin_create_canteen():
    """管理员创建食堂"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'code': 400, 'message': '请求数据不能为空'}), 400
        
        name = data.get('name', '').strip()
        location = data.get('location', '').strip()
        business_hours = data.get('business_hours', '').strip()
        contact = data.get('contact', '').strip()
        description = data.get('description', '').strip()
        images = data.get('images', [])
        
        if not name:
            return jsonify({'code': 400, 'message': '食堂名称不能为空'}), 400
        
        if not location:
            return jsonify({'code': 400, 'message': '食堂位置不能为空'}), 400
        
        # 检查名称是否重复
        if Canteen.query.filter_by(name=name).first():
            return jsonify({'code': 400, 'message': '食堂名称已存在'}), 400
        
        if isinstance(images, str):
            images = [images] if images else []
        
        canteen = Canteen(
            name=name,
            location=location,
            business_hours=business_hours,
            contact=contact,
            description=description,
            images=images
        )
        
        db.session.add(canteen)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '创建成功',
            'data': {
                'id': canteen.id,
                'name': canteen.name,
                'location': canteen.location,
                'business_hours': canteen.business_hours,
                'contact': canteen.contact,
                'description': canteen.description,
                'images': canteen.images
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500


@app.route('/api/admin/canteens/<int:canteen_id>', methods=['PUT'])
@jwt_required()
@admin_required
def admin_update_canteen(canteen_id):
    """管理员更新食堂信息"""
    try:
        canteen = Canteen.query.get(canteen_id)
        if not canteen:
            return jsonify({'code': 404, 'message': '食堂不存在'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'code': 400, 'message': '请求数据不能为空'}), 400
        
        # 更新字段
        if 'name' in data:
            name = data['name'].strip()
            if name:
                # 检查名称是否重复（排除自己）
                existing = Canteen.query.filter(Canteen.name == name, Canteen.id != canteen_id).first()
                if existing:
                    return jsonify({'code': 400, 'message': '食堂名称已存在'}), 400
                canteen.name = name
        
        if 'location' in data:
            location = data['location'].strip()
            if location:
                canteen.location = location
        
        if 'business_hours' in data:
            canteen.business_hours = data['business_hours'].strip()
        
        if 'contact' in data:
            canteen.contact = data['contact'].strip()
        
        if 'description' in data:
            canteen.description = data['description'].strip()
        
        if 'images' in data:
            images = data['images']
            if isinstance(images, str):
                images = [images] if images else []
            canteen.images = images
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '更新成功',
            'data': {
                'id': canteen.id,
                'name': canteen.name,
                'location': canteen.location,
                'business_hours': canteen.business_hours,
                'contact': canteen.contact,
                'description': canteen.description,
                'images': canteen.images
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500


@app.route('/api/admin/canteens/<int:canteen_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def admin_delete_canteen(canteen_id):
    """管理员删除食堂"""
    try:
        canteen = Canteen.query.get(canteen_id)
        if not canteen:
            return jsonify({'code': 404, 'message': '食堂不存在'}), 404
        
        # 检查是否有关联的窗口
        if canteen.windows:
            return jsonify({'code': 400, 'message': '该食堂下还有窗口，无法删除'}), 400
        
        db.session.delete(canteen)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '删除成功'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500


# ================== 管理员窗口管理接口 ==================

@app.route('/api/admin/windows', methods=['POST'])
@jwt_required()
@admin_required
def admin_create_window():
    """管理员创建窗口"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'code': 400, 'message': '请求数据不能为空'}), 400
        
        canteen_id = data.get('canteen_id')
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        business_hours = data.get('business_hours', '').strip()
        images = data.get('images', [])
        
        if not canteen_id:
            return jsonify({'code': 400, 'message': '食堂ID不能为空'}), 400
        
        if not name:
            return jsonify({'code': 400, 'message': '窗口名称不能为空'}), 400
        
        # 检查食堂是否存在
        canteen = Canteen.query.get(canteen_id)
        if not canteen:
            return jsonify({'code': 404, 'message': '食堂不存在'}), 404
        
        # 检查同一食堂下窗口名称是否重复
        if Window.query.filter_by(canteen_id=canteen_id, name=name).first():
            return jsonify({'code': 400, 'message': '该食堂下窗口名称已存在'}), 400
        
        if isinstance(images, str):
            images = [images] if images else []
        
        window = Window(
            canteen_id=canteen_id,
            name=name,
            description=description,
            business_hours=business_hours,
            images=images
        )
        
        db.session.add(window)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '创建成功',
            'data': {
                'id': window.id,
                'canteen_id': window.canteen_id,
                'name': window.name,
                'description': window.description,
                'business_hours': window.business_hours,
                'images': window.images,
                'canteen_name': canteen.name
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500


@app.route('/api/admin/windows/<int:window_id>', methods=['PUT'])
@jwt_required()
@admin_required
def admin_update_window(window_id):
    """管理员更新窗口信息"""
    try:
        window = Window.query.get(window_id)
        if not window:
            return jsonify({'code': 404, 'message': '窗口不存在'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'code': 400, 'message': '请求数据不能为空'}), 400
        
        # 更新字段
        if 'name' in data:
            name = data['name'].strip()
            if name:
                # 检查同一食堂下名称是否重复（排除自己）
                existing = Window.query.filter(
                    Window.canteen_id == window.canteen_id,
                    Window.name == name,
                    Window.id != window_id
                ).first()
                if existing:
                    return jsonify({'code': 400, 'message': '该食堂下窗口名称已存在'}), 400
                window.name = name
        
        if 'description' in data:
            window.description = data['description'].strip()
        
        if 'business_hours' in data:
            window.business_hours = data['business_hours'].strip()
        
        if 'images' in data:
            images = data['images']
            if isinstance(images, str):
                images = [images] if images else []
            window.images = images
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '更新成功',
            'data': {
                'id': window.id,
                'canteen_id': window.canteen_id,
                'name': window.name,
                'description': window.description,
                'business_hours': window.business_hours,
                'images': window.images
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500


@app.route('/api/admin/windows/<int:window_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def admin_delete_window(window_id):
    """管理员删除窗口"""
    try:
        window = Window.query.get(window_id)
        if not window:
            return jsonify({'code': 404, 'message': '窗口不存在'}), 404
        
        # 检查是否有关联的菜品
        if window.dishes:
            return jsonify({'code': 400, 'message': '该窗口下还有菜品，无法删除'}), 400
        
        db.session.delete(window)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '删除成功'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500


# ================== 管理员菜品管理接口 ==================

@app.route('/api/admin/dishes', methods=['POST'])
@jwt_required()
@admin_required
def admin_create_dish():
    """管理员创建菜品"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'code': 400, 'message': '请求数据不能为空'}), 400
        
        window_id = data.get('window_id')
        name = data.get('name', '').strip()
        price = data.get('price')
        category = data.get('category', '').strip()
        description = data.get('description', '').strip()
        images = data.get('images', [])
        is_available = data.get('is_available', True)
        
        if not window_id:
            return jsonify({'code': 400, 'message': '窗口ID不能为空'}), 400
        
        if not name:
            return jsonify({'code': 400, 'message': '菜品名称不能为空'}), 400
        
        if price is None or price < 0:
            return jsonify({'code': 400, 'message': '菜品价格必须大于等于0'}), 400
        
        # 检查窗口是否存在
        window = Window.query.get(window_id)
        if not window:
            return jsonify({'code': 404, 'message': '窗口不存在'}), 404
        
        # 检查同一窗口下菜品名称是否重复
        if Dish.query.filter_by(window_id=window_id, name=name).first():
            return jsonify({'code': 400, 'message': '该窗口下菜品名称已存在'}), 400
        
        if isinstance(images, str):
            images = [images] if images else []
        
        dish = Dish(
            window_id=window_id,
            name=name,
            price=price,
            category=category,
            description=description,
            images=images,
            is_available=is_available
        )
        
        db.session.add(dish)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '创建成功',
            'data': {
                'id': dish.id,
                'window_id': dish.window_id,
                'name': dish.name,
                'price': dish.price,
                'category': dish.category,
                'description': dish.description,
                'images': dish.images,
                'is_available': dish.is_available,
                'window_name': window.name,
                'canteen_name': window.canteen.name
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500


@app.route('/api/admin/dishes/<int:dish_id>', methods=['PUT'])
@jwt_required()
@admin_required
def admin_update_dish(dish_id):
    """管理员更新菜品信息"""
    try:
        dish = Dish.query.get(dish_id)
        if not dish:
            return jsonify({'code': 404, 'message': '菜品不存在'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'code': 400, 'message': '请求数据不能为空'}), 400
        
        # 更新字段
        if 'name' in data:
            name = data['name'].strip()
            if name:
                # 检查同一窗口下名称是否重复（排除自己）
                existing = Dish.query.filter(
                    Dish.window_id == dish.window_id,
                    Dish.name == name,
                    Dish.dish_id != dish_id
                ).first()
                if existing:
                    return jsonify({'code': 400, 'message': '该窗口下菜品名称已存在'}), 400
                dish.name = name
        
        if 'price' in data:
            price = data['price']
            if price is not None and price >= 0:
                dish.price = price
        
        if 'category' in data:
            dish.category = data['category'].strip()
        
        if 'description' in data:
            dish.description = data['description'].strip()
        
        if 'images' in data:
            images = data['images']
            if isinstance(images, str):
                images = [images] if images else []
            dish.images = images
        
        if 'is_available' in data:
            dish.is_available = bool(data['is_available'])
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '更新成功',
            'data': {
                'id': dish.id,
                'window_id': dish.window_id,
                'name': dish.name,
                'price': dish.price,
                'category': dish.category,
                'description': dish.description,
                'images': dish.images,
                'is_available': dish.is_available
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500


@app.route('/api/admin/dishes/<int:dish_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def admin_delete_dish(dish_id):
    """管理员删除菜品"""
    try:
        dish = Dish.query.get(dish_id)
        if not dish:
            return jsonify({'code': 404, 'message': '菜品不存在'}), 404
        
        # 删除菜品相关的数据
        Review.query.filter_by(dish_id=dish_id).delete()
        
        db.session.delete(dish)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '删除成功'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500


# ================== 管理员评价管理接口 ==================

@app.route('/api/admin/reviews', methods=['GET'])
@jwt_required()
@admin_required
def admin_get_reviews():
    """管理员获取评价列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        per_page = min(per_page, 50)
        
        dish_id = request.args.get('dish_id', type=int)
        user_id = request.args.get('user_id', type=int)
        
        query = Review.query
        
        if dish_id:
            query = query.filter_by(dish_id=dish_id)
        
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        reviews = query.order_by(Review.created_at.desc())\
                      .paginate(page=page, per_page=per_page, error_out=False)
        
        result = []
        for review in reviews.items:
            result.append({
                'id': review.id,
                'user': {
                    'id': review.user.id,
                    'username': review.user.username,
                    'nickname': review.user.nickname
                },
                'dish': {
                    'id': review.dish.id,
                    'name': review.dish.name,
                    'window_name': review.dish.window.name,
                    'canteen_name': review.dish.window.canteen.name
                },
                'overall_rating': review.overall_rating,
                'taste_rating': review.taste_rating,
                'portion_rating': review.portion_rating,
                'value_rating': review.value_rating,
                'service_rating': review.service_rating,
                'content': review.content,
                'images': review.images,
                'like_count': review.like_count,
                'reply_count': review.reply_count,
                'created_at': review.created_at.isoformat()
            })
        
        return jsonify({
            'code': 200,
            'data': {
                'reviews': result,
                'pagination': {
                    'page': reviews.page,
                    'per_page': reviews.per_page,
                    'total': reviews.total,
                    'pages': reviews.pages
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500


@app.route('/api/admin/reviews/<int:review_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def admin_delete_review(review_id):
    """管理员删除评价"""
    try:
        review = Review.query.get(review_id)
        if not review:
            return jsonify({'code': 404, 'message': '评价不存在'}), 404
        
        # 删除相关的回复和点赞
        ReviewReply.query.filter_by(review_id=review_id).delete()
        Like.query.filter_by(review_id=review_id).delete()
        
        db.session.delete(review)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '删除成功'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500


# ================== 管理员统计数据接口 ==================

@app.route('/api/admin/stats/detailed', methods=['GET'])
@jwt_required()
@admin_required
def admin_get_detailed_stats():
    """管理员获取详细统计数据"""
    try:
        # 基础统计
        stats = {
            'user_count': User.query.count(),
            'admin_count': User.query.filter_by(role='admin').count(),
            'canteen_count': Canteen.query.count(),
            'window_count': Window.query.count(),
            'dish_count': Dish.query.count(),
            'available_dish_count': Dish.query.filter_by(is_available=True).count(),
            'review_count': Review.query.count(),
            'reply_count': ReviewReply.query.count(),
            'like_count': Like.query.count()
        }
        
        # 评分统计
        avg_rating = db.session.query(db.func.avg(Review.overall_rating)).scalar()
        stats['average_rating'] = round(float(avg_rating), 2) if avg_rating else 0.0
        
        # 各食堂统计
        canteen_stats = []
        canteens = Canteen.query.all()
        for canteen in canteens:
            canteen_stats.append({
                'id': canteen.id,
                'name': canteen.name,
                'window_count': len(canteen.windows),
                'dish_count': sum(len(window.dishes) for window in canteen.windows),
                'review_count': canteen.get_review_count(),
                'average_rating': canteen.get_average_rating()
            })
        
        stats['canteen_stats'] = canteen_stats
        
        return jsonify({
            'code': 200,
            'data': stats
        }), 200
        
    except Exception as e:
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500
