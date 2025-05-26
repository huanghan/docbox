"""
收藏API路由
"""

import math
import json
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Request, Depends, Query
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from models.bookmark import BookmarkCreate, BookmarkResponse, BookmarkUpdate
from models.common import PaginationParams, PaginatedResponse, PaginationInfo, SuccessResponse, ErrorResponse
from services.bookmark_service import BookmarkService
from services.stats_service import StatsService

router = APIRouter(prefix="/api", tags=["bookmarks"])

# 设置日志
logger = logging.getLogger(__name__)

# 依赖注入
def get_bookmark_service() -> BookmarkService:
    """获取收藏服务实例"""
    return BookmarkService()

def get_stats_service() -> StatsService:
    """获取统计服务实例"""
    return StatsService()


@router.post("/bookmarks", response_model=BookmarkResponse)
async def create_bookmark(
    bookmark_data: BookmarkCreate,
    request: Request,
    bookmark_service: BookmarkService = Depends(get_bookmark_service),
    stats_service: StatsService = Depends(get_stats_service)
):
    """创建新收藏"""
    try:
        # 获取用户代理
        user_agent = request.headers.get("user-agent", "")        
        # 创建收藏
        bookmark = bookmark_service.create_bookmark(bookmark_data, user_agent)
        
        print(f"✅ 收藏创建成功，ID: {bookmark.id}")
        print("=" * 80)
        
        # 更新统计信息
        bookmarks = bookmark_service.get_all_bookmarks()
        stats_service.generate_stats(bookmarks)
        
        return bookmark
        
    except Exception as e:
        print(f"❌ 创建收藏失败: {str(e)}")
        print(f"❌ 错误类型: {type(e).__name__}")
        import traceback
        print(f"❌ 错误堆栈: {traceback.format_exc()}")
        print("=" * 80)
        raise HTTPException(status_code=500, detail=f"创建收藏失败: {str(e)}")


@router.get("/bookmarks", response_model=PaginatedResponse[BookmarkResponse])
async def get_bookmarks(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    search: str = Query("", description="搜索关键词"),
    tag: str = Query("", description="标签过滤"),
    bookmark_service: BookmarkService = Depends(get_bookmark_service)
):
    """获取收藏列表"""
    try:
        params = PaginationParams(
            page=page,
            page_size=page_size,
            search=search,
            tag=tag
        )
        
        bookmarks, total = bookmark_service.get_bookmarks(params)
        pages = math.ceil(total / page_size) if total > 0 else 1
        
        pagination_info = PaginationInfo(
            page=page,
            page_size=page_size,
            total=total,
            pages=pages
        )
        
        return PaginatedResponse(
            data=bookmarks,
            pagination=pagination_info
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取收藏列表失败: {str(e)}")


@router.get("/bookmarks/{bookmark_id}", response_model=BookmarkResponse)
async def get_bookmark(
    bookmark_id: str,
    bookmark_service: BookmarkService = Depends(get_bookmark_service)
):
    """根据ID获取收藏"""
    bookmark = bookmark_service.get_bookmark_by_id(bookmark_id)
    
    if not bookmark:
        raise HTTPException(status_code=404, detail="收藏不存在")
    
    return bookmark


@router.put("/bookmarks/{bookmark_id}", response_model=BookmarkResponse)
async def update_bookmark(
    bookmark_id: str,
    update_data: BookmarkUpdate,
    bookmark_service: BookmarkService = Depends(get_bookmark_service),
    stats_service: StatsService = Depends(get_stats_service)
):
    """更新收藏"""
    bookmark = bookmark_service.update_bookmark(bookmark_id, update_data)
    
    if not bookmark:
        raise HTTPException(status_code=404, detail="收藏不存在")
    
    # 更新统计信息
    try:
        bookmarks = bookmark_service.get_all_bookmarks()
        stats_service.generate_stats(bookmarks)
    except Exception as e:
        print(f"更新统计信息失败: {e}")
    
    return bookmark


@router.delete("/bookmarks/{bookmark_id}", response_model=SuccessResponse)
async def delete_bookmark(
    bookmark_id: str,
    bookmark_service: BookmarkService = Depends(get_bookmark_service),
    stats_service: StatsService = Depends(get_stats_service)
):
    """删除收藏"""
    success = bookmark_service.delete_bookmark(bookmark_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="收藏不存在")
    
    # 更新统计信息
    try:
        bookmarks = bookmark_service.get_all_bookmarks()
        stats_service.generate_stats(bookmarks)
    except Exception as e:
        print(f"更新统计信息失败: {e}")
    
    return SuccessResponse(
        message="收藏删除成功",
        timestamp=datetime.now().isoformat()
    ) 