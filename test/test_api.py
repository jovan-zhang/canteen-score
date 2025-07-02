#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API测试脚本
用于测试校园食堂菜品打分系统的各个接口
"""

import requests
import json
import time

BASE_URL = 'http://localhost:5000/api'

def print_response(response, title=""):
    """打印响应信息"""
    print(f"\n{'='*60}")
    if title:
        print(f"测试: {title}")
        print('-'*60)
    print(f"状态码: {response.status_code}")
    try:
        result = response.json()
        print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
    except:
        print(f"响应: {response.text}")
    print('='*60)

def test_user_registration_and_login():
    """测试用户注册和登录"""
    print("\n🔐 测试用户注册和登录")
    
    # 测试用户注册
    register_data = {
        "username": "testuser",
        "password": "123456",
        "nickname": "测试用户"
    }
    
    response = requests.post(f'{BASE_URL}/register', json=register_data)
    print_response(response, "用户注册")
    
    # 测试用户登录
    login_data = {
        "username": "testuser",
        "password": "123456"
    }
    
    response = requests.post(f'{BASE_URL}/login', json=login_data)
    print_response(response, "用户登录")
    
    if response.status_code == 200:
        token = response.json()['data']['token']
        return token
    return None

def test_admin_login():
    """测试管理员登录"""
    print("\n👑 测试管理员登录")
    
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = requests.post(f'{BASE_URL}/login', json=login_data)
    print_response(response, "管理员登录")
    
    if response.status_code == 200:
        token = response.json()['data']['token']
        return token
    return None

def test_get_canteens():
    """测试获取食堂列表"""
    print("\n🏢 测试获取食堂列表")
    
    response = requests.get(f'{BASE_URL}/canteens')
    print_response(response, "获取食堂列表")
    
    if response.status_code == 200:
        canteens = response.json()['data']
        if canteens:
            return canteens[0]['id']
    return None

def test_get_dishes():
    """测试获取菜品列表"""
    print("\n🍽️ 测试获取菜品列表")
    
    response = requests.get(f'{BASE_URL}/dishes')
    print_response(response, "获取菜品列表")
    
    if response.status_code == 200:
        dishes = response.json()['data']['dishes']
        if dishes:
            return dishes[0]['id']
    return None

def test_create_review(token, dish_id):
    """测试创建评价"""
    print("\n⭐ 测试创建菜品评价")
    
    headers = {'Authorization': f'Bearer {token}'}
    review_data = {
        "overall_rating": 4.5,
        "taste_rating": 4.0,
        "portion_rating": 4.5,
        "value_rating": 4.0,
        "service_rating": 4.5,
        "comment": "味道不错，分量充足，服务态度好！"
    }
    
    response = requests.post(f'{BASE_URL}/dishes/{dish_id}/reviews', 
                           json=review_data, headers=headers)
    print_response(response, "创建菜品评价")
    
    if response.status_code == 201:
        return response.json()['data']['id']
    return None

def test_get_reviews(dish_id):
    """测试获取评价列表"""
    print("\n📝 测试获取评价列表")
    
    response = requests.get(f'{BASE_URL}/dishes/{dish_id}/reviews')
    print_response(response, "获取菜品评价列表")

def test_like_review(token, review_id):
    """测试点赞评价"""
    print("\n👍 测试点赞评价")
    
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post(f'{BASE_URL}/reviews/{review_id}/like', headers=headers)
    print_response(response, "点赞评价")

def test_create_reply(token, review_id):
    """测试回复评价"""
    print("\n💬 测试回复评价")
    
    headers = {'Authorization': f'Bearer {token}'}
    reply_data = {
        "content": "谢谢你的评价，我们会继续努力的！"
    }
    
    response = requests.post(f'{BASE_URL}/reviews/{review_id}/replies',
                           json=reply_data, headers=headers)
    print_response(response, "回复评价")

def test_stats():
    """测试统计接口"""
    print("\n📊 测试统计接口")
    
    # 系统概览
    response = requests.get(f'{BASE_URL}/stats/overview')
    print_response(response, "系统概览统计")
    
    # 热门菜品
    response = requests.get(f'{BASE_URL}/stats/popular-dishes?limit=5')
    print_response(response, "热门菜品统计")
    
    # 评分分布
    response = requests.get(f'{BASE_URL}/stats/rating-distribution')
    print_response(response, "评分分布统计")

def test_admin_functions(admin_token):
    """测试管理员功能"""
    print("\n🔧 测试管理员功能")
    
    headers = {'Authorization': f'Bearer {admin_token}'}
    
    # 获取用户列表
    response = requests.get(f'{BASE_URL}/admin/users', headers=headers)
    print_response(response, "管理员获取用户列表")
    
    # 获取详细统计
    response = requests.get(f'{BASE_URL}/admin/stats/detailed', headers=headers)
    print_response(response, "管理员获取详细统计")

def test_user_info(token):
    """测试用户信息接口"""
    print("\n👤 测试用户信息接口")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # 获取用户信息
    response = requests.get(f'{BASE_URL}/user/info', headers=headers)
    print_response(response, "获取用户信息")
    
    # 获取用户评价历史
    response = requests.get(f'{BASE_URL}/user/reviews', headers=headers)
    print_response(response, "获取用户评价历史")

def main():
    """主测试函数"""
    print("🧪 开始API接口测试")
    print(f"测试目标: {BASE_URL}")
    
    try:
        # 1. 测试用户注册和登录
        user_token = test_user_registration_and_login()
        
        # 2. 测试管理员登录
        admin_token = test_admin_login()
        
        # 3. 测试获取食堂列表
        canteen_id = test_get_canteens()
        
        # 4. 测试获取菜品列表
        dish_id = test_get_dishes()
        
        if user_token and dish_id:
            # 5. 测试创建评价
            review_id = test_create_review(user_token, dish_id)
            
            # 6. 测试获取评价列表
            test_get_reviews(dish_id)
            
            # 7. 测试用户信息
            test_user_info(user_token)
            
            if review_id:
                # 8. 测试点赞功能
                test_like_review(user_token, review_id)
                
                # 9. 测试回复功能
                test_create_reply(user_token, review_id)
        
        # 10. 测试统计接口
        test_stats()
        
        # 11. 测试管理员功能
        if admin_token:
            test_admin_functions(admin_token)
        
        print("\n✅ API测试完成！")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ 连接失败！请确保服务器正在运行：")
        print("   python run.py")
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {str(e)}")

if __name__ == '__main__':
    main()
