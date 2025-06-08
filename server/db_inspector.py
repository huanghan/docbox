#!/usr/bin/env python3
"""
SQLite数据库检查工具
"""

import sqlite3
import json
from datetime import datetime
from config import get_settings


def connect_and_inspect():
    """连接数据库并检查内容"""
    settings = get_settings()
    db_path = f"{settings.data_dir}/bookmarks.db"
    
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # 使结果可以像字典一样访问
        cursor = conn.cursor()
        
        print(f"🗄️ 已连接到数据库: {db_path}")
        print("=" * 50)
        
        # 列出所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("📋 数据库中的表:")
        for table in tables:
            print(f"  - {table[0]}")
        
        print("\n" + "=" * 50)
        
        # 查看bookmarks表结构
        if any(table[0] == 'bookmarks' for table in tables):
            print("📊 bookmarks表结构:")
            cursor.execute("PRAGMA table_info(bookmarks);")
            columns = cursor.fetchall()
            
            for col in columns:
                print(f"  {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULL'} - {'PRIMARY KEY' if col[5] else ''}")
            
            print("\n" + "=" * 50)
            
            # 查看数据统计
            cursor.execute("SELECT COUNT(*) as total FROM bookmarks;")
            total = cursor.fetchone()[0]
            print(f"📈 总记录数: {total}")
            
            if total > 0:
                # 查看最近的5条记录
                print("\n🔍 最近5条记录:")
                cursor.execute("""
                    SELECT id, title, url, timestamp, tags 
                    FROM bookmarks 
                    ORDER BY timestamp DESC 
                    LIMIT 5
                """)
                
                recent_records = cursor.fetchall()
                for i, record in enumerate(recent_records, 1):
                    print(f"\n  {i}. {record['title']}")
                    print(f"     URL: {record['url']}")
                    print(f"     时间: {record['timestamp']}")
                    print(f"     标签: {record['tags']}")
                
                print("\n" + "=" * 50)
                
                # 统计按域名分组
                print("🌐 按域名统计:")
                cursor.execute("""
                    SELECT domain, COUNT(*) as count 
                    FROM bookmarks 
                    WHERE domain != '' 
                    GROUP BY domain 
                    ORDER BY count DESC 
                    LIMIT 10
                """)
                
                domain_stats = cursor.fetchall()
                for domain in domain_stats:
                    print(f"  {domain['domain']}: {domain['count']} 条")
                
                print("\n" + "=" * 50)
                
                # 统计按日期分组
                print("📅 按日期统计:")
                cursor.execute("""
                    SELECT created_date, COUNT(*) as count 
                    FROM bookmarks 
                    WHERE created_date != '' 
                    GROUP BY created_date 
                    ORDER BY created_date DESC 
                    LIMIT 10
                """)
                
                date_stats = cursor.fetchall()
                for date in date_stats:
                    print(f"  {date['created_date']}: {date['count']} 条")
        
        else:
            print("⚠️ 未找到bookmarks表")
    
    except sqlite3.Error as e:
        print(f"❌ 数据库错误: {e}")
    except Exception as e:
        print(f"❌ 发生错误: {e}")
    finally:
        if conn:
            conn.close()
            print("\n🔐 数据库连接已关闭")


def execute_custom_query():
    """执行自定义SQL查询"""
    settings = get_settings()
    db_path = f"{settings.data_dir}/bookmarks.db"
    
    print("\n" + "=" * 50)
    print("💡 可以执行自定义SQL查询:")
    print("   示例查询:")
    print("   SELECT * FROM bookmarks WHERE title LIKE '%Python%';")
    print("   SELECT COUNT(*) FROM bookmarks WHERE tags LIKE '%技术%';")
    print("   输入 'quit' 退出")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        while True:
            query = input("\n🔍 请输入SQL查询: ").strip()
            
            if query.lower() == 'quit':
                break
            
            if not query:
                continue
            
            try:
                cursor.execute(query)
                
                if query.upper().startswith('SELECT'):
                    results = cursor.fetchall()
                    if results:
                        print(f"\n📋 查询结果 ({len(results)} 条):")
                        for i, row in enumerate(results[:10], 1):  # 只显示前10条
                            print(f"  {i}. {dict(row)}")
                        if len(results) > 10:
                            print(f"  ... 还有 {len(results) - 10} 条结果")
                    else:
                        print("📭 无结果")
                else:
                    conn.commit()
                    print(f"✅ 查询执行成功，影响 {cursor.rowcount} 行")
                    
            except sqlite3.Error as e:
                print(f"❌ SQL错误: {e}")
    
    except Exception as e:
        print(f"❌ 发生错误: {e}")
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    print("🚀 SQLite数据库检查工具")
    connect_and_inspect()
    
    # 询问是否要执行自定义查询
    choice = input("\n❓ 是否要执行自定义SQL查询? (y/n): ").strip().lower()
    if choice == 'y':
        execute_custom_query()
    
    print("\n✨ 检查完成") 