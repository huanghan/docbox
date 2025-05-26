#!/usr/bin/env python3
"""
简单的API测试
"""

import requests
import json
from datetime import datetime

# API基础URL
BASE_URL = "http://localhost:3000/api"

def test_create_bookmark():
    """测试创建收藏"""
    print("🧪 测试创建收藏...")
    
    # 模拟Chrome插件发送的数据结构
    bookmark_data = {
        "url": "https://example.com/test-article",
        "title": "测试文章标题",
        "tags": ["测试", "Chrome插件"],
        "note": "这是一个测试收藏",
        "favicon": "https://example.com/favicon.ico",
        "domain": "example.com",
        "content": "这是文章的完整内容...",
        "summary": "这是文章的摘要...",
        "keywords": ["关键词1", "关键词2"],
        "extracted_at": datetime.now().isoformat(),
        "type": "bookmark"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/bookmarks",
            json=bookmark_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 创建成功!")
            print(f"   收藏ID: {result['id']}")
            return result['id']
        else:
            print(f"❌ 创建失败: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"   详细错误: {json.dumps(error_detail, indent=2, ensure_ascii=False)}")
            except:
                pass
            return None
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None

if __name__ == "__main__":
    test_create_bookmark() 