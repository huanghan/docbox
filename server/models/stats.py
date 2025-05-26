"""
统计数据模型
"""

from typing import Dict, List, Tuple
from pydantic import BaseModel, Field


class StatsResponse(BaseModel):
    """统计信息响应模型"""
    total_bookmarks: int = Field(..., description="总收藏数")
    last_updated: str = Field(..., description="最后更新时间")
    date_counts: Dict[str, int] = Field(default={}, description="按日期统计")
    top_tags: List[Tuple[str, int]] = Field(default=[], description="热门标签")
    top_domains: List[Tuple[str, int]] = Field(default=[], description="热门域名")

    class Config:
        json_schema_extra = {
            "example": {
                "total_bookmarks": 100,
                "last_updated": "2023-12-07T10:30:00.000Z",
                "date_counts": {
                    "2023-12-07": 10,
                    "2023-12-06": 5
                },
                "top_tags": [
                    ["开发", 20],
                    ["技术", 15],
                    ["工具", 10]
                ],
                "top_domains": [
                    ["github.com", 15],
                    ["stackoverflow.com", 10],
                    ["google.com", 8]
                ]
            }
        } 