#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网页收藏助手服务器
提供API接口接收Chrome插件发送的收藏数据
"""

import json
import os
import datetime
import uuid
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('server.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class BookmarkServer(BaseHTTPRequestHandler):
    """收藏服务器处理类"""
    
    def __init__(self, *args, **kwargs):
        # 确保data目录存在
        self.data_dir = os.path.join(os.path.dirname(__file__), 'data')
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 数据文件路径
        self.bookmarks_file = os.path.join(self.data_dir, 'bookmarks.json')
        self.stats_file = os.path.join(self.data_dir, 'stats.json')
        
        super().__init__(*args, **kwargs)
    
    def do_OPTIONS(self):
        """处理预检请求"""
        self.send_cors_headers()
        self.end_headers()
    
    def do_POST(self):
        """处理POST请求"""
        try:
            # 解析URL路径
            parsed_path = urlparse(self.path)
            
            if parsed_path.path == '/api/bookmarks':
                self.handle_bookmark_request()
            else:
                self.send_error_response(404, '接口不存在')
                
        except Exception as e:
            logging.error(f"处理POST请求失败: {e}")
            self.send_error_response(500, f'服务器内部错误: {str(e)}')
    
    def do_GET(self):
        """处理GET请求"""
        try:
            parsed_path = urlparse(self.path)
            
            if parsed_path.path == '/api/bookmarks':
                self.handle_get_bookmarks()
            elif parsed_path.path == '/api/stats':
                self.handle_get_stats()
            elif parsed_path.path == '/' or parsed_path.path == '/status':
                self.handle_status()
            else:
                self.send_error_response(404, '接口不存在')
                
        except Exception as e:
            logging.error(f"处理GET请求失败: {e}")
            self.send_error_response(500, f'服务器内部错误: {str(e)}')
    
    def handle_bookmark_request(self):
        """处理收藏请求"""
        try:
            # 验证Authorization头
            auth_header = self.headers.get('Authorization')
            if not self.verify_auth(auth_header):
                self.send_error_response(401, 'API密钥无效')
                return
            
            # 读取请求数据
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # 解析JSON数据
            try:
                bookmark_data = json.loads(post_data.decode('utf-8'))
            except json.JSONDecodeError as e:
                self.send_error_response(400, f'JSON格式错误: {str(e)}')
                return
            
            # 验证必需字段
            required_fields = ['url', 'title']
            for field in required_fields:
                if field not in bookmark_data:
                    self.send_error_response(400, f'缺少必需字段: {field}')
                    return
            
            # 处理收藏数据
            processed_bookmark = self.process_bookmark(bookmark_data)
            
            # 保存到JSON文件
            self.save_bookmark(processed_bookmark)
            
            # 更新统计信息
            self.update_stats()
            
            # 返回成功响应
            response_data = {
                'success': True,
                'id': processed_bookmark['id'],
                'message': '收藏成功',
                'timestamp': processed_bookmark['timestamp']
            }
            
            self.send_json_response(200, response_data)
            logging.info(f"收藏成功: {bookmark_data['title']} - {bookmark_data['url']}")
            
        except Exception as e:
            logging.error(f"处理收藏请求失败: {e}")
            self.send_error_response(500, f'保存收藏失败: {str(e)}')
    
    def handle_get_bookmarks(self):
        """获取收藏列表"""
        try:
            # 读取查询参数
            parsed_path = urlparse(self.path)
            query_params = parse_qs(parsed_path.query)
            
            page = int(query_params.get('page', [1])[0])
            page_size = int(query_params.get('page_size', [20])[0])
            search = query_params.get('search', [''])[0]
            tag = query_params.get('tag', [''])[0]
            
            # 限制page_size
            page_size = min(page_size, 100)
            
            # 读取收藏数据
            bookmarks = self.load_bookmarks()
            
            # 过滤数据
            filtered_bookmarks = self.filter_bookmarks(bookmarks, search, tag)
            
            # 分页
            start_index = (page - 1) * page_size
            end_index = start_index + page_size
            page_bookmarks = filtered_bookmarks[start_index:end_index]
            
            response_data = {
                'success': True,
                'data': page_bookmarks,
                'pagination': {
                    'page': page,
                    'page_size': page_size,
                    'total': len(filtered_bookmarks),
                    'pages': (len(filtered_bookmarks) + page_size - 1) // page_size
                }
            }
            
            self.send_json_response(200, response_data)
            
        except Exception as e:
            logging.error(f"获取收藏列表失败: {e}")
            self.send_error_response(500, f'获取收藏列表失败: {str(e)}')
    
    def handle_get_stats(self):
        """获取统计信息"""
        try:
            stats = self.load_stats()
            self.send_json_response(200, stats)
        except Exception as e:
            logging.error(f"获取统计信息失败: {e}")
            self.send_error_response(500, f'获取统计信息失败: {str(e)}')
    
    def handle_status(self):
        """处理状态查询"""
        status_data = {
            'status': 'running',
            'message': '网页收藏助手服务器运行中',
            'version': '1.0.0',
            'timestamp': datetime.datetime.now().isoformat(),
            'endpoints': [
                'POST /api/bookmarks - 添加收藏',
                'GET /api/bookmarks - 获取收藏列表',
                'GET /api/stats - 获取统计信息',
                'GET /status - 服务器状态'
            ]
        }
        self.send_json_response(200, status_data)
    
    def process_bookmark(self, bookmark_data):
        """处理收藏数据"""
        processed = {
            'id': str(uuid.uuid4()),
            'url': bookmark_data['url'],
            'title': bookmark_data['title'],
            'tags': bookmark_data.get('tags', []),
            'note': bookmark_data.get('note', ''),
            'favicon': bookmark_data.get('favicon', ''),
            'domain': bookmark_data.get('domain', ''),
            'timestamp': datetime.datetime.now().isoformat(),
            'user_agent': self.headers.get('User-Agent', ''),
            'created_date': datetime.datetime.now().strftime('%Y-%m-%d'),
            'type': bookmark_data.get('type', 'bookmark')
        }
        
        # 如果是选中内容，添加content字段
        if 'content' in bookmark_data:
            processed['content'] = bookmark_data['content']
        
        return processed
    
    def save_bookmark(self, bookmark_data):
        """保存收藏到JSON文件"""
        try:
            # 读取现有数据
            bookmarks = self.load_bookmarks()
            
            # 添加新收藏
            bookmarks.append(bookmark_data)
            
            # 保存到文件
            with open(self.bookmarks_file, 'w', encoding='utf-8') as f:
                json.dump(bookmarks, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logging.error(f"保存收藏失败: {e}")
            raise
    
    def load_bookmarks(self):
        """从JSON文件加载收藏数据"""
        try:
            if os.path.exists(self.bookmarks_file):
                with open(self.bookmarks_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            logging.error(f"加载收藏数据失败: {e}")
            return []
    
    def filter_bookmarks(self, bookmarks, search, tag):
        """过滤收藏数据"""
        filtered = bookmarks
        
        # 搜索过滤
        if search:
            search_lower = search.lower()
            filtered = [
                b for b in filtered 
                if search_lower in b.get('title', '').lower() 
                or search_lower in b.get('url', '').lower()
                or search_lower in b.get('note', '').lower()
            ]
        
        # 标签过滤
        if tag:
            filtered = [
                b for b in filtered 
                if tag in b.get('tags', [])
            ]
        
        # 按时间倒序排列
        filtered.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return filtered
    
    def update_stats(self):
        """更新统计信息"""
        try:
            bookmarks = self.load_bookmarks()
            
            # 计算统计信息
            total_bookmarks = len(bookmarks)
            
            # 按日期统计
            date_counts = {}
            tag_counts = {}
            domain_counts = {}
            
            for bookmark in bookmarks:
                # 日期统计
                date = bookmark.get('created_date', 'unknown')
                date_counts[date] = date_counts.get(date, 0) + 1
                
                # 标签统计
                for tag in bookmark.get('tags', []):
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
                
                # 域名统计
                domain = bookmark.get('domain', 'unknown')
                domain_counts[domain] = domain_counts.get(domain, 0) + 1
            
            stats = {
                'total_bookmarks': total_bookmarks,
                'last_updated': datetime.datetime.now().isoformat(),
                'date_counts': date_counts,
                'top_tags': sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10],
                'top_domains': sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            }
            
            # 保存统计信息
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logging.error(f"更新统计信息失败: {e}")
    
    def load_stats(self):
        """加载统计信息"""
        try:
            if os.path.exists(self.stats_file):
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {'total_bookmarks': 0, 'message': '暂无数据'}
        except Exception as e:
            logging.error(f"加载统计信息失败: {e}")
            return {'error': str(e)}
    
    def verify_auth(self, auth_header):
        """验证API密钥"""
        # 这里可以配置API密钥验证
        # 目前允许无密钥访问，或者Bearer token格式
        if not auth_header:
            return True  # 允许无密钥访问
        
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
            # 这里可以添加token验证逻辑
            return True
        
        return True
    
    def send_cors_headers(self):
        """发送CORS头"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Max-Age', '86400')
    
    def send_json_response(self, status_code, data):
        """发送JSON响应"""
        self.send_response(status_code)
        self.send_cors_headers()
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        
        json_data = json.dumps(data, ensure_ascii=False, indent=2)
        self.wfile.write(json_data.encode('utf-8'))
    
    def send_error_response(self, status_code, message):
        """发送错误响应"""
        error_data = {
            'success': False,
            'error': message,
            'timestamp': datetime.datetime.now().isoformat()
        }
        self.send_json_response(status_code, error_data)
    
    def log_message(self, format, *args):
        """重写日志方法"""
        logging.info(f"{self.address_string()} - {format % args}")


def run_server(host='localhost', port=3000):
    """启动服务器"""
    server_address = (host, port)
    httpd = HTTPServer(server_address, BookmarkServer)
    
    print(f"🚀 网页收藏助手服务器启动成功!")
    print(f"📍 服务器地址: http://{host}:{port}")
    print(f"📋 状态查询: http://{host}:{port}/status")
    print(f"📚 收藏接口: POST http://{host}:{port}/api/bookmarks")
    print(f"📖 查看收藏: GET http://{host}:{port}/api/bookmarks")
    print(f"📊 统计信息: GET http://{host}:{port}/api/stats")
    print("按 Ctrl+C 停止服务器")
    print("-" * 50)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n⏹️  服务器已停止")
        httpd.server_close()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='网页收藏助手服务器')
    parser.add_argument('--host', default='localhost', help='服务器主机地址 (默认: localhost)')
    parser.add_argument('--port', type=int, default=3000, help='服务器端口 (默认: 3000)')
    
    args = parser.parse_args()
    
    run_server(args.host, args.port) 