# 📚 FastAPI收藏服务器

基于FastAPI构建的现代化Chrome书签扩展后端服务，提供高性能的收藏管理和统计功能。

## ✨ 特性

- 🚀 **FastAPI框架** - 现代、快速的Python Web框架
- 📝 **自动API文档** - Swagger UI 和 ReDoc 支持
- 🔧 **模块化架构** - 清晰的代码组织和职责分离
- 📊 **实时统计** - 收藏数据统计和分析
- 🔍 **高级搜索** - 支持标题、URL、标签搜索
- 📄 **分页支持** - 高效的大数据量处理
- 🔒 **类型安全** - Pydantic数据验证
- 📱 **CORS支持** - 完善的跨域配置
- 💾 **JSON存储** - 轻量级文件存储
- 🧪 **完整测试** - 异步测试套件

## 🏗️ 项目结构

```
server/
├── api/                    # API路由层
│   ├── __init__.py
│   ├── bookmark_routes.py  # 收藏相关路由
│   └── stats_routes.py     # 统计相关路由
├── models/                 # 数据模型层
│   ├── __init__.py
│   ├── bookmark.py         # 收藏数据模型
│   ├── stats.py           # 统计数据模型
│   └── common.py          # 通用数据模型
├── services/               # 业务逻辑层
│   ├── __init__.py
│   ├── bookmark_service.py # 收藏业务逻辑
│   └── stats_service.py   # 统计业务逻辑
├── utils/                  # 工具函数层
│   ├── __init__.py
│   ├── file_utils.py      # 文件操作工具
│   └── auth_utils.py      # 认证工具
├── data/                   # 数据存储目录
│   ├── bookmarks.json     # 收藏数据
│   └── stats.json         # 统计数据
├── main.py                 # FastAPI主应用
├── config.py              # 应用配置
├── requirements.txt       # 依赖包
├── start_fastapi.py       # 启动脚本
├── test_fastapi.py        # 测试脚本
└── README.md              # 说明文档
```

## 🚀 快速开始

### 1. 安装依赖

```bash
# 进入服务器目录
cd server

# 安装Python依赖
pip install -r requirements.txt
```

### 2. 启动服务器

```bash
# 使用启动脚本（推荐）
python start_fastapi.py

# 或直接启动
python main.py

# 开发模式（自动重载）
uvicorn main:app --reload --host localhost --port 3000
```

### 3. 访问服务

- **服务器首页**: http://localhost:3000
- **API文档**: http://localhost:3000/docs（开发模式）
- **API状态**: http://localhost:3000/status

## 📋 API接口

### 收藏管理

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/bookmarks` | 创建新收藏 |
| GET | `/api/bookmarks` | 获取收藏列表 |
| GET | `/api/bookmarks/{id}` | 获取单个收藏 |
| PUT | `/api/bookmarks/{id}` | 更新收藏 |
| DELETE | `/api/bookmarks/{id}` | 删除收藏 |

### 统计信息

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/stats` | 获取实时统计 |
| GET | `/api/stats/cached` | 获取缓存统计 |
| GET | `/api/stats/summary` | 获取统计摘要 |
| POST | `/api/stats/refresh` | 刷新统计缓存 |

### 查询参数

收藏列表支持以下查询参数：

- `page`: 页码（默认1）
- `page_size`: 每页数量（默认20，最大100）
- `search`: 搜索关键词
- `tag`: 标签过滤

示例：
```
GET /api/bookmarks?page=1&page_size=10&search=Python&tag=开发
```

## 📊 数据模型

### 收藏模型

```json
{
  "id": "uuid",
  "url": "https://example.com",
  "title": "页面标题",
  "tags": ["标签1", "标签2"],
  "note": "备注信息",
  "favicon": "https://example.com/favicon.ico",
  "domain": "example.com",
  "timestamp": "2023-12-07T10:30:00.000Z",
  "created_date": "2023-12-07",
  "user_agent": "BookmarkExtension/1.0.0",
  "type": "bookmark",
  "content": "选中的内容"
}
```

