"""
通用数据模型
"""

from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel, Field

T = TypeVar('T')


class PaginationParams(BaseModel):
    """分页参数"""
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页数量")
    search: str = Field(default="", description="搜索关键词")
    tag: str = Field(default="", description="标签过滤")


class PaginationInfo(BaseModel):
    """分页信息"""
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    total: int = Field(..., description="总记录数")
    pages: int = Field(..., description="总页数")


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应模型"""
    success: bool = Field(default=True, description="是否成功")
    data: List[T] = Field(..., description="数据列表")
    pagination: PaginationInfo = Field(..., description="分页信息")


class StatusResponse(BaseModel):
    """状态响应模型"""
    status: str = Field(..., description="服务状态")
    message: str = Field(..., description="状态消息")
    version: str = Field(..., description="版本号")
    timestamp: str = Field(..., description="当前时间")
    endpoints: List[str] = Field(..., description="可用端点")


class ErrorResponse(BaseModel):
    """错误响应模型"""
    success: bool = Field(default=False, description="是否成功")
    error: str = Field(..., description="错误信息")
    timestamp: str = Field(..., description="错误时间")
    detail: Optional[str] = Field(default=None, description="详细错误信息")


class SuccessResponse(BaseModel):
    """成功响应模型"""
    success: bool = Field(default=True, description="是否成功")
    message: str = Field(..., description="成功消息")
    data: Optional[dict] = Field(default=None, description="响应数据")
    timestamp: str = Field(..., description="响应时间") 