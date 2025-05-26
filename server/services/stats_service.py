"""
统计服务
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Tuple, Any

from models.stats import StatsResponse
from utils.file_utils import ensure_directory_exists


class StatsService:
    """统计服务类"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.stats_file = os.path.join(data_dir, "stats.json")
        ensure_directory_exists(data_dir)
    
    def generate_stats(self, bookmarks: List[Dict[str, Any]]) -> StatsResponse:
        """生成统计信息"""
        total_bookmarks = len(bookmarks)
        
        # 初始化计数器
        date_counts: Dict[str, int] = {}
        tag_counts: Dict[str, int] = {}
        domain_counts: Dict[str, int] = {}
        
        # 统计数据
        for bookmark in bookmarks:
            # 日期统计
            date = bookmark.get('created_date', 'unknown')
            date_counts[date] = date_counts.get(date, 0) + 1
            
            # 标签统计
            for tag in bookmark.get('tags', []):
                if tag:  # 忽略空标签
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
            
            # 域名统计
            domain = bookmark.get('domain', 'unknown')
            if domain:  # 忽略空域名
                domain_counts[domain] = domain_counts.get(domain, 0) + 1
        
        # 生成排行榜（取前10）
        top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        top_domains = sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        stats = StatsResponse(
            total_bookmarks=total_bookmarks,
            last_updated=datetime.now().isoformat(),
            date_counts=date_counts,
            top_tags=top_tags,
            top_domains=top_domains
        )
        
        # 保存统计数据
        self._save_stats(stats.model_dump())
        
        return stats
    
    def get_cached_stats(self) -> StatsResponse:
        """获取缓存的统计信息"""
        try:
            if os.path.exists(self.stats_file):
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    stats_data = json.load(f)
                return StatsResponse(**stats_data)
            else:
                # 返回默认统计信息
                return StatsResponse(
                    total_bookmarks=0,
                    last_updated=datetime.now().isoformat(),
                    date_counts={},
                    top_tags=[],
                    top_domains=[]
                )
        except Exception as e:
            print(f"加载统计数据失败: {e}")
            return StatsResponse(
                total_bookmarks=0,
                last_updated=datetime.now().isoformat(),
                date_counts={},
                top_tags=[],
                top_domains=[]
            )
    
    def _save_stats(self, stats_data: Dict[str, Any]) -> None:
        """保存统计数据到文件"""
        try:
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存统计数据失败: {e}")
    
    def get_stats_summary(self) -> Dict[str, Any]:
        """获取统计摘要"""
        stats = self.get_cached_stats()
        
        # 计算一些额外的统计信息
        today = datetime.now().strftime("%Y-%m-%d")
        today_bookmarks = stats.date_counts.get(today, 0)
        
        # 计算最近7天的收藏数
        recent_days = []
        for i in range(7):
            date = datetime.now().replace(day=datetime.now().day - i).strftime("%Y-%m-%d")
            try:
                count = stats.date_counts.get(date, 0)
                recent_days.append({"date": date, "count": count})
            except:
                recent_days.append({"date": date, "count": 0})
        
        return {
            "total_bookmarks": stats.total_bookmarks,
            "today_bookmarks": today_bookmarks,
            "recent_days": recent_days,
            "total_tags": len(stats.top_tags),
            "total_domains": len(stats.top_domains),
            "last_updated": stats.last_updated
        } 