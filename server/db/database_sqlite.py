"""
数据库配置和表结构 - SQLite
"""
import sqlite3
import os
from typing import Optional, List, Dict
from datetime import datetime

class NotedocsDB:
    def __init__(self, db_path: str = "data/notedocs.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库表结构"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS docs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        uid INTEGER NOT NULL,
                        url TEXT NOT NULL,
                        title TEXT NOT NULL UNIQUE,
                        summary TEXT,
                        content TEXT,
                        source TEXT DEFAULT '',
                        favicon TEXT DEFAULT '',
                        tags TEXT DEFAULT '',
                        evaluate INTEGER DEFAULT 0,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # 创建分类表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS categories (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        uid INTEGER NOT NULL DEFAULT 0,
                        name TEXT NOT NULL DEFAULT '',
                        tags TEXT NOT NULL DEFAULT '',
                        icon TEXT NOT NULL DEFAULT '',
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # 创建分类-文档关联表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS categories_docs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        category_id INTEGER NOT NULL DEFAULT 0,
                        doc_id INTEGER NOT NULL DEFAULT 0,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE,
                        FOREIGN KEY (doc_id) REFERENCES docs(id) ON DELETE CASCADE
                    )
                """)
                
                # 创建索引
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_uid ON docs(uid)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_url ON docs(url)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_title ON docs(title)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_tags ON docs(tags)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_updated_at ON docs(updated_at)")
                
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_categories_uid ON categories(uid)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_categories_name ON categories(name)")
                
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_categories_docs_category_id ON categories_docs(category_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_categories_docs_doc_id ON categories_docs(doc_id)")
                
                conn.commit()
        except Exception as e:
            print(f"初始化数据库失败: {e}")
    
    def get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # 启用行工厂，方便访问列名
        return conn
    
    def write_document(self, uid: int, url: str, title: str, summary: str, content: str, 
                      source: str = '', favicon: str = '', tags: str = '', evaluate: int = 0) -> bool:
        """写入文档"""
        try:
            print(f"写入文档: {title}")
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO docs (uid, url, title, summary, content, source, favicon, tags, evaluate, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
                """, (uid, url, title, summary, content, source, favicon, tags, evaluate))
                conn.commit()
                return True
        except Exception as e:
            print(f"写入文档失败: {e}")
            return False
    
    def read_document(self, title: str) -> Optional[Dict]:
        """读取文档"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, uid, url, title, summary, content, source, favicon, tags, evaluate, created_at, updated_at
                    FROM docs WHERE title = ?
                """, (title,))
                row = cursor.fetchone()
                
                if row:
                    return {
                        "id": row["id"],
                        "uid": row["uid"],
                        "url": row["url"],
                        "title": row["title"],
                        "summary": row["summary"],
                        "content": row["content"],
                        "source": row["source"],
                        "favicon": row["favicon"],
                        "tags": row["tags"],
                        "evaluate": row["evaluate"],
                        "created_at": row["created_at"],
                        "updated_at": row["updated_at"]
                    }
                return None
        except Exception as e:
            print(f"读取文档失败: {e}")
            return None
    
    def update_document_by_id(self, doc_id: int, uid: int, url: str, title: str, summary: str, 
                             content: str, source: str = '', favicon: str = '', tags: str = '', evaluate: int = 0) -> bool:
        """根据ID更新文档"""
        print(f"更新文档ID: {doc_id}")
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE docs SET 
                    uid = ?, url = ?, title = ?, summary = ?, content = ?, 
                    source = ?, favicon = ?, tags = ?, evaluate = ?, updated_at = datetime('now')
                    WHERE id = ?
                """, (uid, url, title, summary, content, source, favicon, tags, evaluate, doc_id))
                
                conn.commit()
                affected_rows = cursor.rowcount
                print(f"影响的行数: {affected_rows}")
                
                return affected_rows > 0
        except Exception as e:
            print(f"更新文档失败: {e}")
            return False

    def read_document_by_id(self, doc_id: int) -> Optional[Dict]:
        """根据ID读取文档"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, uid, url, title, summary, content, source, favicon, tags, evaluate, created_at, updated_at
                    FROM docs WHERE id = ?
                """, (doc_id,))
                row = cursor.fetchone()
                
                if row:
                    return {
                        "id": row["id"],
                        "uid": row["uid"],
                        "url": row["url"],
                        "title": row["title"],
                        "summary": row["summary"],
                        "content": row["content"],
                        "source": row["source"],
                        "favicon": row["favicon"],
                        "tags": row["tags"],
                        "evaluate": row["evaluate"],
                        "created_at": row["created_at"],
                        "updated_at": row["updated_at"]
                    }
                return None
        except Exception as e:
            print(f"读取文档失败: {e}")
            return None
    
    def list_documents(self, uid: Optional[int] = None, limit: int = 100, offset: int = 0) -> List[Dict]:
        """列出文档（支持分页和用户过滤）"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if uid is not None:
                    cursor.execute("""
                        SELECT id, uid, url, title, summary, source, favicon, tags, evaluate, created_at, updated_at
                        FROM docs WHERE uid = ? 
                        ORDER BY updated_at DESC 
                        LIMIT ? OFFSET ?
                    """, (uid, limit, offset))
                else:
                    cursor.execute("""
                        SELECT id, uid, url, title, summary, source, favicon, tags, evaluate, created_at, updated_at
                        FROM docs 
                        ORDER BY updated_at DESC 
                        LIMIT ? OFFSET ?
                    """, (limit, offset))
                
                results = []
                for row in cursor.fetchall():
                    results.append({
                        "id": row["id"],
                        "uid": row["uid"],
                        "url": row["url"],
                        "title": row["title"],
                        "summary": row["summary"],
                        "source": row["source"],
                        "favicon": row["favicon"],
                        "tags": row["tags"],
                        "evaluate": row["evaluate"],
                        "created_at": row["created_at"],
                        "updated_at": row["updated_at"]
                    })
                return results
        except Exception as e:
            print(f"列出文档失败: {e}")
            return []
    
    def delete_document(self, title: str) -> bool:
        """删除文档"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM docs WHERE title = ?", (title,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"删除文档失败: {e}")
            return False
    
    def delete_document_by_id(self, doc_id: int) -> bool:
        """根据ID删除文档"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM docs WHERE id = ?", (doc_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"删除文档失败: {e}")
            return False
    
    def search_documents(self, keyword: str, uid: Optional[int] = None, 
                        limit: int = 50, offset: int = 0) -> List[Dict]:
        """搜索文档（支持用户过滤和分页）"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                search_pattern = f"%{keyword}%"
                
                if uid is not None:
                    cursor.execute("""
                        SELECT id, uid, url, title, summary, content, source, favicon, tags, evaluate, created_at, updated_at
                        FROM docs 
                        WHERE uid = ? AND (title LIKE ? OR summary LIKE ? OR content LIKE ? OR tags LIKE ?)
                        ORDER BY evaluate DESC, updated_at DESC
                        LIMIT ? OFFSET ?
                    """, (uid, search_pattern, search_pattern, search_pattern, search_pattern, limit, offset))
                else:
                    cursor.execute("""
                        SELECT id, uid, url, title, summary, content, source, favicon, tags, evaluate, created_at, updated_at
                        FROM docs 
                        WHERE title LIKE ? OR summary LIKE ? OR content LIKE ? OR tags LIKE ?
                        ORDER BY evaluate DESC, updated_at DESC
                        LIMIT ? OFFSET ?
                    """, (search_pattern, search_pattern, search_pattern, search_pattern, limit, offset))
                
                results = []
                for row in cursor.fetchall():
                    content = row["content"]
                    content_preview = content[:200] + "..." if len(content) > 200 else content
                    
                    results.append({
                        "id": row["id"],
                        "uid": row["uid"],
                        "url": row["url"],
                        "title": row["title"],
                        "summary": row["summary"],
                        "content": content_preview,
                        "source": row["source"],
                        "favicon": row["favicon"],
                        "tags": row["tags"],
                        "evaluate": row["evaluate"],
                        "created_at": row["created_at"],
                        "updated_at": row["updated_at"]
                    })
                return results
        except Exception as e:
            print(f"搜索文档失败: {e}")
            return []
    
    def get_documents_by_tag(self, tag: str, uid: Optional[int] = None, 
                            limit: int = 50, offset: int = 0) -> List[Dict]:
        """根据标签获取文档"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                tag_pattern = f"%{tag}%"
                
                if uid is not None:
                    cursor.execute("""
                        SELECT id, uid, url, title, summary, source, favicon, tags, evaluate, created_at, updated_at
                        FROM docs 
                        WHERE uid = ? AND tags LIKE ?
                        ORDER BY evaluate DESC, updated_at DESC
                        LIMIT ? OFFSET ?
                    """, (uid, tag_pattern, limit, offset))
                else:
                    cursor.execute("""
                        SELECT id, uid, url, title, summary, source, favicon, tags, evaluate, created_at, updated_at
                        FROM docs 
                        WHERE tags LIKE ?
                        ORDER BY evaluate DESC, updated_at DESC
                        LIMIT ? OFFSET ?
                    """, (tag_pattern, limit, offset))
                
                results = []
                for row in cursor.fetchall():
                    results.append({
                        "id": row["id"],
                        "uid": row["uid"],
                        "url": row["url"],
                        "title": row["title"],
                        "summary": row["summary"],
                        "source": row["source"],
                        "favicon": row["favicon"],
                        "tags": row["tags"],
                        "evaluate": row["evaluate"],
                        "created_at": row["created_at"],
                        "updated_at": row["updated_at"]
                    })
                return results
        except Exception as e:
            print(f"根据标签获取文档失败: {e}")
            return []

    def get_documents_count(self, uid: Optional[int] = None) -> int:
        """获取文档总数（支持用户过滤）"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if uid is not None:
                    cursor.execute("SELECT COUNT(*) FROM docs WHERE uid = ?", (uid,))
                else:
                    cursor.execute("SELECT COUNT(*) FROM docs")
                
                result = cursor.fetchone()
                return result[0] if result else 0
        except Exception as e:
            print(f"获取文档总数失败: {e}")
            return 0

    # ========== 分类管理操作 ==========
    
    def get_categories_by_uid(self, uid: int) -> List[Dict]:
        """按uid查询所有分类目录"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, uid, name, tags, icon, created_at, updated_at
                    FROM categories WHERE uid = ?
                    ORDER BY created_at DESC
                """, (uid,))
                
                results = []
                for row in cursor.fetchall():
                    results.append({
                        "id": row["id"],
                        "uid": row["uid"],
                        "name": row["name"],
                        "tags": row["tags"],
                        "icon": row["icon"],
                        "created_at": row["created_at"],
                        "updated_at": row["updated_at"]
                    })
                return results
        except Exception as e:
            print(f"查询分类失败: {e}")
            return []

    def create_category(self, uid: int, name: str, tags: str = '', icon: str = '') -> Optional[int]:
        """增加分类目录"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO categories (uid, name, tags, icon, updated_at)
                    VALUES (?, ?, ?, ?, datetime('now'))
                """, (uid, name, tags, icon))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            print(f"创建分类失败: {e}")
            return None

    def delete_category(self, category_id: int, uid: int) -> bool:
        """删除分类目录（只能删除自己的分类）"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                # 先删除关联的文档关系
                cursor.execute("DELETE FROM categories_docs WHERE category_id = ?", (category_id,))
                # 再删除分类
                cursor.execute("DELETE FROM categories WHERE id = ? AND uid = ?", (category_id, uid))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"删除分类失败: {e}")
            return False

    def update_category_name(self, category_id: int, uid: int, name: str, tags: str = None, icon: str = None) -> bool:
        """修改分类目录信息（只能修改自己的分类）"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # 构建动态更新语句
                update_fields = ["name = ?", "updated_at = datetime('now')"]
                params = [name]
                
                if tags is not None:
                    update_fields.insert(-1, "tags = ?")
                    params.insert(-1, tags)
                
                if icon is not None:
                    update_fields.insert(-1, "icon = ?")
                    params.insert(-1, icon)
                
                params.extend([category_id, uid])
                
                cursor.execute(f"""
                    UPDATE categories SET {', '.join(update_fields)}
                    WHERE id = ? AND uid = ?
                """, params)
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"修改分类失败: {e}")
            return False

    # ========== 分类-文档关联操作 ==========
    
    def add_doc_to_category(self, category_id: int, doc_id: int) -> bool:
        """给分类目录增加文章"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                # 检查是否已存在关联
                cursor.execute("""
                    SELECT id FROM categories_docs 
                    WHERE category_id = ? AND doc_id = ?
                """, (category_id, doc_id))
                
                if cursor.fetchone():
                    print(f"文档 {doc_id} 已在分类 {category_id} 中")
                    return True
                
                # 添加关联
                cursor.execute("""
                    INSERT INTO categories_docs (category_id, doc_id, updated_at)
                    VALUES (?, ?, datetime('now'))
                """, (category_id, doc_id))
                conn.commit()
                return True
        except Exception as e:
            print(f"添加文档到分类失败: {e}")
            return False

    def remove_doc_from_category(self, category_id: int, doc_id: int) -> bool:
        """删除分类目录下的文章"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM categories_docs 
                    WHERE category_id = ? AND doc_id = ?
                """, (category_id, doc_id))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"从分类删除文档失败: {e}")
            return False

    def get_docs_by_category(self, category_id: int, limit: int = 50, offset: int = 0) -> List[Dict]:
        """查询分类目录下的所有文章"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT d.id, d.uid, d.url, d.title, d.summary, d.source, d.favicon, 
                           d.tags, d.evaluate, d.created_at, d.updated_at
                    FROM docs d
                    INNER JOIN categories_docs cd ON d.id = cd.doc_id
                    WHERE cd.category_id = ?
                    ORDER BY d.updated_at DESC
                    LIMIT ? OFFSET ?
                """, (category_id, limit, offset))
                
                results = []
                for row in cursor.fetchall():
                    results.append({
                        "id": row["id"],
                        "uid": row["uid"],
                        "url": row["url"],
                        "title": row["title"],
                        "summary": row["summary"],
                        "source": row["source"],
                        "favicon": row["favicon"],
                        "tags": row["tags"],
                        "evaluate": row["evaluate"],
                        "created_at": row["created_at"],
                        "updated_at": row["updated_at"]
                    })
                return results
        except Exception as e:
            print(f"查询分类下的文档失败: {e}")
            return []

    def get_category_docs_count(self, category_id: int) -> int:
        """获取分类下的文档总数"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) FROM categories_docs WHERE category_id = ?
                """, (category_id,))
                result = cursor.fetchone()
                return result[0] if result else 0
        except Exception as e:
            print(f"获取分类文档总数失败: {e}")
            return 0

# 全局数据库实例
db = NotedocsDB()
