"""
收藏数据模型
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class BookmarkBase(BaseModel):
    """收藏基础模型"""
    url: str = Field(..., min_length=1, description="网页URL")
    title: str = Field(..., min_length=1, max_length=500, description="网页标题")
    tags: List[str] = Field(default=[], description="标签列表")
    note: str = Field(default="", description="备注信息")
    favicon: Optional[str] = Field(default="", description="网站图标URL")
    domain: Optional[str] = Field(default="", description="域名")
    content: Optional[str] = Field(default="", description="文章完整内容")
    summary: Optional[str] = Field(default="", description="文章摘要")
    keywords: List[str] = Field(default=[], description="文章关键词列表")


class BookmarkCreate(BookmarkBase):
    """创建收藏的请求模型"""
    type: str = Field(default="bookmark", description="收藏类型")
    extracted_at: Optional[str] = Field(default="", description="内容提取时间")


class BookmarkUpdate(BaseModel):
    """更新收藏的请求模型"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    tags: Optional[List[str]] = None
    note: Optional[str] = Field(None)
    content: Optional[str] = Field(None, description="文章完整内容")
    summary: Optional[str] = Field(None, description="文章摘要")
    keywords: Optional[List[str]] = Field(None, description="文章关键词列表")


class BookmarkResponse(BookmarkBase):
    """收藏响应模型"""
    id: str = Field(..., description="收藏ID")
    timestamp: datetime = Field(..., description="创建时间")
    created_date: str = Field(..., description="创建日期")
    user_agent: str = Field(default="", description="用户代理")
    type: str = Field(default="bookmark", description="收藏类型")
    extracted_at: Optional[str] = Field(default="", description="内容提取时间")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "url": "https://example.com",
                "title": "示例网页",
                "tags": ["示例", "测试"],
                "note": "这是一个示例收藏",
                "favicon": "https://example.com/favicon.ico",
                "domain": "example.com",
                "content": "这是文章的完整内容...",
                "summary": "这是文章的摘要...",
                "keywords": ["关键词1", "关键词2", "关键词3"],
                "timestamp": "2023-12-07T10:30:00.000Z",
                "created_date": "2023-12-07",
                "user_agent": "BookmarkExtension/1.0.0",
                "type": "bookmark",
                "extracted_at": "2023-12-07T10:30:00.000Z"
            }
        } 