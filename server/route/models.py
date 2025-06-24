"""
数据模型定义
"""
from pydantic import BaseModel
from typing import Optional

class WriteDocumentRequest(BaseModel):
    uid: int
    url: str
    title: str
    summary: str
    content: str
    source: str = ""
    favicon: str = ""
    tags: str = ""
    evaluate: int = 0

class UpdateDocumentRequest(BaseModel):
    uid: Optional[int] = None
    url: Optional[str] = None
    title: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    source: Optional[str] = None
    favicon: Optional[str] = None
    tags: Optional[str] = None
    evaluate: Optional[int] = None

class CreateCategoryRequest(BaseModel):
    uid: int
    name: str
    tags: str = ""
    icon: str = ""

class UpdateCategoryRequest(BaseModel):
    name: Optional[str] = None
    tags: Optional[str] = None
    icon: Optional[str] = None

class AddDocToCategoryRequest(BaseModel):
    doc_id: int 

class WriteCategoryRequest(BaseModel):
    uid: int
    name: str
    tags: str = ""
    icon: str = ""

class UpdateCategoryRequest(BaseModel):
    uid: Optional[int] = None
    name: Optional[str] = None