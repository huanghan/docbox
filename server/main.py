"""
FastAPI收藏服务器主应用
"""

import logging
import json
from datetime import datetime
from typing import List

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from starlette.middleware.base import BaseHTTPMiddleware

from config import get_settings
from api.bookmark_routes import router as bookmark_router
from api.stats_routes import router as stats_router
from models.common import StatusResponse
from utils.file_utils import ensure_directory_exists

# 获取配置
settings = get_settings()

# 创建FastAPI应用
app = FastAPI(
    title=settings.app_name,
    description="Chrome书签扩展的后端API服务",
    version=settings.app_version,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)

# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=settings.log_file if settings.log_file else None
)

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """自定义请求日志中间件"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = datetime.now()
        
        # 记录详细的请求信息（特别是POST请求）
        if request.method == "POST" and request.url.path.startswith("/api/"):
            print("🌐" + "=" * 80)
            print(f"📥 收到 {request.method} 请求: {request.url}")
            print(f"🔗 完整URL: {request.url}")
            print(f"📍 路径: {request.url.path}")
            print(f"❓ 查询参数: {request.url.query}")
            
            # 记录请求头
            print("📋 请求头:")
            for name, value in request.headers.items():
                print(f"   {name}: {value}")
            
            # 记录客户端信息
            print(f"🖥️ 客户端IP: {request.client.host if request.client else 'Unknown'}")
            print(f"🌐 用户代理: {request.headers.get('user-agent', 'Unknown')}")
            print(f"📝 内容类型: {request.headers.get('content-type', 'Unknown')}")
            print(f"📏 内容长度: {request.headers.get('content-length', 'Unknown')}")
            
            # 读取并记录原始请求体，然后重新设置
            try:
                body = await request.body()
                print(f"📦 原始请求体 (bytes): {body}")
                
                if body:
                    try:
                        raw_json = json.loads(body.decode('utf-8'))
                        print(f"📝 解析后的JSON数据:")
                        print(json.dumps(raw_json, indent=2, ensure_ascii=False))
                    except Exception as parse_error:
                        print(f"❌ JSON解析失败: {parse_error}")
                
                # 重新设置请求体，这样FastAPI可以再次读取
                async def receive():
                    return {"type": "http.request", "body": body}
                
                request._receive = receive
                
            except Exception as e:
                print(f"❌ 读取请求体失败: {e}")
            
            print("🌐" + "=" * 80)
        
        response = await call_next(request)
        
        process_time = (datetime.now() - start_time).total_seconds()
        
        # 记录响应信息
        if request.method == "POST" and request.url.path.startswith("/api/"):
            print("📤" + "=" * 80)
            print(f"📤 响应状态: {response.status_code}")
            print(f"⏱️ 处理时间: {process_time:.3f}s")
            print("📤" + "=" * 80)
        
        logger.info(
            f"{request.method} {request.url.path} - "
            f"状态码: {response.status_code} - "
            f"处理时间: {process_time:.3f}s"
        )
        
        return response


# 确保数据目录存在
ensure_directory_exists(settings.data_dir)

# 添加请求日志中间件
#app.add_middleware(RequestLoggingMiddleware)

# 注册路由
app.include_router(bookmark_router)
app.include_router(stats_router)


@app.get("/", response_class=HTMLResponse)
async def root():
    """服务器首页"""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{settings.app_name}</title>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 40px 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                min-height: 100vh;
            }}
            .container {{
                background: rgba(255, 255, 255, 0.1);
                padding: 30px;
                border-radius: 15px;
                backdrop-filter: blur(10px);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            }}
            h1 {{
                text-align: center;
                margin-bottom: 30px;
                font-size: 2.5em;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
            }}
            .status {{
                background: rgba(255, 255, 255, 0.1);
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
            }}
            .endpoints {{
                background: rgba(255, 255, 255, 0.1);
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
            }}
            ul {{
                list-style-type: none;
                padding: 0;
            }}
            li {{
                margin: 10px 0;
                padding: 10px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 5px;
                font-family: monospace;
            }}
            .method {{
                color: #4fc3f7;
                font-weight: bold;
            }}
            .footer {{
                text-align: center;
                margin-top: 30px;
                font-size: 0.9em;
                opacity: 0.8;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📚 {settings.app_name}</h1>
            
            <div class="status">
                <h3>🟢 服务状态</h3>
                <p><strong>版本:</strong> {settings.app_version}</p>
                <p><strong>运行时间:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>端口:</strong> {settings.port}</p>
            </div>
            
            <div class="endpoints">
                <h3>🚀 API端点</h3>
                <ul>
                    <li><span class="method">POST</span> /api/bookmarks - 创建收藏</li>
                    <li><span class="method">GET</span> /api/bookmarks - 获取收藏列表</li>
                    <li><span class="method">GET</span> /api/bookmarks/{{id}} - 获取单个收藏</li>
                    <li><span class="method">PUT</span> /api/bookmarks/{{id}} - 更新收藏</li>
                    <li><span class="method">DELETE</span> /api/bookmarks/{{id}} - 删除收藏</li>
                    <li><span class="method">GET</span> /api/stats - 获取统计信息</li>
                    <li><span class="method">GET</span> /status - 服务器状态</li>
                </ul>
            </div>
            
            {"<p><a href='/docs' style='color: #4fc3f7;'>📖 API文档</a></p>" if settings.debug else ""}
            
            <div class="footer">
                <p>💡 Chrome书签扩展后端服务</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content


@app.get("/status", response_model=StatusResponse)
async def get_status():
    """获取服务器状态"""
    endpoints = [
        "POST /api/bookmarks",
        "GET /api/bookmarks",
        "GET /api/bookmarks/{id}",
        "PUT /api/bookmarks/{id}",
        "DELETE /api/bookmarks/{id}",
        "GET /api/stats",
        "GET /api/stats/cached",
        "GET /api/stats/summary",
        "POST /api/stats/refresh",
        "GET /status"
    ]
    
    return StatusResponse(
        status="running",
        message="服务器正常运行",
        version=settings.app_version,
        timestamp=datetime.now().isoformat(),
        endpoints=endpoints
    )


@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """404错误处理"""
    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "error": "资源不存在",
            "detail": "请检查请求路径是否正确",
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(422)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    """422验证错误处理"""
    print("❌" + "=" * 80)
    print("❌ Pydantic验证错误")
    print("❌" + "=" * 80)
    
    # 获取原始请求体用于调试
    try:
        body = await request.body()
        print(f"📦 原始请求体: {body}")
        
        import json
        if body:
            try:
                raw_json = json.loads(body.decode('utf-8'))
                print(f"📝 解析后的JSON:")
                print(json.dumps(raw_json, indent=2, ensure_ascii=False))
            except Exception as parse_error:
                print(f"❌ JSON解析失败: {parse_error}")
    except Exception as e:
        print(f"❌ 获取请求体失败: {e}")
    
    print(f"❌ 验证错误详情:")
    for error in exc.errors():
        print(f"   字段: {error.get('loc', 'Unknown')}")
        print(f"   错误: {error.get('msg', 'Unknown')}")
        print(f"   类型: {error.get('type', 'Unknown')}")
        print(f"   输入: {error.get('input', 'Unknown')}")
        print("   ---")
    
    print("❌" + "=" * 80)
    
    logger.error(f"请求验证失败: {exc.errors()}")
    
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": "请求数据验证失败",
            "detail": exc.errors(),
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: Exception):
    """500错误处理"""
    logger.error(f"服务器内部错误: {str(exc)}")
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "服务器内部错误",
            "detail": str(exc) if settings.debug else "请联系管理员",
            "timestamp": datetime.now().isoformat()
        }
    )





if __name__ == "__main__":
    import uvicorn
    
    print(f"🚀 启动 {settings.app_name} v{settings.app_version}")
    print(f"📡 服务地址: http://{settings.host}:{settings.port}")
    print(f"📂 数据目录: {settings.data_dir}")
    print("-" * 50)
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower()
    ) 