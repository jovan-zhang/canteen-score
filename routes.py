from flask import request, jsonify, send_from_directory
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import os
from datetime import datetime
from PIL import Image
import uuid

from app import app, db
from models import User, Canteen, Window, Dish, Review, ReviewReply, Like


# 辅助函数
def allowed_file(filename):
    """检查文件扩展名是否允许"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_uploaded_file(file, upload_dir):
    """保存上传的文件并返回文件名"""
    if file and allowed_file(file.filename):
        # 生成唯一文件名
        filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
        file_path = os.path.join(upload_dir, filename)
        
        # 创建目录
        os.makedirs(upload_dir, exist_ok=True)
        
        # 保存文件
        file.save(file_path)
        
        # 如果是图片，进行压缩处理
        try:
            with Image.open(file_path) as img:
                # 限制图片最大尺寸
                max_size = (800, 600)
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                img.save(file_path, optimize=True, quality=85)
        except Exception:
            pass  # 如果不是有效图片或处理失败，保持原文件
        
        return filename
    return None


# ================== 用户认证相关接口 ==================

@app.route('/api/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'code': 400, 'message': '请求数据不能为空'}), 400
        
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        nickname = data.get('nickname', '').strip()
        
        # 验证必填字段
        if not username or not password:
            return jsonify({'code': 400, 'message': '用户名和密码不能为空'}), 400
        
        if len(username) < 3 or len(username) > 20:
            return jsonify({'code': 400, 'message': '用户名长度应在3-20个字符之间'}), 400
        
        if len(password) < 6:
            return jsonify({'code': 400, 'message': '密码长度不能少于6个字符'}), 400
        
        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            return jsonify({'code': 400, 'message': '用户名已存在'}), 400
        
        # 创建新用户
        user = User(
            username=username,
            password_hash=generate_password_hash(password),
            nickname=nickname or username
        )
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({'code': 200, 'message': '注册成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500


@app.route('/api/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'code': 400, 'message': '请求数据不能为空'}), 400
        
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        if not username or not password:
            return jsonify({'code': 400, 'message': '用户名和密码不能为空'}), 400
        
        # 查找用户
        user = User.query.filter_by(username=username).first()
        
        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({'code': 401, 'message': '用户名或密码错误'}), 401
        
        # 生成JWT token
        access_token = create_access_token(identity=str(user.id))
        
        return jsonify({
            'code': 200,
            'message': '登录成功',
            'data': {
                'token': access_token,
                'user': {
                    'id': user.user_id,
                    'username': user.username,
                    'nickname': user.nickname,
                    'avatar': user.avatar,
                    'is_admin': user.role == 'admin'
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500


@app.route('/api/user/info', methods=['GET'])
@jwt_required()
def get_user_info():
    """获取当前用户信息"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'code': 404, 'message': '用户不存在'}), 404
        
        return jsonify({
            'code': 200,
            'data': {
                'id': user.user_id,
                'username': user.username,
                'nickname': user.nickname,
                'avatar': user.avatar,
                'created_at': user.created_at.isoformat(),
                'is_admin': user.role == 'admin'
            }
        }), 200
        
    except Exception as e:
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500


