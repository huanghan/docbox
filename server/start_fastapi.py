"""
FastAPI收藏服务器启动脚本
"""

import uvicorn
from config import get_settings

if __name__ == "__main__":
    settings = get_settings()
    
    print("=" * 60)
    print(f"🚀 启动 {settings.app_name} v{settings.app_version}")
    print("=" * 60)
    print(f"📡 服务地址: http://{settings.host}:{settings.port}")
    print(f"📂 数据目录: {settings.data_dir}")
    print(f"🔧 调试模式: {'开启' if settings.debug else '关闭'}")
    print(f"🔒 认证要求: {'开启' if settings.require_auth else '关闭'}")
    print("=" * 60)
    print("🎯 可用端点:")
    print("   - GET  /          - 服务器首页")
    print("   - GET  /status    - 服务器状态")
    print("   - GET  /docs      - API文档 (调试模式)")
    print("   - POST /api/bookmarks    - 创建收藏")
    print("   - GET  /api/bookmarks    - 获取收藏列表")
    print("   - GET  /api/stats        - 获取统计信息")
    print("=" * 60)
    print("📝 按 Ctrl+C 停止服务器")
    print("-" * 60)
    
    try:
        uvicorn.run(
            "main:app",
            host=settings.host,
            port=settings.port,
            reload=settings.reload,
            log_level=settings.log_level.lower(),
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        exit(1) 