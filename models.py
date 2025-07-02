#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库模型定义
"""

from app import db
from datetime import datetime
import json

class User(db.Model):
    """用户表"""
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    nickname = db.Column(db.String(50), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    avatar = db.Column(db.String(255))
    role = db.Column(db.Enum('student', 'admin'), default='student')
    status = db.Column(db.Enum('active', 'banned'), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    reviews = db.relationship('Review', backref='user', lazy=True)
    replies = db.relationship('ReviewReply', backref='user', lazy=True)
    likes = db.relationship('Like', backref='user', lazy=True)
    
    @property
    def id(self):
        """为兼容性提供id属性"""
        return self.user_id
    
    @property
    def is_admin(self):
        """为兼容性提供is_admin属性"""
        return self.role == 'admin'
    
    def to_dict(self):
        return {
            'userId': self.user_id,
            'username': self.username,
            'nickname': self.nickname,
            'avatar': self.avatar,
            'role': self.role,
            'status': self.status,
            'registerTime': self.created_at.isoformat() if self.created_at else None
        }


class Canteen(db.Model):
    """食堂表"""
    __tablename__ = 'canteens'
    
    canteen_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    business_hours = db.Column(db.String(100))
    contact = db.Column(db.String(20))  # 修正字段名
    description = db.Column(db.Text)
    _images_text = db.Column('images', db.Text)  # JSON格式存储图片URL数组
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    windows = db.relationship('Window', backref='canteen', lazy=True)
    
    @property
    def id(self):
        """为兼容性提供id属性"""
        return self.canteen_id
    
    @property
    def images(self):
        """获取图片列表"""
        if hasattr(self, '_images_text') and self._images_text:
            try:
                return json.loads(self._images_text)
            except (json.JSONDecodeError, TypeError):
                return []
        return []
    
    @images.setter
    def images(self, value):
        """设置图片列表"""
        if value is None:
            self._images_text = None
        elif isinstance(value, list):
            self._images_text = json.dumps(value)
        elif isinstance(value, str):
            self._images_text = value
        else:
            self._images_text = json.dumps([])
    
    def get_images(self):
        return self.images
    
    def set_images(self, image_list):
        self.images = image_list
    
    def get_average_rating(self):
        """计算食堂平均评分"""
        from sqlalchemy import func
        result = db.session.query(func.avg(Review.overall_rating)).join(Dish).join(Window).filter(
            Window.canteen_id == self.canteen_id,
            Review.overall_rating.isnot(None)
        ).scalar()
        return round(float(result), 1) if result else 0.0
    
    def get_review_count(self):
        """获取评分总数"""
        return db.session.query(Review).join(Dish).join(Window).filter(
            Window.canteen_id == self.canteen_id,
            Review.overall_rating.isnot(None)
        ).count()
    
    def to_dict(self):
        return {
            'canteenId': self.canteen_id,
            'name': self.name,
            'location': self.location,
            'businessHours': self.business_hours,
            'phone': self.phone,
            'description': self.description,
            'images': self.get_images(),
            'avgRating': self.get_avg_rating(),
            'ratingCount': self.get_rating_count()
        }


class Window(db.Model):
    """窗口表"""
    __tablename__ = 'windows'
    
    window_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    canteen_id = db.Column(db.Integer, db.ForeignKey('canteens.canteen_id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    business_hours = db.Column(db.String(100))
    _images_text = db.Column('images', db.Text)  # JSON格式存储图片URL数组
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    dishes = db.relationship('Dish', backref='window', lazy=True)
    
    @property
    def id(self):
        """为兼容性提供id属性"""
        return self.window_id
    
    @property
    def images(self):
        """获取图片列表"""
        if hasattr(self, '_images_text') and self._images_text:
            try:
                return json.loads(self._images_text)
            except (json.JSONDecodeError, TypeError):
                return []
        return []
    
    @images.setter
    def images(self, value):
        """设置图片列表"""
        if value is None:
            self._images_text = None
        elif isinstance(value, list):
            self._images_text = json.dumps(value)
        elif isinstance(value, str):
            self._images_text = value
        else:
            self._images_text = json.dumps([])
    
    def get_images(self):
        return self.images
    
    def set_images(self, image_list):
        self.images = image_list
    
    def get_average_rating(self):
        """计算窗口平均评分"""
        from sqlalchemy import func
        result = db.session.query(func.avg(Review.overall_rating)).join(Dish).filter(
            Dish.window_id == self.window_id,
            Review.overall_rating.isnot(None)
        ).scalar()
        return round(float(result), 1) if result else 0.0
    
    def get_review_count(self):
        """获取评分总数"""
        return db.session.query(Review).join(Dish).filter(
            Dish.window_id == self.window_id,
            Review.overall_rating.isnot(None)
        ).count()
    
    def get_dish_count(self):
        """获取菜品数量"""
        return len(self.dishes)
    
    def to_dict(self):
        return {
            'windowId': self.window_id,
            'canteenId': self.canteen_id,
            'canteenName': self.canteen.name if self.canteen else None,
            'name': self.name,
            'description': self.description,
            'businessHours': self.business_hours,
            'images': self.get_images(),
            'avgRating': self.get_avg_rating(),
            'ratingCount': self.get_rating_count(),
            'dishCount': self.get_dish_count()
        }


class Dish(db.Model):
    """菜品表"""
    __tablename__ = 'dishes'
    
    dish_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    window_id = db.Column(db.Integer, db.ForeignKey('windows.window_id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Numeric(8, 2), nullable=False)
    category = db.Column(db.String(50))  # 添加分类字段
    description = db.Column(db.Text)
    _images_text = db.Column('images', db.Text)  # JSON格式存储图片URL数组
    is_available = db.Column(db.Boolean, default=True)  # 是否可用
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    reviews = db.relationship('Review', backref='dish', lazy=True)
    
    @property
    def id(self):
        """为兼容性提供id属性"""
        return self.dish_id
    
    @property
    def images(self):
        """获取图片列表"""
        if hasattr(self, '_images_text') and self._images_text:
            try:
                return json.loads(self._images_text)
            except (json.JSONDecodeError, TypeError):
                return []
        return []
    
    @images.setter
    def images(self, value):
        """设置图片列表"""
        if value is None:
            self._images_text = None
        elif isinstance(value, list):
            self._images_text = json.dumps(value)
        elif isinstance(value, str):
            self._images_text = value
        else:
            self._images_text = json.dumps([])
    
    def get_images(self):
        return self.images
    
    def set_images(self, image_list):
        self.images = image_list
    
    def get_average_rating(self):
        """计算菜品平均评分"""
        from sqlalchemy import func
        result = db.session.query(func.avg(Review.overall_rating)).filter(
            Review.dish_id == self.dish_id,
            Review.overall_rating.isnot(None)
        ).scalar()
        return round(float(result), 1) if result else 0.0
    
    def get_review_count(self):
        """获取评分总数"""
        return db.session.query(Review).filter(
            Review.dish_id == self.dish_id,
            Review.overall_rating.isnot(None)
        ).count()
    
    def get_rating_stats(self):
        """获取评分统计"""
        from sqlalchemy import func
        
        # 各评分维度平均值
        taste = db.session.query(func.avg(Review.taste_rating)).filter(
            Review.dish_id == self.dish_id,
            Review.taste_rating.isnot(None)
        ).scalar()
        
        portion = db.session.query(func.avg(Review.portion_rating)).filter(
            Review.dish_id == self.dish_id,
            Review.portion_rating.isnot(None)
        ).scalar()
        
        value = db.session.query(func.avg(Review.value_rating)).filter(
            Review.dish_id == self.dish_id,
            Review.value_rating.isnot(None)
        ).scalar()
        
        service = db.session.query(func.avg(Review.service_rating)).filter(
            Review.dish_id == self.dish_id,
            Review.service_rating.isnot(None)
        ).scalar()
        
        return {
            'taste': round(float(taste), 1) if taste else 0.0,
            'portion': round(float(portion), 1) if portion else 0.0,
            'value': round(float(value), 1) if value else 0.0,
            'service': round(float(service), 1) if service else 0.0,
        }

    
    def get_rating_distribution(self):
        """获取评分分布"""
        from sqlalchemy import func
        
        distribution = {}
        for i in range(1, 6):
            count = db.session.query(Review).filter(
                Review.dish_id == self.dish_id,
                Review.overall_rating == i
            ).count()
            distribution[str(i)] = count
        
        return distribution
    
    def to_dict(self):
        return {
            'dishId': self.dish_id,
            'windowId': self.window_id,
            'windowName': self.window.name if self.window else None,
            'canteenId': self.window.canteen_id if self.window else None,
            'canteenName': self.window.canteen.name if self.window and self.window.canteen else None,
            'name': self.name,
            'price': float(self.price),
            'description': self.description,
            'images': self.get_images(),
            'tags': self.get_tags(),
            'nutrition': self.get_nutrition(),
            'status': self.status,
            'avgRating': self.get_avg_rating(),
            'ratingCount': self.get_rating_count(),
            'ratingDetail': self.get_rating_detail(),
            'ratingDistribution': self.get_rating_distribution()
        }


class Review(db.Model):
    """评价表（合并评分和评论）"""
    __tablename__ = 'reviews'
    
    review_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    dish_id = db.Column(db.Integer, db.ForeignKey('dishes.dish_id'), nullable=False)
    
    # 评分部分（可选）
    overall_rating = db.Column(db.Integer)
    taste_rating = db.Column(db.Integer)
    portion_rating = db.Column(db.Integer)
    value_rating = db.Column(db.Integer)
    service_rating = db.Column(db.Integer)
    
    # 评论部分（可选）
    content = db.Column(db.Text)
    _images_text = db.Column('images', db.Text)  # JSON格式存储图片URL数组
    likes = db.Column(db.Integer, default=0)
    status = db.Column(db.Enum('published', 'hidden', 'deleted'), default='published')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 唯一约束
    __table_args__ = (db.UniqueConstraint('user_id', 'dish_id'),)
    
    # 关联关系
    replies = db.relationship('ReviewReply', backref='review', lazy=True)
    review_likes = db.relationship('Like', backref='review', lazy=True)
    
    @property
    def id(self):
        """为兼容性提供id属性"""
        return self.review_id
    
    @property
    def images(self):
        """获取图片列表"""
        if hasattr(self, '_images_text') and self._images_text:
            try:
                return json.loads(self._images_text)
            except (json.JSONDecodeError, TypeError):
                return []
        return []
    
    @images.setter
    def images(self, value):
        """设置图片列表"""
        if value is None:
            self._images_text = None
        elif isinstance(value, list):
            self._images_text = json.dumps(value)
        elif isinstance(value, str):
            self._images_text = value
        else:
            self._images_text = json.dumps([])
    
    @property
    def like_count(self):
        """获取点赞数"""
        return len(self.review_likes)
    
    @property 
    def reply_count(self):
        """获取回复数"""
        return len(self.replies)
    
    def get_likes_count(self):
        """获取点赞数"""
        return len(self.review_likes)
    
    def is_liked_by_user(self, user_id):
        """检查用户是否已点赞"""
        return Like.query.filter_by(user_id=user_id, review_id=self.review_id).first() is not None
    
    def to_dict(self, current_user_id=None):
        return {
            'reviewId': self.review_id,
            'userId': self.user_id,
            'userNickname': self.user.nickname if self.user else None,
            'userAvatar': self.user.avatar if self.user else None,
            'rating': {
                'overall': self.overall_rating,
                'taste': self.taste_rating,
                'portion': self.portion_rating,
                'value': self.value_rating,
                'service': self.service_rating
            },
            'content': self.content,
            'images': self.images,
            'likes': self.get_likes_count(),
            'isLiked': self.is_liked_by_user(current_user_id) if current_user_id else False,
            'createTime': self.created_at.isoformat() if self.created_at else None,
            'replies': [reply.to_dict() for reply in self.replies]
        }


class ReviewReply(db.Model):
    """评价回复表"""
    __tablename__ = 'review_replies'
    
    reply_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    review_id = db.Column(db.Integer, db.ForeignKey('reviews.review_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def id(self):
        """为兼容性提供id属性"""
        return self.reply_id
    
    def to_dict(self):
        return {
            'replyId': self.reply_id,
            'userId': self.user_id,
            'userNickname': self.user.nickname if self.user else None,
            'content': self.content,
            'createTime': self.created_at.isoformat() if self.created_at else None
        }


class Like(db.Model):
    """点赞表"""
    __tablename__ = 'likes'
    
    like_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    review_id = db.Column(db.Integer, db.ForeignKey('reviews.review_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 唯一约束
    __table_args__ = (db.UniqueConstraint('user_id', 'review_id'),)
    
    @property
    def id(self):
        """为兼容性提供id属性"""
        return self.like_id