@app.route('/api/user/info', methods=['PUT'])
@jwt_required()
def update_user_info():
    """更新用户信息"""
    try:
        user_id = get_jwt_identity()
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
        
        # 更新头像
        if 'avatar' in data:
            avatar = data['avatar'].strip()
            user.avatar = avatar
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '更新成功',
            'data': {
                'id': user.user_id,
                'username': user.username,
                'nickname': user.nickname,
                'avatar': user.avatar
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500


@app.route('/api/user/reviews', methods=['GET'])
@jwt_required()
def get_user_reviews():
    """获取用户评价历史"""
    try:
        user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        per_page = min(per_page, 50)  # 限制最大每页数量
        
        # 查询用户的评价
        reviews = Review.query.filter_by(user_id=user_id)\
                             .order_by(Review.created_at.desc())\
                             .paginate(page=page, per_page=per_page, error_out=False)
        
        result = []
        for review in reviews.items:
            dish = review.dish
            window = dish.window
            canteen = window.canteen
            
            result.append({
                'id': review.id,
                'dish_id': dish.id,
                'dish_name': dish.name,
                'window_name': window.name,
                'canteen_name': canteen.name,
                'overall_rating': review.overall_rating,
                'taste_rating': review.taste_rating,
                'portion_rating': review.portion_rating,
                'value_rating': review.value_rating,
                'service_rating': review.service_rating,
                'content': review.content,
                'images': review.images,
                'created_at': review.created_at.isoformat(),
                'like_count': review.like_count,
                'reply_count': review.reply_count
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


# ================== 食堂相关接口 ==================

@app.route('/api/canteens', methods=['GET'])
def get_canteens():
    """获取食堂列表"""
    try:
        canteens = Canteen.query.all()
        
        result = []
        for canteen in canteens:
            result.append({
                'id': canteen.id,
                'name': canteen.name,
                'location': canteen.location,
                'business_hours': canteen.business_hours,
                'contact': canteen.contact,
                'description': canteen.description,
                'images': canteen.images,
                'average_rating': canteen.get_average_rating(),
                'review_count': canteen.get_review_count(),
                'window_count': len(canteen.windows)
            })
        
        return jsonify({
            'code': 200,
            'data': result
        }), 200
        
    except Exception as e:
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500


@app.route('/api/canteens/<int:canteen_id>', methods=['GET'])
def get_canteen_detail(canteen_id):
    """获取食堂详情"""
    try:
        canteen = Canteen.query.get(canteen_id)
        
        if not canteen:
            return jsonify({'code': 404, 'message': '食堂不存在'}), 404
        
        # 获取窗口信息
        windows = []
        for window in canteen.windows:
            windows.append({
                'id': window.id,
                'name': window.name,
                'description': window.description,
                'business_hours': window.business_hours,
                'images': window.images,
                'average_rating': window.get_average_rating(),
                'review_count': window.get_review_count(),
                'dish_count': len(window.dishes)
            })
        
        result = {
            'id': canteen.id,
            'name': canteen.name,
            'location': canteen.location,
            'business_hours': canteen.business_hours,
            'contact': canteen.contact,
            'description': canteen.description,
            'images': canteen.images,
            'average_rating': canteen.get_average_rating(),
            'review_count': canteen.get_review_count(),
            'windows': windows
        }
        
        return jsonify({
            'code': 200,
            'data': result
        }), 200
        
    except Exception as e:
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500


# ================== 窗口相关接口 ==================

@app.route('/api/windows/<int:window_id>', methods=['GET'])
def get_window_detail(window_id):
    """获取窗口详情"""
    try:
        window = Window.query.get(window_id)
        
        if not window:
            return jsonify({'code': 404, 'message': '窗口不存在'}), 404
        
        # 获取菜品信息
        dishes = []
        for dish in window.dishes:
            dishes.append({
                'id': dish.id,
                'name': dish.name,
                'price': dish.price,
                'category': dish.category,
                'description': dish.description,
                'images': dish.images,
                'average_rating': dish.get_average_rating(),
                'review_count': dish.get_review_count(),
                'is_available': dish.is_available
            })
        
        result = {
            'id': window.id,
            'name': window.name,
            'description': window.description,
            'business_hours': window.business_hours,
            'images': window.images,
            'canteen': {
                'id': window.canteen.id,
                'name': window.canteen.name,
                'location': window.canteen.location
            },
            'average_rating': window.get_average_rating(),
            'review_count': window.get_review_count(),
            'dishes': dishes
        }
        
        return jsonify({
            'code': 200,
            'data': result
        }), 200
        
    except Exception as e:
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500


# ================== 菜品相关接口 ==================

@app.route('/api/dishes', methods=['GET'])
def get_dishes():
    """获取菜品列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        per_page = min(per_page, 50)
        
        window_id = request.args.get('window_id', type=int)
        category = request.args.get('category')
        search = request.args.get('search')
        
        query = Dish.query
        
        # 按窗口筛选
        if window_id:
            query = query.filter_by(window_id=window_id)
        
        # 按分类筛选
        if category:
            query = query.filter_by(category=category)
        
        # 搜索
        if search:
            query = query.filter(Dish.name.contains(search))
        
        # 只显示可用的菜品
        query = query.filter_by(is_available=True)
        
        dishes = query.order_by(Dish.created_at.desc())\
                     .paginate(page=page, per_page=per_page, error_out=False)
        
        result = []
        for dish in dishes.items:
            result.append({
                'id': dish.id,
                'name': dish.name,
                'price': dish.price,
                'category': dish.category,
                'description': dish.description,
                'images': dish.images,
                'window': {
                    'id': dish.window.id,
                    'name': dish.window.name,
                    'canteen_name': dish.window.canteen.name
                },
                'average_rating': dish.get_average_rating(),
                'review_count': dish.get_review_count(),
                'is_available': dish.is_available
            })
        
        return jsonify({
            'code': 200,
            'data': {
                'dishes': result,
                'pagination': {
                    'page': dishes.page,
                    'per_page': dishes.per_page,
                    'total': dishes.total,
                    'pages': dishes.pages
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500


@app.route('/api/dishes/<int:dish_id>', methods=['GET'])
def get_dish_detail(dish_id):
    """获取菜品详情"""
    try:
        dish = Dish.query.get(dish_id)
        
        if not dish:
            return jsonify({'code': 404, 'message': '菜品不存在'}), 404
        
        result = {
            'id': dish.id,
            'name': dish.name,
            'price': dish.price,
            'category': dish.category,
            'description': dish.description,
            'images': dish.images,
            'window': {
                'id': dish.window.id,
                'name': dish.window.name,
                'canteen': {
                    'id': dish.window.canteen.id,
                    'name': dish.window.canteen.name,
                    'location': dish.window.canteen.location
                }
            },
            'average_rating': dish.get_average_rating(),
            'review_count': dish.get_review_count(),
            'rating_stats': dish.get_rating_stats(),
            'is_available': dish.is_available,
            'created_at': dish.created_at.isoformat()
        }
        
        return jsonify({
            'code': 200,
            'data': result
        }), 200
        
    except Exception as e:
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500


# ================== 评价相关接口 ==================

@app.route('/api/dishes/<int:dish_id>/reviews', methods=['GET'])
def get_dish_reviews(dish_id):
    """获取菜品评价列表"""
    try:
        dish = Dish.query.get(dish_id)
        if not dish:
            return jsonify({'code': 404, 'message': '菜品不存在'}), 404
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        per_page = min(per_page, 50)
        
        reviews = Review.query.filter_by(dish_id=dish_id)\
                             .order_by(Review.created_at.desc())\
                             .paginate(page=page, per_page=per_page, error_out=False)
        
        result = []
        for review in reviews.items:
            result.append({
                'id': review.id,
                'user': {
                    'id': review.user.id,
                    'nickname': review.user.nickname,
                    'avatar': review.user.avatar
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


@app.route('/api/dishes/<int:dish_id>/reviews', methods=['POST'])
@jwt_required()
def create_review(dish_id):
    """创建菜品评价"""
    try:
        user_id = get_jwt_identity()
        dish = Dish.query.get(dish_id)
        
        if not dish:
            return jsonify({'code': 404, 'message': '菜品不存在'}), 404
        
        # 检查用户是否已经评价过该菜品
        existing_review = Review.query.filter_by(user_id=user_id, dish_id=dish_id).first()
        if existing_review:
            return jsonify({'code': 400, 'message': '您已经评价过该菜品'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'code': 400, 'message': '请求数据不能为空'}), 400
        
        # 验证评分 - 支持驼峰和下划线两种命名方式
        overall_rating = data.get('overallRating') or data.get('overall_rating')
        taste_rating = data.get('tasteRating') or data.get('taste_rating')
        portion_rating = data.get('portionRating') or data.get('portion_rating')
        value_rating = data.get('valueRating') or data.get('value_rating')
        service_rating = data.get('serviceRating') or data.get('service_rating')
        
        if not all(isinstance(rating, (int, float)) and 1 <= rating <= 5 
                   for rating in [overall_rating, taste_rating, portion_rating, value_rating, service_rating]):
            return jsonify({'code': 400, 'message': '评分必须在1-5之间'}), 400
        
        content = data.get('content', '').strip()
        images = data.get('images', [])
        
        if isinstance(images, str):
            images = [images] if images else []
        
        review = Review(
            user_id=user_id,
            dish_id=dish_id,
            overall_rating=overall_rating,
            taste_rating=taste_rating,
            portion_rating=portion_rating,
            value_rating=value_rating,
            service_rating=service_rating,
            content=content,
            images=images
        )
        
        db.session.add(review)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '评价成功',
            'data': {
                'id': review.id,
                'overall_rating': review.overall_rating,
                'taste_rating': review.taste_rating,
                'portion_rating': review.portion_rating,
                'value_rating': review.value_rating,
                'service_rating': review.service_rating,
                'content': review.content,
                'images': review.images,
                'created_at': review.created_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500


@app.route('/api/reviews/<int:review_id>', methods=['PUT'])
@jwt_required()
def update_review(review_id):
    """更新评价"""
    try:
        user_id = get_jwt_identity()
        review = Review.query.get(review_id)
        
        if not review:
            return jsonify({'code': 404, 'message': '评价不存在'}), 404
        
        if review.user_id != int(user_id):
            return jsonify({'code': 403, 'message': '无权限修改此评价'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'code': 400, 'message': '请求数据不能为空'}), 400
        
        # 更新评分 - 支持驼峰和下划线两种命名方式
        overall_rating_key = 'overallRating' if 'overallRating' in data else 'overall_rating'
        if overall_rating_key in data:
            if not (isinstance(data[overall_rating_key], (int, float)) and 1 <= data[overall_rating_key] <= 5):
                return jsonify({'code': 400, 'message': '总体评分必须在1-5之间'}), 400
            review.overall_rating = data[overall_rating_key]
        
        taste_rating_key = 'tasteRating' if 'tasteRating' in data else 'taste_rating'
        if taste_rating_key in data:
            if not (isinstance(data[taste_rating_key], (int, float)) and 1 <= data[taste_rating_key] <= 5):
                return jsonify({'code': 400, 'message': '口味评分必须在1-5之间'}), 400
            review.taste_rating = data[taste_rating_key]
        
        portion_rating_key = 'portionRating' if 'portionRating' in data else 'portion_rating'
        if portion_rating_key in data:
            if not (isinstance(data[portion_rating_key], (int, float)) and 1 <= data[portion_rating_key] <= 5):
                return jsonify({'code': 400, 'message': '分量评分必须在1-5之间'}), 400
            review.portion_rating = data[portion_rating_key]
        
        value_rating_key = 'valueRating' if 'valueRating' in data else 'value_rating'
        if value_rating_key in data:
            if not (isinstance(data[value_rating_key], (int, float)) and 1 <= data[value_rating_key] <= 5):
                return jsonify({'code': 400, 'message': '性价比评分必须在1-5之间'}), 400
            review.value_rating = data[value_rating_key]
        
        service_rating_key = 'serviceRating' if 'serviceRating' in data else 'service_rating'
        if service_rating_key in data:
            if not (isinstance(data[service_rating_key], (int, float)) and 1 <= data[service_rating_key] <= 5):
                return jsonify({'code': 400, 'message': '服务评分必须在1-5之间'}), 400
            review.service_rating = data[service_rating_key]
        
        # 更新评论内容
        if 'content' in data:
            review.content = data['content'].strip()
        
        # 更新图片
        if 'images' in data:
            images = data['images']
            if isinstance(images, str):
                images = [images] if images else []
            review.images = images
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '更新成功',
            'data': {
                'id': review.id,
                'overall_rating': review.overall_rating,
                'taste_rating': review.taste_rating,
                'portion_rating': review.portion_rating,
                'value_rating': review.value_rating,
                'service_rating': review.service_rating,
                'content': review.content,
                'images': review.images
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500


@app.route('/api/reviews/<int:review_id>', methods=['DELETE'])
@jwt_required()
def delete_review(review_id):
    """删除评价"""
    try:
        user_id = get_jwt_identity()
        review = Review.query.get(review_id)
        
        if not review:
            return jsonify({'code': 404, 'message': '评价不存在'}), 404
        
        if review.user_id != int(user_id):
            return jsonify({'code': 403, 'message': '无权限删除此评价'}), 403
        
        db.session.delete(review)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '删除成功'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500


# ================== 点赞相关接口 ==================

@app.route('/api/reviews/<int:review_id>/like', methods=['POST'])
@jwt_required()
def like_review(review_id):
    """点赞/取消点赞评价"""
    try:
        user_id = get_jwt_identity()
        review = Review.query.get(review_id)
        
        if not review:
            return jsonify({'code': 404, 'message': '评价不存在'}), 404
        
        # 检查是否已经点赞
        existing_like = Like.query.filter_by(user_id=user_id, review_id=review_id).first()
        
        if existing_like:
            # 取消点赞
            db.session.delete(existing_like)
            action = 'unliked'
        else:
            # 点赞
            like = Like(user_id=user_id, review_id=review_id)
            db.session.add(like)
            action = 'liked'
        
        db.session.commit()
        
        # 更新点赞数
        like_count = Like.query.filter_by(review_id=review_id).count()
        
        return jsonify({
            'code': 200,
            'message': '操作成功',
            'data': {
                'action': action,
                'like_count': like_count
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500


# ================== 回复相关接口 ==================

@app.route('/api/reviews/<int:review_id>/replies', methods=['GET'])
def get_review_replies(review_id):
    """获取评价回复列表"""
    try:
        review = Review.query.get(review_id)
        if not review:
            return jsonify({'code': 404, 'message': '评价不存在'}), 404
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        per_page = min(per_page, 50)
        
        replies = ReviewReply.query.filter_by(review_id=review_id)\
                                  .order_by(ReviewReply.created_at.asc())\
                                  .paginate(page=page, per_page=per_page, error_out=False)
        
        result = []
        for reply in replies.items:
            result.append({
                'id': reply.id,
                'user': {
                    'id': reply.user.id,
                    'nickname': reply.user.nickname,
                    'avatar': reply.user.avatar
                },
                'content': reply.content,
                'created_at': reply.created_at.isoformat()
            })
        
        return jsonify({
            'code': 200,
            'data': {
                'replies': result,
                'pagination': {
                    'page': replies.page,
                    'per_page': replies.per_page,
                    'total': replies.total,
                    'pages': replies.pages
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500


@app.route('/api/reviews/<int:review_id>/replies', methods=['POST'])
@jwt_required()
def create_reply(review_id):
    """创建评价回复"""
    try:
        user_id = get_jwt_identity()
        review = Review.query.get(review_id)
        
        if not review:
            return jsonify({'code': 404, 'message': '评价不存在'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'code': 400, 'message': '请求数据不能为空'}), 400
        
        content = data.get('content', '').strip()
        if not content:
            return jsonify({'code': 400, 'message': '回复内容不能为空'}), 400
        
        if len(content) > 500:
            return jsonify({'code': 400, 'message': '回复内容不能超过500个字符'}), 400
        
        reply = ReviewReply(
            user_id=user_id,
            review_id=review_id,
            content=content
        )
        
        db.session.add(reply)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '回复成功',
            'data': {
                'id': reply.id,
                'content': reply.content,
                'created_at': reply.created_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500


@app.route('/api/replies/<int:reply_id>', methods=['DELETE'])
@jwt_required()
def delete_reply(reply_id):
    """删除回复"""
    try:
        user_id = get_jwt_identity()
        reply = ReviewReply.query.get(reply_id)
        
        if not reply:
            return jsonify({'code': 404, 'message': '回复不存在'}), 404
        
        if reply.user_id != int(user_id):
            return jsonify({'code': 403, 'message': '无权限删除此回复'}), 403
        
        db.session.delete(reply)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '删除成功'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500


# ================== 文件上传接口 ==================

@app.route('/api/upload', methods=['POST'])
@jwt_required()
def upload_file():
    """文件上传"""
    try:
        if 'file' not in request.files:
            return jsonify({'code': 400, 'message': '没有文件被上传'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'code': 400, 'message': '没有选择文件'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'code': 400, 'message': '不支持的文件类型'}), 400
        
        # 保存文件
        filename = save_uploaded_file(file, app.config['UPLOAD_FOLDER'])
        if not filename:
            return jsonify({'code': 400, 'message': '文件保存失败'}), 400
        
        file_url = f'/api/uploads/{filename}'
        
        return jsonify({
            'code': 200,
            'message': '上传成功',
            'data': {
                'filename': filename,
                'url': file_url
            }
        }), 200
        
    except Exception as e:
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500


@app.route('/api/uploads/<filename>')
def uploaded_file(filename):
    """获取上传的文件"""
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except Exception:
        return jsonify({'code': 404, 'message': '文件不存在'}), 404


# ================== 数据统计接口 ==================

@app.route('/api/stats/overview', methods=['GET'])
def get_stats_overview():
    """获取系统概览统计"""
    try:
        stats = {
            'user_count': User.query.count(),
            'canteen_count': Canteen.query.count(),
            'window_count': Window.query.count(),
            'dish_count': Dish.query.count(),
            'review_count': Review.query.count(),
            'total_rating_sum': db.session.query(db.func.sum(Review.overall_rating)).scalar() or 0,
            'average_rating': round(
                (db.session.query(db.func.avg(Review.overall_rating)).scalar() or 0), 2
            )
        }
        
        return jsonify({
            'code': 200,
            'data': stats
        }), 200
        
    except Exception as e:
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500


@app.route('/api/stats/popular-dishes', methods=['GET'])
def get_popular_dishes():
    """获取热门菜品统计"""
    try:
        limit = request.args.get('limit', 10, type=int)
        limit = min(limit, 50)
        
        # 按评价数量排序获取热门菜品
        popular_dishes = db.session.query(
            Dish.dish_id,
            Dish.name,
            Window.name.label('window_name'),
            Canteen.name.label('canteen_name'),
            db.func.count(Review.review_id).label('review_count'),
            db.func.avg(Review.overall_rating).label('avg_rating')
        ).join(Review, Dish.dish_id == Review.dish_id)\
         .join(Window, Dish.window_id == Window.window_id)\
         .join(Canteen, Window.canteen_id == Canteen.canteen_id)\
         .group_by(Dish.dish_id, Dish.name, Window.name, Canteen.name)\
         .order_by(db.func.count(Review.review_id).desc())\
         .limit(limit).all()
        
        result = []
        for dish in popular_dishes:
            result.append({
                'dish_id': dish.dish_id,
                'dish_name': dish.name,
                'window_name': dish.window_name,
                'canteen_name': dish.canteen_name,
                'review_count': dish.review_count,
                'average_rating': round(float(dish.avg_rating), 2)
            })
        
        return jsonify({
            'code': 200,
            'data': result
        }), 200
        
    except Exception as e:
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500


@app.route('/api/stats/rating-distribution', methods=['GET'])
def get_rating_distribution():
    """获取评分分布统计"""
    try:
        # 统计各评分区间的数量
        distribution = {}
        for i in range(1, 6):
            count = Review.query.filter(
                Review.overall_rating >= i,
                Review.overall_rating < i + 1 if i < 5 else Review.overall_rating <= 5
            ).count()
            distribution[f'{i}星'] = count
        
        return jsonify({
            'code': 200,
            'data': distribution
        }), 200
        
    except Exception as e:
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500


# ================== AI菜品识别接口 ==================

@app.route('/api/classify-dish', methods=['POST'])
def classify_dish():
    """
    AI菜品图片识别接口
    上传图片文件，返回AI识别的菜品名称
    注意：此接口为独立的AI识别模块，不需要登录认证
    """
    try:
        # 检查是否有文件
        if 'image' not in request.files:
            return jsonify({'code': 400, 'message': '请上传图片文件'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'code': 400, 'message': '未选择文件'}), 400
        
        # 检查文件类型
        if not allowed_file(file.filename):
            return jsonify({'code': 400, 'message': '不支持的文件格式，请上传 PNG、JPG、JPEG 或 GIF 格式的图片'}), 400
        
        # 保存上传的文件到临时目录
        upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'temp')
        filename = save_uploaded_file(file, upload_dir)
        
        if not filename:
            return jsonify({'code': 400, 'message': '文件保存失败'}), 400
        
        # 获取图片的绝对路径
        image_path = os.path.abspath(os.path.join(upload_dir, filename))
        
        # 调用AI分类模型
        try:
            import sys
            import importlib.util
            
            # 动态加载模块
            classifier_path = os.path.join(os.path.dirname(__file__), 'resnet_classifier')
            predict_module_path = os.path.join(classifier_path, 'resnet_predict.py')
            
            spec = importlib.util.spec_from_file_location("resnet_predict", predict_module_path)
            resnet_predict = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(resnet_predict)
            
            # 执行AI识别
            result = resnet_predict.predict_image(image_path)
            
            # 清理临时文件
            try:
                os.remove(image_path)
            except:
                pass
            
            # 检查预测结果
            if 'error' in result:
                return jsonify({'code': 500, 'message': f'AI识别失败: {result["error"]}'}), 500
            
            return jsonify({
                'code': 200,
                'message': '识别成功',
                'data': {
                    'dish_name': result['name'],
                    'confidence': round(result.get('confidence', 0) * 100, 2)  # 置信度转换为百分比
                }
            })
            
        except ImportError:
            return jsonify({'code': 500, 'message': 'AI模型未正确安装或配置，请联系管理员'}), 500
        except Exception as e:
            # 确保清理临时文件
            try:
                os.remove(image_path)
            except:
                pass
            return jsonify({'code': 500, 'message': f'AI识别过程中出错: {str(e)}'}), 500
            
    except Exception as e:
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500




# ================== 错误处理 ==================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'code': 404, 'message': '接口不存在'}), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'code': 405, 'message': '请求方法不被允许'}), 405


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'code': 500, 'message': '服务器内部错误'}), 500
