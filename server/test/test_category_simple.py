"""
分类API快速测试脚本 - 简化版
"""
import requests
import json

# 配置
BASE_URL = "http://127.0.0.1:8000"
TEST_UID = 1001

def test_category_basic_operations():
    """测试分类基本操作"""
    print("🧪 分类API基本操作测试")
    print("=" * 40)
    
    # 1. 创建分类
    print("\n1️⃣ 创建分类")
    create_data = {
        "uid": TEST_UID,
        "name": "快速测试分类",
        "tags": "test,quick",
        "icon": "🚀"
    }
    
    response = requests.post(f"{BASE_URL}/api/categories", json=create_data)
    if response.status_code == 200:
        result = response.json()
        category_id = result.get('category_id')
        print(f"✅ 创建成功，分类ID: {category_id}")
    else:
        print(f"❌ 创建失败: {response.text}")
        return
    
    # 2. 获取分类列表
    print("\n2️⃣ 获取分类列表")
    response = requests.get(f"{BASE_URL}/api/categories?uid={TEST_UID}")
    if response.status_code == 200:
        result = response.json()
        categories = result.get('categories', [])
        print(f"✅ 获取成功，共 {len(categories)} 个分类:")
        for cat in categories:
            print(f"   - {cat['name']} (ID: {cat['id']})")
    else:
        print(f"❌ 获取失败: {response.text}")
    
    # 3. 修改分类
    print("\n3️⃣ 修改分类")
    update_data = {
        "name": "快速测试分类（已修改）",
        "tags": "test,quick,updated"
    }
    
    response = requests.put(f"{BASE_URL}/api/categories/{category_id}?uid={TEST_UID}", json=update_data)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 修改成功: {result.get('message')}")
    else:
        print(f"❌ 修改失败: {response.text}")
    
    # 4. 创建测试文档
    print("\n4️⃣ 创建测试文档")
    doc_data = {
        "uid": TEST_UID,
        "url": "http://test.com/doc",
        "title": "分类测试文档",
        "summary": "用于测试分类功能",
        "content": "这是测试内容"
    }
    
    response = requests.post(f"{BASE_URL}/api/documents", json=doc_data)
    if response.status_code == 200:
        print("✅ 文档创建成功")
        
        # 获取文档ID
        doc_response = requests.get(f"{BASE_URL}/api/documents?uid={TEST_UID}&limit=5")
        if doc_response.status_code == 200:
            docs = doc_response.json().get('documents', [])
            doc_id = None
            for doc in docs:
                if doc['title'] == "分类测试文档":
                    doc_id = doc['id']
                    break
            
            if doc_id:
                print(f"   文档ID: {doc_id}")
                
                # 5. 添加文档到分类
                print("\n5️⃣ 添加文档到分类")
                add_data = {"doc_id": doc_id}
                response = requests.post(f"{BASE_URL}/api/categories/{category_id}/docs", json=add_data)
                if response.status_code == 200:
                    print("✅ 添加文档到分类成功")
                    
                    # 6. 查看分类下的文档
                    print("\n6️⃣ 查看分类下的文档")
                    response = requests.get(f"{BASE_URL}/api/categories/{category_id}/docs")
                    if response.status_code == 200:
                        result = response.json()
                        docs = result.get('documents', [])
                        print(f"✅ 分类包含 {len(docs)} 个文档:")
                        for doc in docs:
                            print(f"   - {doc['title']}")
                    
                    # 清理：删除文档
                    requests.delete(f"{BASE_URL}/api/documents/id/{doc_id}")
                    print(f"🧹 清理文档: {doc_id}")
                else:
                    print(f"❌ 添加文档失败: {response.text}")
    else:
        print(f"❌ 文档创建失败: {response.text}")
    
    # 7. 删除分类
    print("\n7️⃣ 删除分类")
    response = requests.delete(f"{BASE_URL}/api/categories/{category_id}?uid={TEST_UID}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 删除成功: {result.get('message')}")
    else:
        print(f"❌ 删除失败: {response.text}")
    
    print("\n🎉 测试完成！")

def test_error_handling():
    """测试错误处理"""
    print("\n⚠️ 错误处理测试")
    print("=" * 40)
    
    # 测试访问不存在的分类
    response = requests.get(f"{BASE_URL}/api/categories/99999/docs")
    print(f"1. 访问不存在的分类: HTTP {response.status_code}")
    
    # 测试无效数据
    invalid_data = {"uid": "invalid"}
    response = requests.post(f"{BASE_URL}/api/categories", json=invalid_data)
    print(f"2. 无效数据创建分类: HTTP {response.status_code}")
    
    # 测试空的更新
    response = requests.put(f"{BASE_URL}/api/categories/1?uid={TEST_UID}", json={})
    print(f"3. 空数据更新分类: HTTP {response.status_code}")
    
    print("✅ 错误处理测试完成")

if __name__ == "__main__":
    print("🚀 分类API快速测试")
    print("请确保API服务运行在: http://127.0.0.1:8000")
    
    # 检查服务状态
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=3)
        if response.status_code == 200:
            print("✅ API服务正常")
            test_category_basic_operations()
            test_error_handling()
        else:
            print("❌ API服务异常")
    except Exception as e:
        print(f"❌ 无法连接API服务: {e}")
        print("请先启动API服务: python start.py") 