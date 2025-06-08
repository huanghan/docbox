# NoteDocs - 文档管理系统

基于 FastAPI + MySQL 5.7 的文档管理系统

## 功能特性

- ✅ 文档增删改查
- ✅ 文档搜索
- ✅ MySQL 5.7 数据库
- ✅ RESTful API
- ✅ 自动API文档

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制环境变量示例文件并修改配置：

```bash
cp env.example .env
```

编辑 `.env` 文件，修改数据库连接信息。

### 3. 启动MySQL数据库

使用Docker Compose启动MySQL 5.7：

```bash
docker-compose up -d
```

### 4. 启动服务

```bash
python start.py
```

或直接运行：

```bash
python main.py
```

## API接口

### 写入文档
```
POST /api/documents/write
```

### 读取文档
```
GET /api/documents/{title}
```

### 列出所有文档
```
GET /api/documents
```

### 删除文档
```
DELETE /api/documents/{title}
```

### 搜索文档
```
GET /api/documents/search/{keyword}
```

### 健康检查
```
GET /health
```

## 配置说明

在 `.env` 文件中配置环境变量：

- `MYSQL_HOST`: MySQL主机地址 (默认: localhost)
- `MYSQL_PORT`: MySQL端口 (默认: 3306)
- `MYSQL_USER`: MySQL用户名 (默认: root)
- `MYSQL_PASSWORD`: MySQL密码 (默认: 123456)
- `MYSQL_DATABASE`: 数据库名 (默认: notedocs)
- `API_HOST`: API服务主机 (默认: 127.0.0.1)
- `API_PORT`: API服务端口 (默认: 8000)
- `API_DEBUG`: 调试模式 (默认: True)

## 数据库结构

```sql
CREATE TABLE docs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL UNIQUE,
    content LONGTEXT NOT NULL,
    time VARCHAR(50) NOT NULL,
    uid VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
``` 