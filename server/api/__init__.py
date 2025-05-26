"""
API路由包
"""

from .bookmark_routes import router as bookmark_router
from .stats_routes import router as stats_router

__all__ = ["bookmark_router", "stats_router"] 