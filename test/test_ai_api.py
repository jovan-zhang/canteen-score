#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI菜品识别接口快速验证脚本
用于验证新增的AI分类接口是否正常工作
"""

import requests
import json
import os
import sys

# 配置
BASE_URL = 'http://localhost:5000/api'
TEST_USERNAME = 'admin'
TEST_PASSWORD = 'admin123'

def test_server_connection():
    """测试服务器连接"""
    try:
        response = requests.get(f'{BASE_URL}/stats/overview', timeout=5)
        print("✓ 服务器连接正常")
        return True
    except requests.exceptions.RequestException as e:
        print(f"✗ 服务器连接失败: {e}")
        return False

def login_and_get_token():
    """登录获取token"""
    try:
        response = requests.post(f'{BASE_URL}/login', json={
            'username': TEST_USERNAME,
            'password': TEST_PASSWORD
        })
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 200:
                token = data['data']['access_token']
                print("✓ 登录成功，获取到token")
                return token
            else:
                print(f"✗ 登录失败: {data.get('message')}")
                return None
        else:
            print(f"✗ 登录请求失败，状态码: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"✗ 登录过程出错: {e}")
        return None

def test_ai_classify_endpoint(token):
    """测试AI分类接口端点"""
    headers = {'Authorization': f'Bearer {token}'}
    
    # 测试无文件的情况
    try:
        response = requests.post(f'{BASE_URL}/classify-dish', headers=headers)
        result = response.json()
        
        if response.status_code == 400 and '请上传图片文件' in result.get('message', ''):
            print("✓ AI分类接口端点正常（正确处理无文件情况）")
            return True
        else:
            print(f"✗ AI分类接口端点异常: {result}")
            return False
            
    except Exception as e:
        print(f"✗ AI分类接口测试出错: {e}")
        return False

def test_ai_suggest_endpoint(token):
    """测试AI分类推荐接口端点"""
    headers = {'Authorization': f'Bearer {token}'}
    
    # 测试无文件的情况
    try:
        response = requests.post(f'{BASE_URL}/classify-and-suggest', headers=headers)
        result = response.json()
        
        if response.status_code == 400 and '请上传图片文件' in result.get('message', ''):
            print("✓ AI分类推荐接口端点正常（正确处理无文件情况）")
            return True
        else:
            print(f"✗ AI分类推荐接口端点异常: {result}")
            return False
            
    except Exception as e:
        print(f"✗ AI分类推荐接口测试出错: {e}")
        return False

def find_test_image():
    """查找可用的测试图片"""
    possible_paths = [
        'static/uploads/7d2b896a-4099-4afa-9a26-fdcac5013f42.jpg',
        'uploads/rice1.jpg',
        'test_image.jpg',
        'static/uploads/dishes/',  # 检查dishes目录
        'static/uploads/canteens/', # 检查canteens目录
    ]
    
    for path in possible_paths:
        if os.path.isfile(path):
            return path
        elif os.path.isdir(path):
            # 如果是目录，查找其中的图片文件
            for file in os.listdir(path):
                if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    return os.path.join(path, file)
    
    return None

def test_ai_with_real_image(token):
    """使用真实图片测试AI接口"""
    test_image = find_test_image()
    
    if not test_image:
        print("⚠ 未找到测试图片，跳过真实图片测试")
        print("  建议：在项目目录下放置一张菜品图片进行测试")
        return
    
    print(f"使用测试图片: {test_image}")
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        with open(test_image, 'rb') as f:
            files = {'image': f}
            response = requests.post(f'{BASE_URL}/classify-dish', 
                                   files=files, headers=headers)
        
        result = response.json()
        print(f"=== AI分类结果 ===")
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print("✓ AI图片分类测试成功")
        else:
            print("⚠ AI图片分类测试有问题，请检查模型文件")
            
    except Exception as e:
        print(f"✗ AI图片分类测试出错: {e}")

def main():
    print("=== AI菜品识别接口验证 ===")
    print()
    
    # 1. 检查服务器连接
    if not test_server_connection():
        print("请确保后端服务正在运行: python run.py")
        return
    
    # 2. 登录获取token
    token = login_and_get_token()
    if not token:
        print("请检查登录凭据或服务器状态")
        return
    
    # 3. 测试AI接口端点
    endpoint1_ok = test_ai_classify_endpoint(token)
    endpoint2_ok = test_ai_suggest_endpoint(token)
    
    if not (endpoint1_ok and endpoint2_ok):
        print("AI接口端点存在问题，请检查routes.py中的新增接口")
        return
    
    # 4. 测试真实图片
    test_ai_with_real_image(token)
    
    print()
    print("=== 验证完成 ===")
    print("✓ 基础接口验证通过")
    print("📝 建议使用Postman进行完整的功能测试")
    print("📖 详细测试说明请参考: test/POSTMAN_测试指南.md")

if __name__ == '__main__':
    main()
