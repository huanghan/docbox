"""
数据库功能测试脚本
"""
import time
from database import db

def test_write_document():
    """测试写入文档"""
    print("🔸 测试写入文档...")
    
    # 测试数据
    test_docs = [
        {
            "uid": 1,
            "title": "Python编程指南",
            "summary": "Python基础编程教程",
            "content": "这是一个详细的Python编程指南，包含基础语法、数据结构、函数等内容。",
            "source": "tutorial",
            "tags": "python,programming,tutorial",
            "evaluate": 5
        },
        {
            "uid": 1,
            "title": "MySQL数据库教程",
            "summary": "MySQL数据库操作指南",
            "content": "MySQL是一个流行的关系型数据库管理系统，本教程介绍基本的SQL操作。",
            "source": "manual",
            "tags": "mysql,database,sql",
            "evaluate": 4
        },
        {
            "uid": 2,
            "title": "FastAPI开发实践",
            "summary": "FastAPI Web框架使用指南",
            "content": "FastAPI是一个现代、快速的Web框架，用于构建API。支持自动文档生成。",
            "source": "blog",
            "tags": "fastapi,web,api",
            "evaluate": 5
        }
    ]
    
    for doc in test_docs:
        success = db.write_document(**doc)
        print(f"  ✅ 写入文档 '{doc['title']}': {'成功' if success else '失败'}")
    
    print()

def test_read_document():
    """测试读取文档"""
    print("🔸 测试读取文档...")
    
    # 按标题读取
    doc = db.read_document("Python编程指南")
    if doc:
        print(f"  ✅ 读取文档成功: {doc['title']} (ID: {doc['id']})")
        print(f"     摘要: {doc['summary']}")
        print(f"     标签: {doc['tags']}")
        print(f"     评分: {doc['evaluate']}")
    else:
        print("  ❌ 读取文档失败")
    
    # 按ID读取
    if doc:
        doc_by_id = db.read_document_by_id(doc['id'])
        if doc_by_id:
            print(f"  ✅ 按ID读取文档成功: {doc_by_id['title']}")
        else:
            print("  ❌ 按ID读取文档失败")
    
    print()

def test_list_documents():
    """测试列出文档"""
    print("🔸 测试列出文档...")
    
    # 列出所有文档
    all_docs = db.list_documents(limit=10)
    print(f"  ✅ 所有文档数量: {len(all_docs)}")
    for doc in all_docs:
        print(f"     - {doc['title']} (用户ID: {doc['uid']}, 评分: {doc['evaluate']})")
    
    # 列出特定用户的文档
    user1_docs = db.list_documents(uid=1, limit=5)
    print(f"  ✅ 用户1的文档数量: {len(user1_docs)}")
    
    # 测试分页
    page1 = db.list_documents(limit=2, offset=0)
    page2 = db.list_documents(limit=2, offset=2)
    print(f"  ✅ 分页测试 - 第1页: {len(page1)}条, 第2页: {len(page2)}条")
    
    print()

def test_search_documents():
    """测试搜索文档"""
    print("🔸 测试搜索文档...")
    
    # 搜索关键词
    search_results = db.search_documents("Python")
    print(f"  ✅ 搜索'Python'结果: {len(search_results)}条")
    for doc in search_results:
        print(f"     - {doc['title']} (评分: {doc['evaluate']})")
    
    # 按用户搜索
    user_search = db.search_documents("数据库", uid=1)
    print(f"  ✅ 用户1搜索'数据库'结果: {len(user_search)}条")
    
    # 搜索标签
    tag_search = db.search_documents("api")
    print(f"  ✅ 搜索'api'结果: {len(tag_search)}条")
    
    print()

def test_get_documents_by_tag():
    """测试按标签获取文档"""
    print("🔸 测试按标签获取文档...")
    
    # 获取python标签的文档
    python_docs = db.get_documents_by_tag("python")
    print(f"  ✅ 标签'python'的文档: {len(python_docs)}条")
    for doc in python_docs:
        print(f"     - {doc['title']} (标签: {doc['tags']})")
    
    # 按用户和标签获取
    user_tag_docs = db.get_documents_by_tag("web", uid=2)
    print(f"  ✅ 用户2标签'web'的文档: {len(user_tag_docs)}条")
    
    print()

