import requests
import json

# 先创建一个测试文档
doc_data = {
    'uid': 999,
    'title': '更新测试文档',
    'summary': '原始摘要',
    'content': '原始内容',
    'source': 'test',
    'tags': 'test',
    'evaluate': 3
}

print("🔸 测试更新功能...")

# 创建文档
create_resp = requests.post('http://127.0.0.1:8001/api/documents', json=doc_data)
print(f'✅ 创建文档: {create_resp.status_code}')

# 搜索文档获取ID
search_resp = requests.get('http://127.0.0.1:8001/api/documents/search?keyword=更新测试文档')
if search_resp.status_code == 200:
    search_data = search_resp.json()
    if search_data['results']:
        doc_id = search_data['results'][0]['id']
        print(f'📋 文档ID: {doc_id}')
        
        # 更新文档
        update_data = {'summary': '已更新的摘要', 'evaluate': 5}
        update_resp = requests.put(f'http://127.0.0.1:8001/api/documents/id/{doc_id}', json=update_data)
        print(f'🔄 更新文档: {update_resp.status_code}')
        
        # 验证更新
        get_resp = requests.get(f'http://127.0.0.1:8001/api/documents/id/{doc_id}')
        if get_resp.status_code == 200:
            doc = get_resp.json()
            print(f'✅ 验证更新: 摘要="{doc["summary"]}", 评分={doc["evaluate"]}')
            
            if doc["summary"] == "已更新的摘要" and doc["evaluate"] == 5:
                print("🎉 更新功能测试通过！")
            else:
                print("❌ 更新功能测试失败！")
        
        # 清理
        delete_resp = requests.delete(f'http://127.0.0.1:8001/api/documents/id/{doc_id}')
        print(f'🧹 清理完成: {delete_resp.status_code}')
    else:
        print("❌ 未找到创建的文档")
else:
    print("❌ 搜索文档失败") 