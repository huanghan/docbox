"""
纯 FastAPI 接口服务
"""
from fastapi import FastAPI
from route import document_router
from route import category_router
from config import API_CONFIG

app = FastAPI(title="NoteDocs API", description="文档管理系统API", version="1.0.0")

# 注册路由
app.include_router(document_router)
app.include_router(category_router)

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