def test_update_document():
    """测试更新文档"""
    print("🔸 测试更新文档...")
    
    # 更新文档（通过重新写入相同标题）
    success = db.write_document(
        uid=1,
        title="Python编程指南",
        summary="Python高级编程教程（已更新）",
        content="这是一个更新后的Python编程指南，增加了高级特性和最佳实践。",
        source="tutorial_v2",
        tags="python,programming,advanced,tutorial",
        evaluate=5
    )
    print(f"  ✅ 更新文档: {'成功' if success else '失败'}")
    
    # 验证更新
    updated_doc = db.read_document("Python编程指南")
    if updated_doc and "已更新" in updated_doc['summary']:
        print(f"  ✅ 验证更新成功: {updated_doc['summary']}")
    else:
        print("  ❌ 验证更新失败")
    
    print()

def test_delete_document():
    """测试删除文档"""
    print("🔸 测试删除文档...")
    
    # 先创建一个测试文档
    test_title = "临时测试文档"
    db.write_document(
        uid=999,
        title=test_title,
        summary="这是一个临时测试文档",
        content="用于测试删除功能",
        source="test",
        tags="test,temp",
        evaluate=1
    )
    
    # 验证文档存在
    temp_doc = db.read_document(test_title)
    if temp_doc:
        print(f"  ✅ 临时文档创建成功: {temp_doc['title']}")
        
        # 按标题删除
        success = db.delete_document(test_title)
        print(f"  ✅ 按标题删除文档: {'成功' if success else '失败'}")
        
        # 验证删除
        deleted_doc = db.read_document(test_title)
        if deleted_doc is None:
            print("  ✅ 验证删除成功")
        else:
            print("  ❌ 验证删除失败")
    
    # 测试按ID删除
    docs = db.list_documents(uid=2, limit=1)
    if docs:
        doc_id = docs[0]['id']
        success = db.delete_document_by_id(doc_id)
        print(f"  ✅ 按ID删除文档: {'成功' if success else '失败'}")
    
    print()

def test_edge_cases():
    """测试边界情况"""
    print("🔸 测试边界情况...")
    
    # 读取不存在的文档
    non_exist = db.read_document("不存在的文档")
    print(f"  ✅ 读取不存在文档: {'正确返回None' if non_exist is None else '错误'}")
    
    # 删除不存在的文档
    delete_result = db.delete_document("不存在的文档")
    print(f"  ✅ 删除不存在文档: {'正确返回False' if not delete_result else '错误'}")
    
    # 空关键词搜索
    empty_search = db.search_documents("")
    print(f"  ✅ 空关键词搜索: 返回{len(empty_search)}条结果")
    
    # 大数据量测试
    large_content = "x" * 10000  # 10KB内容
    success = db.write_document(
        uid=999,
        title="大内容测试文档",
        summary="测试大内容存储",
        content=large_content,
        source="test",
        tags="test,large",
        evaluate=3
    )
    print(f"  ✅ 大内容文档写入: {'成功' if success else '失败'}")
    
    # 清理测试数据
    db.delete_document("大内容测试文档")
    
    print()

def run_all_tests():
    """运行所有测试"""
    print("🚀 开始数据库功能测试...\n")
    
    try:
        test_write_document()
        test_read_document()
        test_list_documents()
        test_search_documents()
        test_get_documents_by_tag()
        test_update_document()
        test_delete_document()
        test_edge_cases()
        
        print("✅ 所有测试完成!")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

def cleanup_test_data():
    """清理测试数据"""
    print("🧹 清理测试数据...")
    
    test_titles = [
        "Python编程指南",
        "MySQL数据库教程", 
        "FastAPI开发实践",
        "临时测试文档",
        "大内容测试文档"
    ]
    
    for title in test_titles:
        db.delete_document(title)
    
    print("✅ 测试数据清理完成")

if __name__ == "__main__":
    # 运行测试
    run_all_tests()
    
    # 询问是否清理测试数据
    response = input("\n是否清理测试数据? (y/n): ").lower().strip()
    if response in ['y', 'yes', '是']:
        cleanup_test_data()
    else:
        print("保留测试数据") 