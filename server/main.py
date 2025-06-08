"""
纯 FastAPI 接口服务
"""
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
#from database import db
from database_sqlite import db
from config import API_CONFIG

app = FastAPI(title="NoteDocs API", description="文档管理系统API", version="1.0.0")

# 请求模型
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

# 文档CRUD接口
@app.post("/api/documents", summary="创建文档")
async def create_document(request: WriteDocumentRequest):
    """创建新文档"""
    success = db.write_document(
        uid=request.uid,
        url=request.url,
        title=request.title,
        summary=request.summary,
        content=request.content,
        source=request.source,
        favicon=request.favicon,
        tags=request.tags,
        evaluate=request.evaluate
    )
    if success:
        return {"success": True, "message": f"Document '{request.title}' created successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to create document")

@app.get("/api/documents/id/{doc_id}", summary="根据ID获取文档")
async def get_document_by_id(doc_id: int):
    """根据ID获取文档"""
    document = db.read_document_by_id(doc_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@app.get("/api/documents", summary="列出文档")
async def list_documents(
    uid: Optional[int] = Query(None, description="用户ID过滤"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    offset: int = Query(0, ge=0, description="偏移量")
):
    """列出文档（支持分页和用户过滤）"""
    documents = db.list_documents(uid=uid, limit=limit, offset=offset)
    total_count = db.get_documents_count(uid=uid)
    return {
        "documents": documents, 
        "count": total_count,
        "limit": limit,
        "offset": offset
    }

@app.put("/api/documents/id/{doc_id}", summary="更新文档")
async def update_document(doc_id: int, request: UpdateDocumentRequest):
    """更新文档（通过ID）"""
    
    print(f"更新文档ID: {doc_id}")
    #print(f"接收到的请求数据: {request.dict()}")
    
    # 先获取原文档
    existing_doc = db.read_document_by_id(doc_id)
    if existing_doc is None:
        print(f"错误: 文档ID {doc_id} 不存在")
        raise HTTPException(status_code=404, detail="Document not found")
        
    # 合并更新数据
    updated_data = {
        "uid": request.uid if request.uid is not None else existing_doc["uid"],
        "url": request.url if request.url is not None else existing_doc["url"],
        "title": request.title if request.title is not None else existing_doc["title"],
        "summary": request.summary if request.summary is not None else existing_doc["summary"],
        "content": request.content if request.content is not None else existing_doc["content"],
        "source": request.source if request.source is not None else existing_doc["source"],
        "favicon": request.favicon if request.favicon is not None else existing_doc["favicon"],
        "tags": request.tags if request.tags is not None else existing_doc["tags"],
        "evaluate": request.evaluate if request.evaluate is not None else existing_doc["evaluate"]
    }
    
     
    
    # 检查内容是否真的有变化
    if request.content is not None:
        print(f"内容更新: 原内容长度={len(existing_doc.get('content', ''))}, 新内容长度={len(request.content)}")
        print(f"内容是否相同: {existing_doc.get('content', '') == request.content}")
    
    success = db.update_document_by_id(doc_id, **updated_data)
    print(f"数据库更新结果: {success}")
    
    if success:
        # 验证更新后的数据
        updated_doc = db.read_document_by_id(doc_id)
        
        return {"success": True, "message": f"Document with ID {doc_id} updated successfully"}
    else:
        print(f"错误: 数据库更新失败")
        raise HTTPException(status_code=500, detail="Failed to update document")


@app.delete("/api/documents/id/{doc_id}", summary="根据ID删除文档")
async def delete_document_by_id(doc_id: int):
    """根据ID删除文档"""
    success = db.delete_document_by_id(doc_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"success": True, "message": f"Document with ID {doc_id} deleted successfully"}

# 搜索和查询接口
@app.get("/api/documents/search", summary="搜索文档")
async def search_documents(
    keyword: str = Query(..., description="搜索关键词"),
    uid: Optional[int] = Query(None, description="用户ID过滤"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    offset: int = Query(0, ge=0, description="偏移量")
):
    """搜索文档（支持多字段搜索、用户过滤和分页）"""
    results = db.search_documents(keyword=keyword, uid=uid, limit=limit, offset=offset)
    return {
        "results": results, 
        "count": len(results),
        "keyword": keyword,
        "limit": limit,
        "offset": offset
    }

@app.get("/api/documents/tags/{tag}", summary="根据标签获取文档")
async def get_documents_by_tag(
    tag: str,
    uid: Optional[int] = Query(None, description="用户ID过滤"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    offset: int = Query(0, ge=0, description="偏移量")
):
    """根据标签获取文档"""
    results = db.get_documents_by_tag(tag=tag, uid=uid, limit=limit, offset=offset)
    return {
        "results": results,
        "count": len(results),
        "tag": tag,
        "limit": limit,
        "offset": offset
    }

 

# 系统接口
@app.get("/health", summary="健康检查")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "service": "NoteDocs API"}

@app.get("/", summary="API信息")
async def root():
    """API根路径"""
    return {
        "message": "Welcome to NoteDocs API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=API_CONFIG['host'], 
        port=API_CONFIG['port'],
        reload=API_CONFIG['debug']
    ) 