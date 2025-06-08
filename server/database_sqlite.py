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
                
                # 创建索引
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_uid ON docs(uid)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_url ON docs(url)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_title ON docs(title)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_tags ON docs(tags)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_updated_at ON docs(updated_at)")
                
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

# 全局数据库实例
db = NotedocsDB()
