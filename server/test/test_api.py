"""
API接口测试脚本
"""
import requests
import json
import time
from typing import Dict, Any

class APITester:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.created_doc_ids = []  # 记录创建的文档ID，用于清理
        
    def log(self, message: str, level: str = "INFO"):
        """日志输出"""
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def test_health_check(self):
        """测试健康检查接口"""
        self.log("🔸 测试健康检查接口...")
        
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ 健康检查成功: {data}")
                return True
            else:
                self.log(f"❌ 健康检查失败: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ 健康检查异常: {e}", "ERROR")
            return False
    
    def test_root_endpoint(self):
        """测试根路径接口"""
        self.log("🔸 测试根路径接口...")
        
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ 根路径访问成功: {data['message']}")
                return True
            else:
                self.log(f"❌ 根路径访问失败: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ 根路径访问异常: {e}", "ERROR")
            return False
    
    def test_create_document(self) -> Dict[str, Any]:
        """测试创建文档接口"""
        self.log("🔸 测试创建文档接口...")
        
        test_docs = [
            {
                "uid": 1,
                "title": "API测试文档1",
                "summary": "这是第一个API测试文档",
                "content": "详细的文档内容，包含各种信息和数据。",
                "source": "api_test",
                "tags": "test,api,document",
                "evaluate": 5
            },
            {
                "uid": 1,
                "title": "API测试文档2",
                "summary": "这是第二个API测试文档",
                "content": "另一个测试文档的内容，用于验证API功能。",
                "source": "api_test",
                "tags": "test,api,second",
                "evaluate": 4
            },
            {
                "uid": 2,
                "title": "用户2的测试文档",
                "summary": "用户2创建的测试文档",
                "content": "不同用户的文档内容，用于测试用户隔离功能。",
                "source": "user_test",
                "tags": "test,user2,isolation",
                "evaluate": 3
            }
        ]
        
        created_docs = []
        
        for doc_data in test_docs:
            try:
                response = self.session.post(
                    f"{self.base_url}/api/documents",
                    json=doc_data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    self.log(f"✅ 创建文档成功: {doc_data['title']}")
                    created_docs.append(doc_data)
                else:
                    self.log(f"❌ 创建文档失败: {doc_data['title']} - {response.status_code}", "ERROR")
                    if response.text:
                        self.log(f"   错误详情: {response.text}", "ERROR")
                        
            except Exception as e:
                self.log(f"❌ 创建文档异常: {doc_data['title']} - {e}", "ERROR")
        
        return {"created_docs": created_docs}
    
    def test_get_document_by_id(self, doc_id: int = None):
        """测试根据ID获取文档"""
        self.log("🔸 测试根据ID获取文档...")
        
        # 如果没有指定ID，先获取文档列表找一个ID
        if doc_id is None:
            docs_response = self.session.get(f"{self.base_url}/api/documents?limit=1")
            if docs_response.status_code == 200:
                docs_data = docs_response.json()
                if docs_data["documents"]:
                    doc_id = docs_data["documents"][0]["id"]
                else:
                    self.log("❌ 没有找到可用的文档ID", "ERROR")
                    return False
            else:
                self.log("❌ 获取文档列表失败", "ERROR")
                return False
        
        try:
            response = self.session.get(f"{self.base_url}/api/documents/id/{doc_id}")
            
            if response.status_code == 200:
                doc = response.json()
                self.log(f"✅ 获取文档成功: ID={doc_id}, 标题={doc['title']}")
                return doc
            elif response.status_code == 404:
                self.log(f"⚠️ 文档不存在: ID={doc_id}")
                return None
            else:
                self.log(f"❌ 获取文档失败: ID={doc_id} - {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ 获取文档异常: ID={doc_id} - {e}", "ERROR")
            return False
    
    def test_list_documents(self):
        """测试列出文档接口"""
        self.log("🔸 测试列出文档接口...")
        
        test_cases = [
            {"params": {}, "desc": "获取所有文档"},
            {"params": {"limit": 2}, "desc": "限制数量"},
            {"params": {"uid": 1}, "desc": "按用户过滤"},
            {"params": {"limit": 1, "offset": 1}, "desc": "分页查询"},
        ]
        
        for case in test_cases:
            try:
                response = self.session.get(
                    f"{self.base_url}/api/documents",
                    params=case["params"]
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.log(f"✅ {case['desc']}: 返回{data['count']}条文档")
                else:
                    self.log(f"❌ {case['desc']}失败: {response.status_code}", "ERROR")
                    
            except Exception as e:
                self.log(f"❌ {case['desc']}异常: {e}", "ERROR")
    
    def test_search_documents(self):
        """测试搜索文档接口"""
        self.log("🔸 测试搜索文档接口...")
        
        search_cases = [
            {"keyword": "测试", "desc": "搜索'测试'"},
            {"keyword": "API", "desc": "搜索'API'"},
            {"keyword": "不存在的内容", "desc": "搜索不存在的内容"},
        ]
        
        for case in search_cases:
            try:
                response = self.session.get(
                    f"{self.base_url}/api/documents/search",
                    params={"keyword": case["keyword"]}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.log(f"✅ {case['desc']}: 找到{data['count']}条结果")
                else:
                    self.log(f"❌ {case['desc']}失败: {response.status_code}", "ERROR")
                    
            except Exception as e:
                self.log(f"❌ {case['desc']}异常: {e}", "ERROR")
    
    def test_get_documents_by_tag(self):
        """测试根据标签获取文档"""
        self.log("🔸 测试根据标签获取文档...")
        
        tag_cases = [
            {"tag": "test", "desc": "获取'test'标签文档"},
            {"tag": "api", "desc": "获取'api'标签文档"},
            {"tag": "nonexistent", "desc": "获取不存在标签文档"},
        ]
        
        for case in tag_cases:
            try:
                response = self.session.get(
                    f"{self.base_url}/api/documents/tags/{case['tag']}"
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.log(f"✅ {case['desc']}: 找到{data['count']}条文档")
                else:
                    self.log(f"❌ {case['desc']}失败: {response.status_code}", "ERROR")
                    
            except Exception as e:
                self.log(f"❌ {case['desc']}异常: {e}", "ERROR")
    
    def test_update_document(self):
        """测试更新文档接口"""
        self.log("🔸 测试更新文档接口...")
        
        # 先获取一个文档ID
        docs_response = self.session.get(f"{self.base_url}/api/documents?limit=1")
        if docs_response.status_code != 200:
            self.log("❌ 无法获取文档列表进行更新测试", "ERROR")
            return False
        
        docs_data = docs_response.json()
        if not docs_data["documents"]:
            self.log("❌ 没有可用文档进行更新测试", "ERROR")
            return False
        
        doc_id = docs_data["documents"][0]["id"]
        original_title = docs_data["documents"][0]["title"]
        
        # 更新文档
        update_data = {
            "summary": "已更新的摘要内容",
            "evaluate": 5,
            "tags": "updated,test,modified"
        }
        
        try:
            response = self.session.put(
                f"{self.base_url}/api/documents/id/{doc_id}",
                json=update_data
            )
            
            if response.status_code == 200:
                result = response.json()
                self.log(f"✅ 更新文档成功: ID={doc_id}")
                
                # 验证更新
                updated_doc = self.test_get_document_by_id(doc_id)
                if updated_doc and updated_doc["summary"] == update_data["summary"]:
                    self.log("✅ 更新验证成功")
                    return True
                else:
                    self.log("❌ 更新验证失败", "ERROR")
                    return False
            else:
                self.log(f"❌ 更新文档失败: ID={doc_id} - {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ 更新文档异常: ID={doc_id} - {e}", "ERROR")
            return False
    
    def test_delete_document(self):
        """测试删除文档接口"""
        self.log("🔸 测试删除文档接口...")
        
        # 先创建一个临时文档用于删除测试
        temp_doc = {
            "uid": 999,
            "title": "临时删除测试文档",
            "summary": "用于测试删除功能的临时文档",
            "content": "这个文档将被删除",
            "source": "delete_test",
            "tags": "temp,delete,test",
            "evaluate": 1
        }
        
        # 创建临时文档
        create_response = self.session.post(
            f"{self.base_url}/api/documents",
            json=temp_doc
        )
        
        if create_response.status_code != 200:
            self.log("❌ 无法创建临时文档进行删除测试", "ERROR")
            return False
        
        # 获取创建的文档ID
        docs_response = self.session.get(
            f"{self.base_url}/api/documents/search",
            params={"keyword": "临时删除测试文档"}
        )
        
        if docs_response.status_code != 200:
            self.log("❌ 无法找到临时文档", "ERROR")
            return False
        
        search_data = docs_response.json()
        if not search_data["results"]:
            self.log("❌ 临时文档未找到", "ERROR")
            return False
        
        doc_id = search_data["results"][0]["id"]
        
        # 删除文档
        try:
            response = self.session.delete(f"{self.base_url}/api/documents/id/{doc_id}")
            
            if response.status_code == 200:
                result = response.json()
                self.log(f"✅ 删除文档成功: ID={doc_id}")
                
                # 验证删除
                verify_response = self.session.get(f"{self.base_url}/api/documents/id/{doc_id}")
                if verify_response.status_code == 404:
                    self.log("✅ 删除验证成功")
                    return True
                else:
                    self.log("❌ 删除验证失败", "ERROR")
                    return False
            else:
                self.log(f"❌ 删除文档失败: ID={doc_id} - {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ 删除文档异常: ID={doc_id} - {e}", "ERROR")
            return False
    
    def test_error_cases(self):
        """测试错误情况"""
        self.log("🔸 测试错误情况...")
        
        error_cases = [
            {
                "desc": "获取不存在的文档",
                "method": "GET",
                "url": f"{self.base_url}/api/documents/id/99999",
                "expected_status": 404
            },
            {
                "desc": "删除不存在的文档",
                "method": "DELETE", 
                "url": f"{self.base_url}/api/documents/id/99999",
                "expected_status": 404
            },
            {
                "desc": "更新不存在的文档",
                "method": "PUT",
                "url": f"{self.base_url}/api/documents/id/99999",
                "json": {"summary": "test"},
                "expected_status": 404
            },
            {
                "desc": "创建文档缺少必需字段",
                "method": "POST",
                "url": f"{self.base_url}/api/documents",
                "json": {"title": "test"},  # 缺少必需字段
                "expected_status": 422
            }
        ]
        
        for case in error_cases:
            try:
                if case["method"] == "GET":
                    response = self.session.get(case["url"])
                elif case["method"] == "DELETE":
                    response = self.session.delete(case["url"])
                elif case["method"] == "PUT":
                    response = self.session.put(case["url"], json=case.get("json", {}))
                elif case["method"] == "POST":
                    response = self.session.post(case["url"], json=case.get("json", {}))
                
                if response.status_code == case["expected_status"]:
                    self.log(f"✅ {case['desc']}: 正确返回{case['expected_status']}")
                else:
                    self.log(f"❌ {case['desc']}: 期望{case['expected_status']}, 实际{response.status_code}", "ERROR")
                    
            except Exception as e:
                self.log(f"❌ {case['desc']}异常: {e}", "ERROR")
    
    def cleanup_test_data(self):
        """清理测试数据"""
        self.log("🧹 清理测试数据...")
        
        # 搜索并删除测试文档
        test_keywords = ["API测试文档", "用户2的测试文档", "临时删除测试文档"]
        
        for keyword in test_keywords:
            try:
                search_response = self.session.get(
                    f"{self.base_url}/api/documents/search",
                    params={"keyword": keyword}
                )
                
                if search_response.status_code == 200:
                    search_data = search_response.json()
                    for doc in search_data["results"]:
                        delete_response = self.session.delete(
                            f"{self.base_url}/api/documents/id/{doc['id']}"
                        )
                        if delete_response.status_code == 200:
                            self.log(f"✅ 清理文档: {doc['title']}")
                        
            except Exception as e:
                self.log(f"❌ 清理数据异常: {keyword} - {e}", "ERROR")
    
    def run_all_tests(self):
        """运行所有测试"""
        self.log("🚀 开始API接口测试...\n")
        
        test_results = []
        
        # 基础测试
        test_results.append(("健康检查", self.test_health_check()))
        test_results.append(("根路径", self.test_root_endpoint()))
        
        # CRUD测试
        create_result = self.test_create_document()
        test_results.append(("创建文档", len(create_result["created_docs"]) > 0))
        
        test_results.append(("获取文档", self.test_get_document_by_id() is not False))
        test_results.append(("列出文档", self.test_list_documents() is not False))
        test_results.append(("更新文档", self.test_update_document()))
        test_results.append(("删除文档", self.test_delete_document()))
        
        # 查询测试
        test_results.append(("搜索文档", self.test_search_documents() is not False))
        test_results.append(("标签查询", self.test_get_documents_by_tag() is not False))
        
        # 错误测试
        test_results.append(("错误情况", self.test_error_cases() is not False))
        
        # 输出测试结果
        self.log("\n📊 测试结果汇总:")
        passed = 0
        total = len(test_results)
        
        for test_name, result in test_results:
            status = "✅ 通过" if result else "❌ 失败"
            self.log(f"  {test_name}: {status}")
            if result:
                passed += 1
        
        self.log(f"\n🎯 测试完成: {passed}/{total} 通过")
        
        return passed == total

def main():
    """主函数"""
    import sys
    
    # 检查服务器是否运行
    tester = APITester()
    
    if not tester.test_health_check():
        print("❌ 服务器未运行，请先启动API服务器:")
        print("   python start.py")
        sys.exit(1)
    
    # 运行所有测试
    success = tester.run_all_tests()
    
    # 询问是否清理测试数据
    response = input("\n是否清理测试数据? (y/n): ").lower().strip()
    if response in ['y', 'yes', '是']:
        tester.cleanup_test_data()
    else:
        print("保留测试数据")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 