### 统计模型

```json
{
  "total_bookmarks": 100,
  "last_updated": "2023-12-07T10:30:00.000Z",
  "date_counts": {
    "2023-12-07": 10,
    "2023-12-06": 5
  },
  "top_tags": [
    ["开发", 20],
    ["技术", 15]
  ],
  "top_domains": [
    ["github.com", 15],
    ["stackoverflow.com", 10]
  ]
}
```

## ⚙️ 配置选项

可以通过环境变量或`.env`文件配置（所有变量以`BOOKMARK_`为前缀）：

```bash
# 服务器设置
BOOKMARK_HOST=localhost
BOOKMARK_PORT=3000
BOOKMARK_DEBUG=false
BOOKMARK_RELOAD=false

# 数据存储
BOOKMARK_DATA_DIR=data

# 认证设置
BOOKMARK_REQUIRE_AUTH=false
BOOKMARK_API_KEYS=["key1", "key2"]

# 日志设置
BOOKMARK_LOG_LEVEL=INFO
BOOKMARK_LOG_FILE=server.log

# 分页设置
BOOKMARK_DEFAULT_PAGE_SIZE=20
BOOKMARK_MAX_PAGE_SIZE=100
```

## 🧪 测试

### 运行测试套件

```bash
# 确保服务器运行中
python test_fastapi.py
```

测试包括：
- ✅ 服务器状态检查
- ✅ 首页访问测试
- ✅ 收藏创建/读取/更新
- ✅ 搜索和分页功能
- ✅ 统计信息获取

### 手动测试

```bash
# 创建收藏
curl -X POST http://localhost:3000/api/bookmarks \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "title": "测试页面",
    "tags": ["测试", "示例"],
    "note": "这是一个测试收藏"
  }'

# 获取收藏列表
curl http://localhost:3000/api/bookmarks

# 获取统计信息
curl http://localhost:3000/api/stats
```

## 🔧 开发指南

### 添加新的API端点

1. 在`models/`中定义数据模型
2. 在`services/`中实现业务逻辑
3. 在`api/`中创建路由处理器
4. 在`main.py`中注册路由

### 数据验证

使用Pydantic进行自动数据验证：

```python
from pydantic import BaseModel, Field, HttpUrl

class BookmarkCreate(BaseModel):
    url: HttpUrl = Field(..., description="网页URL")
    title: str = Field(..., min_length=1, max_length=500)
    tags: List[str] = Field(default=[])
```

### 错误处理

FastAPI自动处理验证错误，自定义错误使用HTTPException：

```python
from fastapi import HTTPException

if not bookmark:
    raise HTTPException(status_code=404, detail="收藏不存在")
```

## 🐛 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   # 检查端口占用
   netstat -an | findstr :3000
   # 修改配置中的端口号
   ```

2. **依赖安装失败**
   ```bash
   # 升级pip
   python -m pip install --upgrade pip
   # 使用国内镜像
   pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
   ```

3. **CORS错误**
   - 检查`config.py`中的CORS配置
   - 确保Chrome扩展的域名在允许列表中

4. **数据文件权限**
   ```bash
   # 确保data目录可写
   chmod 755 data/
   ```

## 📝 更新日志

### v2.0.0 (FastAPI重构)
- 🚀 升级到FastAPI框架
- 🔧 模块化代码架构
- 📝 自动API文档生成
- 🧪 完整的异步测试套件
- 📊 增强的统计功能
- 🔒 改进的数据验证

### v1.0.0 (初始版本)
- 基础HTTP服务器
- 收藏管理功能
- 简单统计接口

## 📞 支持

如有问题或建议，请：

1. 查看API文档：http://localhost:3000/docs
2. 运行测试脚本确认功能
3. 检查服务器日志
4. 查看本文档的故障排除部分

## 📄 许可证

MIT License - 详见LICENSE文件 