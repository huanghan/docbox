"""
文件操作工具函数
"""

import os
import json
import shutil
from datetime import datetime
from typing import Any, Dict, List


def ensure_directory_exists(directory: str) -> None:
    """确保目录存在"""
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)


def backup_file(file_path: str, backup_dir: str = "backups") -> str:
    """备份文件"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")
    
    ensure_directory_exists(backup_dir)
    
    # 生成备份文件名
    base_name = os.path.basename(file_path)
    name, ext = os.path.splitext(base_name)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{name}_{timestamp}{ext}"
    backup_path = os.path.join(backup_dir, backup_name)
    
    # 复制文件
    shutil.copy2(file_path, backup_path)
    
    return backup_path


def safe_json_load(file_path: str, default: Any = None) -> Any:
    """安全加载JSON文件"""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return default
    except (json.JSONDecodeError, FileNotFoundError, IOError) as e:
        print(f"加载JSON文件失败 {file_path}: {e}")
        return default


def safe_json_save(file_path: str, data: Any, backup: bool = True) -> bool:
    """安全保存JSON文件"""
    try:
        # 如果需要备份且文件存在
        if backup and os.path.exists(file_path):
            try:
                backup_file(file_path)
            except Exception as e:
                print(f"备份文件失败: {e}")
        
        # 确保目录存在
        directory = os.path.dirname(file_path)
        if directory:
            ensure_directory_exists(directory)
        
        # 保存文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        print(f"保存JSON文件失败 {file_path}: {e}")
        return False


def get_file_size_mb(file_path: str) -> float:
    """获取文件大小（MB）"""
    try:
        if os.path.exists(file_path):
            size_bytes = os.path.getsize(file_path)
            return size_bytes / (1024 * 1024)
        return 0.0
    except Exception:
        return 0.0


def cleanup_old_backups(backup_dir: str, keep_days: int = 30) -> None:
    """清理旧的备份文件"""
    if not os.path.exists(backup_dir):
        return
    
    current_time = datetime.now().timestamp()
    
    for filename in os.listdir(backup_dir):
        file_path = os.path.join(backup_dir, filename)
        
        if os.path.isfile(file_path):
            file_time = os.path.getmtime(file_path)
            days_old = (current_time - file_time) / (24 * 3600)
            
            if days_old > keep_days:
                try:
                    os.remove(file_path)
                    print(f"删除旧备份文件: {filename}")
                except Exception as e:
                    print(f"删除备份文件失败 {filename}: {e}") 