#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Postman集合验证脚本
验证更新后的AI识别接口配置是否正确
"""

import json
import os

def validate_postman_collection():
    """验证Postman集合文件"""
    collection_path = "postman_collection.json"
    
    if not os.path.exists(collection_path):
        print("❌ Postman集合文件不存在")
        return False
    
    try:
        with open(collection_path, 'r', encoding='utf-8') as f:
            collection = json.load(f)
        
        print("✅ Postman集合文件格式正确")
        
        # 查找AI识别相关的接口
        ai_folder = None
        for item in collection.get("item", []):
            if "AI菜品识别" in item.get("name", ""):
                ai_folder = item
                break
        
        if not ai_folder:
            print("❌ 未找到AI菜品识别文件夹")
            return False
        
        print("✅ 找到AI菜品识别文件夹")
        
        # 检查AI识别接口
        ai_requests = ai_folder.get("item", [])
        
        # 应该只有一个接口（菜品图片识别）
        if len(ai_requests) != 1:
            print(f"⚠️  AI识别接口数量异常: {len(ai_requests)} (期望: 1)")
        
        # 检查接口配置
        classify_request = ai_requests[0]
        request_config = classify_request.get("request", {})
        
        # 检查是否移除了认证
        headers = request_config.get("header", [])
        has_auth = any("Authorization" in header.get("key", "") for header in headers)
        
        if has_auth:
            print("❌ AI识别接口仍包含认证头")
            return False
        else:
            print("✅ AI识别接口已移除认证要求")
        
        # 检查URL
        url_config = request_config.get("url", {})
        path = url_config.get("path", [])
        if path == ["api", "classify-dish"]:
            print("✅ AI识别接口URL配置正确")
        else:
            print(f"❌ AI识别接口URL配置错误: {path}")
            return False
        
        # 检查请求方法
        method = request_config.get("method", "")
        if method == "POST":
            print("✅ AI识别接口请求方法正确")
        else:
            print(f"❌ AI识别接口请求方法错误: {method}")
            return False
        
        # 检查Body配置
        body_config = request_config.get("body", {})
        if body_config.get("mode") == "formdata":
            print("✅ AI识别接口Body格式正确")
        else:
            print(f"❌ AI识别接口Body格式错误: {body_config.get('mode')}")
            return False
        
        # 检查是否有测试脚本
        events = classify_request.get("event", [])
        has_test_script = any(event.get("listen") == "test" for event in events)
        
        if has_test_script:
            print("✅ AI识别接口包含自动化测试脚本")
        else:
            print("⚠️  AI识别接口缺少自动化测试脚本")
        
        # 检查是否有响应示例
        responses = classify_request.get("response", [])
        if responses:
            print(f"✅ AI识别接口包含 {len(responses)} 个响应示例")
        else:
            print("⚠️  AI识别接口缺少响应示例")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Postman集合文件JSON格式错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 验证过程中出错: {e}")
        return False

def validate_environment():
    """验证Postman环境文件"""
    env_path = "postman_environment.json"
    
    if not os.path.exists(env_path):
        print("❌ Postman环境文件不存在")
        return False
    
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            environment = json.load(f)
        
        print("✅ Postman环境文件格式正确")
        
        # 检查必要的环境变量
        values = environment.get("values", [])
        required_vars = ["base_url", "user_token", "admin_token"]
        
        existing_vars = [var.get("key") for var in values]
        
        for var in required_vars:
            if var in existing_vars:
                print(f"✅ 环境变量 {var} 存在")
            else:
                print(f"❌ 环境变量 {var} 缺失")
                return False
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ 环境文件JSON格式错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 验证过程中出错: {e}")
        return False

def generate_test_summary():
    """生成测试摘要"""
    print("\n" + "="*50)
    print("📋 AI识别接口更新摘要")
    print("="*50)
    print("✅ 移除了用户认证要求")
    print("✅ 删除了复杂的推荐功能接口")
    print("✅ 简化了响应格式")
    print("✅ 添加了自动化测试脚本")
    print("✅ 包含了响应示例")
    print("✅ 更新了接口描述")
    
    print("\n📝 主要变更:")
    print("1. POST /api/classify-dish - 无需认证的独立AI识别")
    print("2. 删除了 /api/classify-and-suggest 接口")
    print("3. 响应格式: dish_name + confidence")
    print("4. 支持格式: PNG, JPG, JPEG, GIF")
    
    print("\n🔧 测试建议:")
    print("1. 准备多种菜品图片进行测试")
    print("2. 验证错误处理机制")
    print("3. 检查响应时间和置信度")
    print("4. 测试不同图片格式")

def main():
    """主函数"""
    print("🔍 验证Postman集合配置")
    print("="*30)
    
    # 切换到test目录
    os.chdir(os.path.join(os.path.dirname(__file__)))
    
    collection_valid = validate_postman_collection()
    environment_valid = validate_environment()
    
    print("\n" + "="*30)
    print("📊 验证结果")
    print("="*30)
    
    if collection_valid and environment_valid:
        print("🎉 所有验证通过！Postman集合可以正常使用")
        generate_test_summary()
        return True
    else:
        print("❌ 验证失败，请检查配置文件")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
