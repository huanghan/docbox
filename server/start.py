"""
启动脚本 - 检查数据库连接并启动服务
"""
import time
import sys
#from database import db
from database_sqlite import db
from config import API_CONFIG

def check_database_connection():
    """检查数据库连接"""
    max_retries = 5
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # 尝试连接数据库
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                print("✅ 数据库连接成功")
                return True
        except Exception as e:
            retry_count += 1
            print(f"❌ 数据库连接失败 (尝试 {retry_count}/{max_retries}): {e}")
            if retry_count < max_retries:
                print("⏳ 5秒后重试...")
                time.sleep(5)
    
    print("💥 数据库连接失败，请检查MySQL服务是否启动")
    return False

def start_server():
    """启动FastAPI服务器"""
    print("🚀 启动NoteDocs服务...")
    
    # 检查数据库连接
    if not check_database_connection():
        sys.exit(1)
    
    # 启动FastAPI服务器
    import uvicorn
    
    print(f"🌐 服务启动地址: http://{API_CONFIG['host']}:{API_CONFIG['port']}")
    print("📚 API文档地址: http://127.0.0.1:8001/docs")
    
    if API_CONFIG['debug']:
        # 开发模式：使用模块字符串启动，支持热重载
        uvicorn.run(
            "main:app",
            host=API_CONFIG['host'],
            port=API_CONFIG['port'],
            reload=True
        )
    else:
        # 生产模式：直接使用app对象
        from main import app
        uvicorn.run(
            app,
            host=API_CONFIG['host'],
            port=API_CONFIG['port'],
            reload=False
        )

if __name__ == "__main__":
    start_server() 