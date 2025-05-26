#!/usr/bin/env python3
"""
测试新增字段的API功能
"""

import requests
import json
from datetime import datetime

# API基础URL
BASE_URL = "http://localhost:3000/api"

def test_create_bookmark_with_new_fields():
    """测试创建包含新字段的收藏"""
    print("🧪 测试创建包含新字段的收藏...")
    
    bookmark_data = {
        "url": "https://example.com/test-article",
        "title": "测试文章 - Chrome插件内容提取",
        "tags": ["测试", "Chrome插件", "内容提取"],
        "note": "这是一个测试收藏，包含提取的文章内容",
        "favicon": "https://example.com/favicon.ico",
        "domain": "example.com",
        "content": "这是完整的文章内容。在现代Web开发中，内容提取是一个常见需求。本文将介绍如何使用Chrome扩展程序来智能提取网页中的文章内容。Chrome扩展程序提供了强大的API，允许我们访问和操作网页内容。",
        "summary": "本文介绍如何使用Chrome扩展程序智能提取网页文章内容，包括技术实现和核心算法。",
        "keywords": ["Chrome扩展", "内容提取", "JavaScript", "DOM解析", "自动化"],
        "type": "bookmark",
        "extracted_at": datetime.now().isoformat()
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/bookmarks",
            json=bookmark_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 创建成功!")
            print(f"   收藏ID: {result['id']}")
            print(f"   标题: {result['title']}")
            print(f"   摘要: {result['summary'][:50]}...")
            print(f"   关键词: {', '.join(result['keywords'])}")
            print(f"   内容长度: {len(result['content'])} 字符")
            return result['id']
        else:
            print(f"❌ 创建失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            try:
                error_detail = response.json()
                print(f"   详细错误: {json.dumps(error_detail, indent=2, ensure_ascii=False)}")
            except:
                pass
            return None
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None

def test_get_bookmark(bookmark_id):
    """测试获取收藏详情"""
    print(f"\n🧪 测试获取收藏详情 (ID: {bookmark_id})...")
    
    try:
        response = requests.get(f"{BASE_URL}/bookmarks/{bookmark_id}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 获取成功!")
            print(f"   标题: {result['title']}")
            print(f"   摘要: {result.get('summary', 'N/A')}")
            print(f"   关键词: {', '.join(result.get('keywords', []))}")
            print(f"   提取时间: {result.get('extracted_at', 'N/A')}")
            return True
        else:
            print(f"❌ 获取失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def test_search_bookmarks():
    """测试搜索功能（包含新字段）"""
    print("\n🧪 测试搜索功能...")
    
    # 测试搜索关键词
    search_terms = ["Chrome扩展", "内容提取", "JavaScript"]
    
    for term in search_terms:
        try:
            response = requests.get(
                f"{BASE_URL}/bookmarks",
                params={"search": term, "page": 1, "page_size": 10}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 搜索 '{term}' 成功!")
                print(f"   找到 {result['pagination']['total']} 条结果")
                
                for bookmark in result['data']:
                    print(f"   - {bookmark['title']}")
            else:
                print(f"❌ 搜索 '{term}' 失败: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 搜索 '{term}' 请求失败: {e}")

def test_update_bookmark(bookmark_id):
    """测试更新收藏的新字段"""
    print(f"\n🧪 测试更新收藏新字段 (ID: {bookmark_id})...")
    
    update_data = {
        "summary": "更新后的文章摘要：详细介绍Chrome插件开发技术",
        "keywords": ["Chrome插件", "Web开发", "前端技术", "自动化工具"],
        "content": "更新后的完整文章内容..."
    }
    
    try:
        response = requests.put(
            f"{BASE_URL}/bookmarks/{bookmark_id}",
            json=update_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 更新成功!")
            print(f"   新摘要: {result['summary']}")
            print(f"   新关键词: {', '.join(result['keywords'])}")
            return True
        else:
            print(f"❌ 更新失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 更新请求失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试新增字段的API功能\n")
    
    # 测试创建
    bookmark_id = test_create_bookmark_with_new_fields()
    
    if bookmark_id:
        # 测试获取
        test_get_bookmark(bookmark_id)
        
        # 测试搜索
        test_search_bookmarks()
        
        # 测试更新
        test_update_bookmark(bookmark_id)
        
        print(f"\n✅ 所有测试完成! 测试收藏ID: {bookmark_id}")
    else:
        print("\n❌ 创建收藏失败，跳过其他测试")

if __name__ == "__main__":
    main() 