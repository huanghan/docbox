"""
分类API接口测试脚本
"""
import requests
import json
from typing import Dict, List, Optional

# API基础URL
BASE_URL = "http://127.0.0.1:8000"
CATEGORY_URL = f"{BASE_URL}/api/categories"
DOCUMENT_URL = f"{BASE_URL}/api/documents"

class CategoryAPITest:
    def __init__(self):
        self.test_uid = 1001  # 测试用户ID
        self.created_categories = []  # 记录创建的分类ID，用于清理
        self.created_documents = []   # 记录创建的文档ID，用于清理
        
    def run_all_tests(self):
        """运行所有测试"""
        print("🧪 开始分类API接口测试...")
        print("=" * 50)
        
        try:
            # 准备测试数据
            self.prepare_test_data()
            
            # 分类管理测试
            self.test_create_category()
            self.test_get_categories()
            self.test_update_category()
            
            # 分类-文档关联测试
            self.test_add_doc_to_category()
            self.test_get_docs_by_category()
            self.test_remove_doc_from_category()
            
            # 删除测试
            self.test_delete_category()
            
            # 错误情况测试
            self.test_error_cases()
            
            print("\n✅ 所有测试完成！")
            
        except Exception as e:
            print(f"\n❌ 测试出现异常: {e}")
        finally:
            # 清理测试数据
            self.cleanup_test_data()
    
    def prepare_test_data(self):
        """准备测试数据 - 创建几个测试文档"""
        print("🔧 准备测试数据...")
        
        test_docs = [
            {
                "uid": self.test_uid,
                "url": "http://example.com/doc1",
                "title": "分类测试文档1",
                "summary": "用于测试分类功能的文档1",
                "content": "这是测试分类功能的文档内容1",
                "source": "test",
                "tags": "test,category",
                "evaluate": 5
            },
            {
                "uid": self.test_uid,
                "url": "http://example.com/doc2", 
                "title": "分类测试文档2",
                "summary": "用于测试分类功能的文档2",
                "content": "这是测试分类功能的文档内容2",
                "source": "test",
                "tags": "test,category",
                "evaluate": 4
            }
        ]
        
        for doc in test_docs:
            response = requests.post(DOCUMENT_URL, json=doc)
            if response.status_code == 200:
                print(f"  ✅ 创建测试文档: {doc['title']}")
                # 获取文档ID（需要通过标题查询）
                doc_response = requests.get(f"{DOCUMENT_URL}?uid={self.test_uid}&limit=10")
                if doc_response.status_code == 200:
                    docs = doc_response.json().get('documents', [])
                    for d in docs:
                        if d['title'] == doc['title']:
                            self.created_documents.append(d['id'])
                            break
            else:
                print(f"  ❌ 创建测试文档失败: {doc['title']}")
        
        print(f"  📝 创建了 {len(self.created_documents)} 个测试文档")
    
    def test_create_category(self):
        """测试创建分类"""
        print("\n📁 测试创建分类...")
        
        test_categories = [
            {
                "uid": self.test_uid,
                "name": "技术文档",
                "tags": "tech,programming",
                "icon": "📚"
            },
            {
                "uid": self.test_uid,
                "name": "学习笔记",
                "tags": "study,notes",
                "icon": "📝"
            },
            {
                "uid": self.test_uid,
                "name": "项目文档",
                "tags": "project,docs",
                "icon": "🚀"
            }
        ]
        
        for category in test_categories:
            response = requests.post(CATEGORY_URL, json=category)
            if response.status_code == 200:
                data = response.json()
                category_id = data.get('category_id')
                self.created_categories.append(category_id)
                print(f"  ✅ 创建分类成功: {category['name']} (ID: {category_id})")
            else:
                print(f"  ❌ 创建分类失败: {category['name']} - {response.text}")
    
    def test_get_categories(self):
        """测试获取分类列表"""
        print("\n📋 测试获取分类列表...")
        
        response = requests.get(f"{CATEGORY_URL}?uid={self.test_uid}")
        if response.status_code == 200:
            data = response.json()
            categories = data.get('categories', [])
            count = data.get('count', 0)
            
            print(f"  ✅ 获取分类列表成功: {count} 个分类")
            for category in categories:
                print(f"     - {category['name']} (ID: {category['id']}, 标签: {category['tags']})")
        else:
            print(f"  ❌ 获取分类列表失败: {response.text}")
    
    def test_update_category(self):
        """测试修改分类"""
        print("\n✏️ 测试修改分类...")
        
        if not self.created_categories:
            print("  ⚠️ 没有可修改的分类")
            return
        
        category_id = self.created_categories[0]
        update_data = {
            "name": "技术文档（已更新）",
            "tags": "tech,programming,updated",
            "icon": "📖"
        }
        
        response = requests.put(f"{CATEGORY_URL}/{category_id}?uid={self.test_uid}", json=update_data)
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ 修改分类成功: {data.get('message')}")
            
            # 验证修改结果
            verify_response = requests.get(f"{CATEGORY_URL}?uid={self.test_uid}")
            if verify_response.status_code == 200:
                categories = verify_response.json().get('categories', [])
                for category in categories:
                    if category['id'] == category_id:
                        print(f"  ✅ 验证修改结果: {category['name']} - {category['tags']}")
                        break
        else:
            print(f"  ❌ 修改分类失败: {response.text}")
    
    def test_add_doc_to_category(self):
        """测试给分类添加文档"""
        print("\n📄 测试给分类添加文档...")
        
        if not self.created_categories or not self.created_documents:
            print("  ⚠️ 缺少测试数据")
            return
        
        category_id = self.created_categories[0]
        
        # 给分类添加多个文档
        for doc_id in self.created_documents:
            add_data = {"doc_id": doc_id}
            response = requests.post(f"{CATEGORY_URL}/{category_id}/docs", json=add_data)
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ 添加文档成功: 文档ID {doc_id} -> 分类ID {category_id}")
            else:
                print(f"  ❌ 添加文档失败: 文档ID {doc_id} - {response.text}")
    
    def test_get_docs_by_category(self):
        """测试获取分类下的文档"""
        print("\n📚 测试获取分类下的文档...")
        
        if not self.created_categories:
            print("  ⚠️ 没有可查询的分类")
            return
        
        category_id = self.created_categories[0]
        response = requests.get(f"{CATEGORY_URL}/{category_id}/docs?limit=10&offset=0")
        if response.status_code == 200:
            data = response.json()
            documents = data.get('documents', [])
            count = data.get('count', 0)
            
            print(f"  ✅ 获取分类文档成功: 分类ID {category_id} 包含 {count} 个文档")
            for doc in documents:
                print(f"     - {doc['title']} (ID: {doc['id']})")
        else:
            print(f"  ❌ 获取分类文档失败: {response.text}")
    
    def test_remove_doc_from_category(self):
        """测试从分类中移除文档"""
        print("\n🗑️ 测试从分类中移除文档...")
        
        if not self.created_categories or not self.created_documents:
            print("  ⚠️ 缺少测试数据")
            return
        
        category_id = self.created_categories[0]
        doc_id = self.created_documents[0]
        
        response = requests.delete(f"{CATEGORY_URL}/{category_id}/docs/{doc_id}")
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ 移除文档成功: {data.get('message')}")
            
            # 验证移除结果
            verify_response = requests.get(f"{CATEGORY_URL}/{category_id}/docs")
            if verify_response.status_code == 200:
                remaining_count = verify_response.json().get('count', 0)
                print(f"  ✅ 验证移除结果: 分类中还剩 {remaining_count} 个文档")
        else:
            print(f"  ❌ 移除文档失败: {response.text}")
    
    def test_delete_category(self):
        """测试删除分类"""
        print("\n🗑️ 测试删除分类...")
        
        if len(self.created_categories) < 2:
            print("  ⚠️ 需要至少2个分类进行测试")
            return
        
        # 删除最后一个分类
        category_id = self.created_categories[-1]
        response = requests.delete(f"{CATEGORY_URL}/{category_id}?uid={self.test_uid}")
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ 删除分类成功: {data.get('message')}")
            self.created_categories.remove(category_id)
            
            # 验证删除结果
            verify_response = requests.get(f"{CATEGORY_URL}?uid={self.test_uid}")
            if verify_response.status_code == 200:
                remaining_count = verify_response.json().get('count', 0)
                print(f"  ✅ 验证删除结果: 用户还剩 {remaining_count} 个分类")
        else:
            print(f"  ❌ 删除分类失败: {response.text}")
    
    def test_error_cases(self):
        """测试错误情况"""
        print("\n⚠️ 测试错误情况...")
        
        # 测试不存在的分类
        response = requests.get(f"{CATEGORY_URL}/99999/docs")
        print(f"  🔍 访问不存在的分类: {response.status_code}")
        
        # 测试无权限操作
        if self.created_categories:
            wrong_uid = 9999
            category_id = self.created_categories[0]
            response = requests.delete(f"{CATEGORY_URL}/{category_id}?uid={wrong_uid}")
            print(f"  🔍 无权限删除分类: {response.status_code}")
        
        # 测试无效的请求数据
        invalid_data = {"uid": "invalid", "name": ""}
        response = requests.post(CATEGORY_URL, json=invalid_data)
        print(f"  🔍 无效请求数据: {response.status_code}")
        
        # 测试空的更新请求
        if self.created_categories:
            category_id = self.created_categories[0]
            response = requests.put(f"{CATEGORY_URL}/{category_id}?uid={self.test_uid}", json={})
            print(f"  🔍 空的更新请求: {response.status_code}")
    
    def cleanup_test_data(self):
        """清理测试数据"""
        print("\n🧹 清理测试数据...")
        
        # 清理分类
        for category_id in self.created_categories:
            response = requests.delete(f"{CATEGORY_URL}/{category_id}?uid={self.test_uid}")
            if response.status_code == 200:
                print(f"  ✅ 清理分类: ID {category_id}")
            else:
                print(f"  ❌ 清理分类失败: ID {category_id}")
        
        # 清理文档
        for doc_id in self.created_documents:
            response = requests.delete(f"{DOCUMENT_URL}/id/{doc_id}")
            if response.status_code == 200:
                print(f"  ✅ 清理文档: ID {doc_id}")
            else:
                print(f"  ❌ 清理文档失败: ID {doc_id}")
        
        print("  🎉 测试数据清理完成")

def main():
    """主函数"""
    print("🚀 分类API接口测试工具")
    print("请确保API服务正在运行: http://127.0.0.1:8000")
    print("=" * 50)
    
    # 检查API服务是否可用
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API服务连接正常")
        else:
            print("❌ API服务连接失败")
            return
    except Exception as e:
        print(f"❌ 无法连接到API服务: {e}")
        print("请确保服务已启动并运行在 http://127.0.0.1:8000")
        return
    
    # 运行测试
    tester = CategoryAPITest()
    tester.run_all_tests()

if __name__ == "__main__":
    main() 