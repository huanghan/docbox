"""
收藏服务
"""

import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse

from sqlalchemy import create_engine, and_, or_
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from models.bookmark import BookmarkCreate, BookmarkResponse, BookmarkUpdate, BookmarkORM, Base
from models.common import PaginationParams
from utils.file_utils import ensure_directory_exists


class BookmarkService:
    """收藏服务类"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        ensure_directory_exists(data_dir)
        
        # 初始化SQLite数据库
        db_path = f"sqlite:///{data_dir}/bookmarks.db"
        self.engine = create_engine(db_path, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # 创建表
        Base.metadata.create_all(bind=self.engine)
    
    def _get_db(self) -> Session:
        """获取数据库会话"""
        return self.SessionLocal()
    
    def create_bookmark(self, bookmark_data: BookmarkCreate, user_agent: str = "") -> BookmarkResponse:
        """创建新收藏"""
        db = self._get_db()
        try:
            # 创建ORM对象
            bookmark_orm = BookmarkORM(
                id=str(uuid.uuid4()),
                url=str(bookmark_data.url),
                title=bookmark_data.title,
                tags=bookmark_data.tags,
                note=bookmark_data.note,
                favicon=bookmark_data.favicon or "",
                domain=bookmark_data.domain or self._extract_domain(str(bookmark_data.url)),
                timestamp=datetime.now(),
                created_date=datetime.now().strftime("%Y-%m-%d"),
                user_agent=user_agent,
                type=bookmark_data.type,
                content=bookmark_data.content or "",
                summary=bookmark_data.summary or "",
                keywords=bookmark_data.keywords or [],
                extracted_at=bookmark_data.extracted_at or ""
            )
            
            # 保存到数据库
            db.add(bookmark_orm)
            db.commit()
            db.refresh(bookmark_orm)
            
            return self._orm_to_response(bookmark_orm)
            
        except SQLAlchemyError as e:
            db.rollback()
            print(f"创建收藏失败: {e}")
            raise
        finally:
            db.close()
    
    def get_bookmarks(self, params: PaginationParams) -> tuple[List[BookmarkResponse], int]:
        """获取收藏列表"""
        db = self._get_db()
        try:
            # 构建查询
            query = db.query(BookmarkORM)
            
            # 搜索过滤
            if params.search:
                search_term = f"%{params.search.lower()}%"
                query = query.filter(
                    or_(
                        BookmarkORM.title.ilike(search_term),
                        BookmarkORM.url.ilike(search_term),
                        BookmarkORM.note.ilike(search_term),
                        BookmarkORM.content.ilike(search_term),
                        BookmarkORM.summary.ilike(search_term)
                    )
                )
            
            # 标签过滤
            if params.tag:
                # 在JSON数组中搜索标签
                query = query.filter(BookmarkORM.tags.contains([params.tag]))
            
            # 获取总数
            total = query.count()
            
            # 排序和分页
            bookmarks = (query
                        .order_by(BookmarkORM.timestamp.desc())
                        .offset((params.page - 1) * params.page_size)
                        .limit(params.page_size)
                        .all())
            
            # 转换为响应模型
            bookmark_responses = [self._orm_to_response(bookmark) for bookmark in bookmarks]
            
            return bookmark_responses, total
            
        except SQLAlchemyError as e:
            print(f"获取收藏列表失败: {e}")
            return [], 0
        finally:
            db.close()
    
    def get_bookmark_by_id(self, bookmark_id: str) -> Optional[BookmarkResponse]:
        """根据ID获取收藏"""
        db = self._get_db()
        try:
            bookmark = db.query(BookmarkORM).filter(BookmarkORM.id == bookmark_id).first()
            if bookmark:
                return self._orm_to_response(bookmark)
            return None
            
        except SQLAlchemyError as e:
            print(f"获取收藏失败: {e}")
            return None
        finally:
            db.close()
    
    def update_bookmark(self, bookmark_id: str, update_data: BookmarkUpdate) -> Optional[BookmarkResponse]:
        """更新收藏"""
        db = self._get_db()
        try:
            bookmark = db.query(BookmarkORM).filter(BookmarkORM.id == bookmark_id).first()
            if not bookmark:
                return None
            
            # 更新字段
            if update_data.title is not None:
                bookmark.title = update_data.title
            if update_data.tags is not None:
                bookmark.tags = update_data.tags
            if update_data.note is not None:
                bookmark.note = update_data.note
            if update_data.content is not None:
                bookmark.content = update_data.content
            if update_data.summary is not None:
                bookmark.summary = update_data.summary
            if update_data.keywords is not None:
                bookmark.keywords = update_data.keywords
            
            db.commit()
            db.refresh(bookmark)
            
            return self._orm_to_response(bookmark)
            
        except SQLAlchemyError as e:
            db.rollback()
            print(f"更新收藏失败: {e}")
            return None
        finally:
            db.close()
    
    def delete_bookmark(self, bookmark_id: str) -> bool:
        """删除收藏"""
        db = self._get_db()
        try:
            bookmark = db.query(BookmarkORM).filter(BookmarkORM.id == bookmark_id).first()
            if not bookmark:
                return False
            
            db.delete(bookmark)
            db.commit()
            return True
            
        except SQLAlchemyError as e:
            db.rollback()
            print(f"删除收藏失败: {e}")
            return False
        finally:
            db.close()
    
    def get_all_bookmarks(self) -> List[Dict[str, Any]]:
        """获取所有收藏（用于统计）"""
        db = self._get_db()
        try:
            bookmarks = db.query(BookmarkORM).all()
            return [self._orm_to_dict(bookmark) for bookmark in bookmarks]
            
        except SQLAlchemyError as e:
            print(f"获取所有收藏失败: {e}")
            return []
        finally:
            db.close()
    
    def _orm_to_response(self, bookmark_orm: BookmarkORM) -> BookmarkResponse:
        """将ORM对象转换为响应模型"""
        return BookmarkResponse(
            id=bookmark_orm.id,
            url=bookmark_orm.url,
            title=bookmark_orm.title,
            tags=bookmark_orm.tags or [],
            note=bookmark_orm.note or "",
            favicon=bookmark_orm.favicon or "",
            domain=bookmark_orm.domain or "",
            content=bookmark_orm.content or "",
            summary=bookmark_orm.summary or "",
            keywords=bookmark_orm.keywords or [],
            timestamp=bookmark_orm.timestamp,
            created_date=bookmark_orm.created_date or "",
            user_agent=bookmark_orm.user_agent or "",
            type=bookmark_orm.type or "bookmark",
            extracted_at=bookmark_orm.extracted_at or ""
        )
    
    def _orm_to_dict(self, bookmark_orm: BookmarkORM) -> Dict[str, Any]:
        """将ORM对象转换为字典（用于统计）"""
        return {
            "id": bookmark_orm.id,
            "url": bookmark_orm.url,
            "title": bookmark_orm.title,
            "tags": bookmark_orm.tags or [],
            "note": bookmark_orm.note or "",
            "favicon": bookmark_orm.favicon or "",
            "domain": bookmark_orm.domain or "",
            "content": bookmark_orm.content or "",
            "summary": bookmark_orm.summary or "",
            "keywords": bookmark_orm.keywords or [],
            "timestamp": bookmark_orm.timestamp.isoformat() if bookmark_orm.timestamp else "",
            "created_date": bookmark_orm.created_date or "",
            "user_agent": bookmark_orm.user_agent or "",
            "type": bookmark_orm.type or "bookmark",
            "extracted_at": bookmark_orm.extracted_at or ""
        }
    
    def _extract_domain(self, url: str) -> str:
        """从URL提取域名"""
        try:
            parsed = urlparse(url)
            return parsed.netloc.replace('www.', '')
        except Exception:
            return "" 