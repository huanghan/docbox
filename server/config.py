"""
数据库配置文件
"""
import os
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

# MySQL 数据库配置
MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', '123456'),
    'database': os.getenv('MYSQL_DATABASE', 'notedocs')
}

# FastAPI 配置
API_CONFIG = {
    'host': os.getenv('API_HOST', '127.0.0.1'),
    'port': int(os.getenv('API_PORT', 8000)),
    'debug': os.getenv('API_DEBUG', 'True').lower() == 'true'
} 