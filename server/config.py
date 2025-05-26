#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用配置
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用设置"""
    
    # 基本设置
    app_name: str = "Bookmark Server"
    app_version: str = "2.0.0"
    debug: bool = False
    
    # 服务器设置
    host: str = "localhost"
    port: int = 3000
    reload: bool = False
    
    # 数据存储设置
    data_dir: str = "data"
    
    # CORS设置
    cors_origins: List[str] = [
        "chrome-extension://*",
        "http://localhost:*",
        "http://127.0.0.1:*"
    ]
    cors_methods: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    cors_headers: List[str] = ["*"]
    
    # 认证设置
    api_keys: List[str] = []
    require_auth: bool = False
    
    # 日志设置
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    # 分页设置
    default_page_size: int = 20
    max_page_size: int = 100
    
    # 备份设置
    auto_backup: bool = True
    backup_keep_days: int = 30
    
    class Config:
        env_file = ".env"
        env_prefix = "BOOKMARK_"


# 全局设置实例
settings = Settings()


def get_settings() -> Settings:
    """获取设置实例"""
    return settings

print(f"📋 服务器配置:")
print(f"   - 主机: {settings.host}")
print(f"   - 端口: {settings.port}")
print(f"   - 数据目录: {settings.data_dir}")
print(f"   - API密钥验证: {'启用' if settings.require_auth else '禁用'}")
print(f"   - 日志级别: {settings.log_level}")
print("-" * 30) 