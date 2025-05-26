"""
统计API路由
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any

from models.stats import StatsResponse
from services.bookmark_service import BookmarkService
from services.stats_service import StatsService

router = APIRouter(prefix="/api", tags=["stats"])

# 依赖注入
def get_bookmark_service() -> BookmarkService:
    """获取收藏服务实例"""
    return BookmarkService()

def get_stats_service() -> StatsService:
    """获取统计服务实例"""
    return StatsService()


@router.get("/stats", response_model=StatsResponse)
async def get_stats(
    bookmark_service: BookmarkService = Depends(get_bookmark_service),
    stats_service: StatsService = Depends(get_stats_service)
):
    """获取统计信息"""
    try:
        # 获取所有收藏数据
        bookmarks = bookmark_service.get_all_bookmarks()
        
        # 生成最新统计信息
        stats = stats_service.generate_stats(bookmarks)
        
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")


@router.get("/stats/cached", response_model=StatsResponse)
async def get_cached_stats(
    stats_service: StatsService = Depends(get_stats_service)
):
    """获取缓存的统计信息"""
    try:
        return stats_service.get_cached_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取缓存统计信息失败: {str(e)}")


@router.get("/stats/summary")
async def get_stats_summary(
    stats_service: StatsService = Depends(get_stats_service)
) -> Dict[str, Any]:
    """获取统计摘要"""
    try:
        return stats_service.get_stats_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计摘要失败: {str(e)}")


@router.post("/stats/refresh", response_model=StatsResponse)
async def refresh_stats(
    bookmark_service: BookmarkService = Depends(get_bookmark_service),
    stats_service: StatsService = Depends(get_stats_service)
):
    """刷新统计信息"""
    try:
        # 获取所有收藏数据
        bookmarks = bookmark_service.get_all_bookmarks()
        
        # 重新生成统计信息
        stats = stats_service.generate_stats(bookmarks)
        
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"刷新统计信息失败: {str(e)}") 