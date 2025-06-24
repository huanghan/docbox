# 测试文件说明

本目录包含NoteDocs API的测试用例，用于验证API接口的功能和稳定性。

## 测试文件列表

### 分类相关测试
- `test_category_api.py` - 完整的分类API测试套件
- `test_category_simple.py` - 快速的分类API基本功能测试

### 文档相关测试
- `test_api.py` - 原有的文档API测试
- `test_db.py` - 数据库功能测试
- `test_update.py` - 更新功能测试

### 测试运行器
- `run_tests.py` - 统一运行所有测试的脚本

## 如何运行测试

### 前提条件
1. 确保API服务正在运行：
   ```bash
   cd ..
   python start.py
   ```

2. 安装依赖：
   ```bash
   pip install requests
   ```

### 运行单个测试

#### 快速分类测试（推荐）
```bash
python test_category_simple.py
```
这个测试会快速验证分类API的基本功能，包括：
- 创建分类
- 获取分类列表
- 修改分类
- 添加文档到分类
- 查看分类文档
- 删除分类

#### 完整分类测试
```bash
python test_category_api.py
```
这个测试会进行更全面的测试，包括错误处理和边界情况。

#### 其他测试
```bash
python test_api.py      # 文档API测试
python test_db.py       # 数据库测试
python test_update.py   # 更新功能测试
```

### 运行所有测试
```bash
python run_tests.py
```

## 测试说明

### 分类API测试覆盖内容

#### 基本CRUD操作
- ✅ 创建分类 (`POST /api/categories`)
- ✅ 获取分类列表 (`GET /api/categories?uid={uid}`)
- ✅ 修改分类 (`PUT /api/categories/{id}?uid={uid}`)
- ✅ 删除分类 (`DELETE /api/categories/{id}?uid={uid}`)

#### 分类-文档关联操作
- ✅ 添加文档到分类 (`POST /api/categories/{id}/docs`)
- ✅ 从分类移除文档 (`DELETE /api/categories/{id}/docs/{doc_id}`)
- ✅ 获取分类下的文档 (`GET /api/categories/{id}/docs`)

#### 错误处理测试
- ✅ 访问不存在的分类
- ✅ 无权限操作
- ✅ 无效请求数据
- ✅ 空的更新请求

### 测试数据
测试会使用测试用户ID `1001` 创建临时数据，测试完成后会自动清理。

### 注意事项
1. 确保API服务在运行测试前已启动
2. 测试会创建和删除临时数据，不会影响生产数据
3. 如果测试失败，可能需要手动清理残留的测试数据
4. 测试使用的是HTTP请求，确保网络连接正常

## 故障排除

### 常见问题

#### 连接失败
```
❌ 无法连接到API服务
```
**解决方案**：确保API服务正在运行在 `http://127.0.0.1:8001`

#### 测试数据残留
如果测试异常中断，可能留下测试数据，可以通过以下方式清理：
1. 使用API文档页面手动删除：`http://127.0.0.1:8001/docs`
2. 查看数据库中用户ID为1001的数据

#### 导入错误
```
ModuleNotFoundError: No module named 'requests'
```
**解决方案**：安装requests库
```bash
pip install requests
```

## 扩展测试

如需添加新的测试用例：

1. 创建新的测试文件，如 `test_new_feature.py`
2. 在 `run_tests.py` 中添加测试文件信息
3. 按照现有测试的格式编写测试代码
4. 确保测试完成后清理创建的数据 