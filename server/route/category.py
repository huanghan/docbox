"""
文档分类相关路由
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from route.models import CreateCategoryRequest, UpdateCategoryRequest, AddDocToCategoryRequest
from db.database_sqlite import db

router = APIRouter(prefix="/api/categories", tags=["categories"])

# ========== 分类管理接口 ==========

@router.get("", summary="获取用户的所有分类")
async def get_categories(
    uid: int = Query(..., description="用户ID")
):
    """按uid查询所有分类目录"""
    print(f"get_categories: uid={uid}")
    categories = db.get_categories_by_uid(uid)
    return {
        "success": True,
        "categories": categories,
        "count": len(categories)
    }

@router.post("", summary="创建分类")
async def create_category(request: CreateCategoryRequest):
    """创建新分类"""
    category_id = db.create_category(
        uid=request.uid,
        name=request.name,
        tags=request.tags,
        icon=request.icon
    )
    
    if category_id:
        return {
            "success": True, 
            "message": f"分类 '{request.name}' 创建成功",
            "category_id": category_id
        }
    else:
        raise HTTPException(status_code=500, detail="创建分类失败")

@router.put("/{category_id}", summary="修改分类信息")
async def update_category(
    category_id: int, 
    request: UpdateCategoryRequest,
    uid: int = Query(..., description="用户ID，用于权限验证")
):
    """修改分类目录信息（只能修改自己的分类）"""
    if not any([request.name, request.tags is not None, request.icon is not None]):
        raise HTTPException(status_code=400, detail="至少需要提供一个要更新的字段")
    
    success = db.update_category_name(
        category_id=category_id,
        uid=uid,
        name=request.name,
        tags=request.tags,
        icon=request.icon
    )
    
    if success:
        return {
            "success": True,
            "message": f"分类ID {category_id} 更新成功"
        }
    else:
        raise HTTPException(status_code=404, detail="分类不存在或无权限修改")

@router.delete("/{category_id}", summary="删除分类")
async def delete_category(
    category_id: int,
    uid: int = Query(..., description="用户ID，用于权限验证")
):
    """删除分类目录（只能删除自己的分类）"""
    success = db.delete_category(category_id, uid)
    
    if success:
        return {
            "success": True,
            "message": f"分类ID {category_id} 删除成功"
        }
    else:
        raise HTTPException(status_code=404, detail="分类不存在或无权限删除")

# ========== 分类-文档关联接口 ==========

@router.post("/{category_id}/docs", summary="给分类添加文档")
async def add_doc_to_category(
    category_id: int,
    request: AddDocToCategoryRequest
):
    """给分类目录增加文章"""
    success = db.add_doc_to_category(category_id, request.doc_id)
    
    if success:
        return {
            "success": True,
            "message": f"文档ID {request.doc_id} 已添加到分类ID {category_id}"
        }
    else:
        raise HTTPException(status_code=500, detail="添加文档到分类失败")

@router.delete("/{category_id}/docs/{doc_id}", summary="从分类中移除文档")
async def remove_doc_from_category(
    category_id: int,
    doc_id: int
):
    """删除分类目录下的文章"""
    success = db.remove_doc_from_category(category_id, doc_id)
    
    if success:
        return {
            "success": True,
            "message": f"文档ID {doc_id} 已从分类ID {category_id} 中移除"
        }
    else:
        raise HTTPException(status_code=404, detail="文档不在该分类中或操作失败")

@router.get("/{category_id}/docs", summary="获取分类下的所有文档")
async def get_docs_by_category(
    category_id: int,
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    offset: int = Query(0, ge=0, description="偏移量")
):
    """查询分类目录下的所有文章"""
    documents = db.get_docs_by_category(category_id, limit, offset)
    total_count = db.get_category_docs_count(category_id)
    
    return {
        "success": True,
        "documents": documents,
        "count": total_count,
        "limit": limit,
        "offset": offset,
        "category_id": category_id
    }

