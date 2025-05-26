"""
收藏服务
"""

import json
import os
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

from models.bookmark import BookmarkCreate, BookmarkResponse, BookmarkUpdate
from models.common import PaginationParams
from utils.file_utils import ensure_directory_exists


class BookmarkService:
    """收藏服务类"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.bookmarks_file = os.path.join(data_dir, "bookmarks.json")
        ensure_directory_exists(data_dir)
    
    def create_bookmark(self, bookmark_data: BookmarkCreate, user_agent: str = "") -> BookmarkResponse:
        """创建新收藏"""
        # 生成收藏数据
        bookmark_dict = {
            "id": str(uuid.uuid4()),
            "url": str(bookmark_data.url),
            "title": bookmark_data.title,
            "tags": bookmark_data.tags,
            "note": bookmark_data.note,
            "favicon": bookmark_data.favicon or "",
            "domain": bookmark_data.domain or self._extract_domain(str(bookmark_data.url)),
            "timestamp": datetime.now().isoformat(),
            "created_date": datetime.now().strftime("%Y-%m-%d"),
            "user_agent": user_agent,
            "type": bookmark_data.type,
            "content": bookmark_data.content or "",
            "summary": bookmark_data.summary or "",
            "keywords": bookmark_data.keywords or [],
            "extracted_at": bookmark_data.extracted_at or ""
        }
        
        # 保存到文件
        bookmarks = self._load_bookmarks()
        bookmarks.append(bookmark_dict)
        self._save_bookmarks(bookmarks)
        
        return BookmarkResponse(**bookmark_dict)
    
    def get_bookmarks(self, params: PaginationParams) -> tuple[List[BookmarkResponse], int]:
        """获取收藏列表"""
        bookmarks = self._load_bookmarks()
        
        # 过滤
        filtered_bookmarks = self._filter_bookmarks(bookmarks, params.search, params.tag)
        
        # 排序（按时间倒序）
        filtered_bookmarks.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        # 分页
        total = len(filtered_bookmarks)
        start_index = (params.page - 1) * params.page_size
        end_index = start_index + params.page_size
        page_bookmarks = filtered_bookmarks[start_index:end_index]
        
        # 转换为响应模型
        bookmark_responses = [BookmarkResponse(**bookmark) for bookmark in page_bookmarks]
        
        return bookmark_responses, total
    
    def get_bookmark_by_id(self, bookmark_id: str) -> Optional[BookmarkResponse]:
        """根据ID获取收藏"""
        bookmarks = self._load_bookmarks()
        
        for bookmark in bookmarks:
            if bookmark.get("id") == bookmark_id:
                return BookmarkResponse(**bookmark)
        
        return None
    
    def update_bookmark(self, bookmark_id: str, update_data: BookmarkUpdate) -> Optional[BookmarkResponse]:
        """更新收藏"""
        bookmarks = self._load_bookmarks()
        
        for i, bookmark in enumerate(bookmarks):
            if bookmark.get("id") == bookmark_id:
                # 更新字段
                if update_data.title is not None:
                    bookmark["title"] = update_data.title
                if update_data.tags is not None:
                    bookmark["tags"] = update_data.tags
                if update_data.note is not None:
                    bookmark["note"] = update_data.note
                if update_data.content is not None:
                    bookmark["content"] = update_data.content
                if update_data.summary is not None:
                    bookmark["summary"] = update_data.summary
                if update_data.keywords is not None:
                    bookmark["keywords"] = update_data.keywords
                
                bookmarks[i] = bookmark
                self._save_bookmarks(bookmarks)
                
                return BookmarkResponse(**bookmark)
        
        return None
    
    def delete_bookmark(self, bookmark_id: str) -> bool:
        """删除收藏"""
        bookmarks = self._load_bookmarks()
        
        for i, bookmark in enumerate(bookmarks):
            if bookmark.get("id") == bookmark_id:
                del bookmarks[i]
                self._save_bookmarks(bookmarks)
                return True
        
        return False
    
    def get_all_bookmarks(self) -> List[Dict[str, Any]]:
        """获取所有收藏（用于统计）"""
        return self._load_bookmarks()
    
    def _load_bookmarks(self) -> List[Dict[str, Any]]:
        """从文件加载收藏数据"""
        try:
            if os.path.exists(self.bookmarks_file):
                with open(self.bookmarks_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"加载收藏数据失败: {e}")
            return []
    
    def _save_bookmarks(self, bookmarks: List[Dict[str, Any]]) -> None:
        """保存收藏数据到文件"""
        try:
            with open(self.bookmarks_file, 'w', encoding='utf-8') as f:
                json.dump(bookmarks, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存收藏数据失败: {e}")
            raise
    
    def _filter_bookmarks(self, bookmarks: List[Dict[str, Any]], search: str, tag: str) -> List[Dict[str, Any]]:
        """过滤收藏数据"""
        filtered = bookmarks
        
        # 搜索过滤
        if search:
            search_lower = search.lower()
            filtered = [
                b for b in filtered 
                if search_lower in b.get('title', '').lower() 
                or search_lower in b.get('url', '').lower()
                or search_lower in b.get('note', '').lower()
                or search_lower in b.get('content', '').lower()
                or search_lower in b.get('summary', '').lower()
                or any(search_lower in keyword.lower() for keyword in b.get('keywords', []))
            ]
        
        # 标签过滤
        if tag:
            filtered = [
                b for b in filtered 
                if tag in b.get('tags', [])
            ]
        
        return filtered
    
    def _extract_domain(self, url: str) -> str:
        """从URL提取域名"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc.replace('www.', '')
        except Exception:
            return "" 