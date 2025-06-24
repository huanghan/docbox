"""
数据库配置和表结构 - MySQL 5.7
"""
import pymysql
from typing import Optional, List, Dict
from config import MYSQL_CONFIG

class NotedocsDB:
    def __init__(self):
        self.config = {
            **MYSQL_CONFIG,
            'charset': 'utf8mb4',
            'autocommit': True
        }
    
    def get_connection(self):
        """获取数据库连接"""
        return pymysql.connect(**self.config)
    
    def write_document(self, uid: int, title: str, summary: str, content: str, 
                      source: str = '', tags: str = '', evaluate: int = 0) -> bool:
        """写入文档"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO docs (uid, title, summary, content, source, tags, evaluate, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                    ON DUPLICATE KEY UPDATE
                    uid = VALUES(uid),
                    summary = VALUES(summary),
                    content = VALUES(content),
                    source = VALUES(source),
                    tags = VALUES(tags),
                    evaluate = VALUES(evaluate),
                    updated_at = NOW()
                """, (uid, title, summary, content, source, tags, evaluate))
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
                    SELECT id, uid, title, summary, content, source, tags, evaluate, created_at, updated_at
                    FROM docs WHERE title = %s
                """, (title,))
                row = cursor.fetchone()
                
                if row:
                    return {
                        "id": row[0],
                        "uid": row[1],
                        "title": row[2],
                        "summary": row[3],
                        "content": row[4],
                        "source": row[5],
                        "tags": row[6],
                        "evaluate": row[7],
                        "created_at": str(row[8]),
                        "updated_at": str(row[9])
                    }
                return None
        except Exception as e:
            print(f"读取文档失败: {e}")
            return None
    
    def update_document_by_id(self, doc_id: int, uid: int, title: str, summary: str, 
                             content: str, source: str = '', tags: str = '', evaluate: int = 0) -> bool:
        """根据ID更新文档"""
        #print(f"=== 数据库更新操作 ===")
        print(f"更新文档ID: {doc_id}")
        #print(f"更新参数: uid={uid}, title='{title}', summary='{summary[:50]}...', content={(content)}, source='{source}', tags='{tags}', evaluate={evaluate}")
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                sql = """
                    UPDATE docs SET 
                    uid = %s, title = %s, summary = %s, content = %s, 
                    source = %s, tags = %s, evaluate = %s, updated_at = NOW()
                    WHERE id = %s
                """
                params = (uid, title, summary, content, source, tags, evaluate, doc_id)
                
                #print(f"执行SQL: {sql}")
                #print(f"SQL参数: {params}")
                
                cursor.execute(sql, params)
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
                    SELECT id, uid, title, summary, content, source, tags, evaluate, created_at, updated_at
                    FROM docs WHERE id = %s
                """, (doc_id,))
                row = cursor.fetchone()
                
                if row:
                    return {
                        "id": row[0],
                        "uid": row[1],
                        "title": row[2],
                        "summary": row[3],
                        "content": row[4],
                        "source": row[5],
                        "tags": row[6],
                        "evaluate": row[7],
                        "created_at": str(row[8]),
                        "updated_at": str(row[9])
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
                        SELECT id, uid, title, summary, source, tags, evaluate, created_at, updated_at
                        FROM docs WHERE uid = %s 
                        ORDER BY updated_at DESC 
                        LIMIT %s OFFSET %s
                    """, (uid, limit, offset))
                else:
                    cursor.execute("""
                        SELECT id, uid, title, summary, source, tags, evaluate, created_at, updated_at
                        FROM docs 
                        ORDER BY updated_at DESC 
                        LIMIT %s OFFSET %s
                    """, (limit, offset))
                
                results = []
                for row in cursor.fetchall():
                    results.append({
                        "id": row[0],
                        "uid": row[1],
                        "title": row[2],
                        "summary": row[3],
                        "source": row[4],
                        "tags": row[5],
                        "evaluate": row[6],
                        "created_at": str(row[7]),
                        "updated_at": str(row[8])
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
                cursor.execute("DELETE FROM docs WHERE title = %s", (title,))
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
                cursor.execute("DELETE FROM docs WHERE id = %s", (doc_id,))
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
                
                if uid is not None:
                    cursor.execute("""
                        SELECT id, uid, title, summary, content, source, tags, evaluate, created_at, updated_at
                        FROM docs 
                        WHERE uid = %s AND (title LIKE %s OR summary LIKE %s OR content LIKE %s OR tags LIKE %s)
                        ORDER BY evaluate DESC, updated_at DESC
                        LIMIT %s OFFSET %s
                    """, (uid, f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", limit, offset))
                else:
                    cursor.execute("""
                        SELECT id, uid, title, summary, content, source, tags, evaluate, created_at, updated_at
                        FROM docs 
                        WHERE title LIKE %s OR summary LIKE %s OR content LIKE %s OR tags LIKE %s
                        ORDER BY evaluate DESC, updated_at DESC
                        LIMIT %s OFFSET %s
                    """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", limit, offset))
                
                results = []
                for row in cursor.fetchall():
                    results.append({
                        "id": row[0],
                        "uid": row[1],
                        "title": row[2],
                        "summary": row[3],
                        "content": row[4][:200] + "..." if len(row[4]) > 200 else row[4],
                        "source": row[5],
                        "tags": row[6],
                        "evaluate": row[7],
                        "created_at": str(row[8]),
                        "updated_at": str(row[9])
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
                
                if uid is not None:
                    cursor.execute("""
                        SELECT id, uid, title, summary, source, tags, evaluate, created_at, updated_at
                        FROM docs 
                        WHERE uid = %s AND tags LIKE %s
                        ORDER BY evaluate DESC, updated_at DESC
                        LIMIT %s OFFSET %s
                    """, (uid, f"%{tag}%", limit, offset))
                else:
                    cursor.execute("""
                        SELECT id, uid, title, summary, source, tags, evaluate, created_at, updated_at
                        FROM docs 
                        WHERE tags LIKE %s
                        ORDER BY evaluate DESC, updated_at DESC
                        LIMIT %s OFFSET %s
                    """, (f"%{tag}%", limit, offset))
                
                results = []
                for row in cursor.fetchall():
                    results.append({
                        "id": row[0],
                        "uid": row[1],
                        "title": row[2],
                        "summary": row[3],
                        "source": row[4],
                        "tags": row[5],
                        "evaluate": row[6],
                        "created_at": str(row[7]),
                        "updated_at": str(row[8])
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
                    cursor.execute("SELECT COUNT(*) FROM docs WHERE uid = %s", (uid,))
                else:
                    cursor.execute("SELECT COUNT(*) FROM docs")
                
                result = cursor.fetchone()
                return result[0] if result else 0
        except Exception as e:
            print(f"获取文档总数失败: {e}")
            return 0

# 全局数据库实例
db = NotedocsDB() 