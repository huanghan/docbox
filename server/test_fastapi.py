"""
FastAPI服务器测试脚本
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Any

import httpx


class BookmarkServerTester:
    """收藏服务器测试类"""
    
    def __init__(self, base_url: str = "http://localhost:3000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self.test_bookmark_id = None
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def test_server_status(self) -> bool:
        """测试服务器状态"""
        try:
            response = await self.client.get(f"{self.base_url}/status")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 服务器状态: {data.get('status', 'unknown')}")
                print(f"   版本: {data.get('version', 'unknown')}")
                print(f"   消息: {data.get('message', 'unknown')}")
                return True
            else:
                print(f"❌ 服务器状态检查失败: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 服务器连接失败: {e}")
            return False
    
    async def test_create_bookmark(self) -> bool:
        """测试创建收藏"""
        try:
            bookmark_data = {
                "url": "https://fastapi.tiangolo.com/",
                "title": "FastAPI官方文档",
                "tags": ["Python", "FastAPI", "API", "文档"],
                "note": "现代、快速的Python Web框架",
                "favicon": "https://fastapi.tiangolo.com/img/favicon.png",
                "domain": "fastapi.tiangolo.com",
                "type": "bookmark",
                "content": "FastAPI框架，用于构建API"
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/bookmarks",
                json=bookmark_data
            )
            
            if response.status_code == 200:
                data = response.json()
                self.test_bookmark_id = data.get("id")
                print(f"✅ 创建收藏成功")
                print(f"   ID: {self.test_bookmark_id}")
                print(f"   标题: {data.get('title', 'unknown')}")
                print(f"   URL: {data.get('url', 'unknown')}")
                print(f"   标签数: {len(data.get('tags', []))}")
                return True
            else:
                print(f"❌ 创建收藏失败: HTTP {response.status_code}")
                print(f"   响应: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 创建收藏异常: {e}")
            return False
    
    async def test_get_bookmarks(self) -> bool:
        """测试获取收藏列表"""
        try:
            # 测试基本列表
            response = await self.client.get(f"{self.base_url}/api/bookmarks")
            
            if response.status_code == 200:
                data = response.json()
                bookmarks = data.get("data", [])
                pagination = data.get("pagination", {})
                
                print(f"✅ 获取收藏列表成功")
                print(f"   总数: {pagination.get('total', 0)}")
                print(f"   当前页: {pagination.get('page', 1)}")
                print(f"   每页数量: {pagination.get('page_size', 20)}")
                print(f"   本页收藏数: {len(bookmarks)}")
                
                # 测试搜索
                if bookmarks:
                    search_response = await self.client.get(
                        f"{self.base_url}/api/bookmarks?search=FastAPI"
                    )
                    
                    if search_response.status_code == 200:
                        search_data = search_response.json()
                        search_results = search_data.get("data", [])
                        print(f"   搜索结果数: {len(search_results)}")
                
                return True
            else:
                print(f"❌ 获取收藏列表失败: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 获取收藏列表异常: {e}")
            return False
    
    async def test_get_single_bookmark(self) -> bool:
        """测试获取单个收藏"""
        if not self.test_bookmark_id:
            print("⚠️  跳过单个收藏测试: 没有测试收藏ID")
            return True
        
        try:
            response = await self.client.get(
                f"{self.base_url}/api/bookmarks/{self.test_bookmark_id}"
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 获取单个收藏成功")
                print(f"   ID: {data.get('id', 'unknown')}")
                print(f"   标题: {data.get('title', 'unknown')}")
                return True
            else:
                print(f"❌ 获取单个收藏失败: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 获取单个收藏异常: {e}")
            return False
    
    async def test_update_bookmark(self) -> bool:
        """测试更新收藏"""
        if not self.test_bookmark_id:
            print("⚠️  跳过更新收藏测试: 没有测试收藏ID")
            return True
        
        try:
            update_data = {
                "title": "FastAPI官方文档 - 已更新",
                "tags": ["Python", "FastAPI", "API", "文档", "更新"],
                "note": "现代、快速的Python Web框架 - 测试更新"
            }
            
            response = await self.client.put(
                f"{self.base_url}/api/bookmarks/{self.test_bookmark_id}",
                json=update_data
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 更新收藏成功")
                print(f"   新标题: {data.get('title', 'unknown')}")
                print(f"   新标签数: {len(data.get('tags', []))}")
                return True
            else:
                print(f"❌ 更新收藏失败: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 更新收藏异常: {e}")
            return False
    
    async def test_get_stats(self) -> bool:
        """测试获取统计信息"""
        try:
            # 测试实时统计
            response = await self.client.get(f"{self.base_url}/api/stats")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 获取统计信息成功")
                print(f"   总收藏数: {data.get('total_bookmarks', 0)}")
                print(f"   热门标签数: {len(data.get('top_tags', []))}")
                print(f"   热门域名数: {len(data.get('top_domains', []))}")
                
                # 测试缓存统计
                cached_response = await self.client.get(f"{self.base_url}/api/stats/cached")
                if cached_response.status_code == 200:
                    print(f"   缓存统计: ✅")
                
                # 测试统计摘要
                summary_response = await self.client.get(f"{self.base_url}/api/stats/summary")
                if summary_response.status_code == 200:
                    summary_data = summary_response.json()
                    print(f"   今日收藏数: {summary_data.get('today_bookmarks', 0)}")
                
                return True
            else:
                print(f"❌ 获取统计信息失败: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 获取统计信息异常: {e}")
            return False
    
    async def test_homepage(self) -> bool:
        """测试首页"""
        try:
            response = await self.client.get(f"{self.base_url}/")
            
            if response.status_code == 200:
                content = response.text
                if "Bookmark Server" in content:
                    print(f"✅ 首页访问成功")
                    return True
                else:
                    print(f"❌ 首页内容异常")
                    return False
            else:
                print(f"❌ 首页访问失败: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 首页访问异常: {e}")
            return False
    
    async def run_all_tests(self) -> bool:
        """运行所有测试"""
        print("🧪 开始FastAPI服务器测试")
        print("=" * 50)
        
        tests = [
            ("服务器状态", self.test_server_status),
            ("首页访问", self.test_homepage),
            ("创建收藏", self.test_create_bookmark),
            ("获取收藏列表", self.test_get_bookmarks),
            ("获取单个收藏", self.test_get_single_bookmark),
            ("更新收藏", self.test_update_bookmark),
            ("获取统计信息", self.test_get_stats),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🔄 测试: {test_name}")
            print("-" * 30)
            
            try:
                start_time = time.time()
                result = await test_func()
                end_time = time.time()
                
                if result:
                    passed += 1
                    print(f"   ⏱️  耗时: {end_time - start_time:.3f}s")
                else:
                    print(f"   ❌ 测试失败")
                    
            except Exception as e:
                print(f"   💥 测试异常: {e}")
        
        print("\n" + "=" * 50)
        print(f"📊 测试结果: {passed}/{total} 通过")
        
        if passed == total:
            print("🎉 所有测试通过！")
            return True
        else:
            print("⚠️  部分测试失败")
            return False


async def main():
    """主函数"""
    print(f"⏰ 测试开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    async with BookmarkServerTester() as tester:
        success = await tester.run_all_tests()
        
        if success:
            print("\n✅ 所有测试完成，服务器运行正常！")
            exit(0)
        else:
            print("\n❌ 测试失败，请检查服务器状态")
            exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 