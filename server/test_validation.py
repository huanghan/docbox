#!/usr/bin/env python3
"""
测试Pydantic模型验证
"""

import json
from models.bookmark import BookmarkCreate

# 从Chrome插件发送的实际数据
test_data = {
    "url": "file:///G:/docbox/chrom-plugin/test-article.html",
    "title": "测试文章 - 如何使用Chrome插件提取网页内容",
    "tags": [],
    "note": "自动提取的文章摘要：\n在现代Web开发中，内容提取是一个常见需求。本文将介绍如何使用Chrome扩展程序来智能提取网页中的文章内容。 背景介绍 随着信息时代的发展，我们每天都会浏览大量的网页内容。如何有效地收藏和管理这些信息成为了一个重要问题。传统的书签功能只能保存URL，无法保存页面的实际内容。 Chrome扩展程序提供了强大的API，允许我们访问和操作网页内容。通过使用content scripts和scripti...\n\n自动提取的文章关键词：\napi, content, article, 在现代web开发中, 内容提取是一个常见需求, 本文将介绍如何使用chrome扩展程序来智能提取网页中的文章内容, 背景介绍, 随着信息时代的发展, 我们每天都会浏览大量的网页内容, 如何有效地收藏和管理这些信息成为了一个重要问题\n\n自动提取的文章标题：\n如何使用Chrome插件提取网页内容\n\n自动提取的文章内容：\n在现代Web开发中，内容提取是一个常见需求。本文将介绍如何使用Chrome扩展程序来智能提取网页中的文章内容。 背景介绍 随着信息时代的发展，我们每天都会浏览大量的网页内容。如何有效地收藏和管理这些信息成为了一个重要问题。传统的书签功能只能保存URL，无法保存页面的实际内容。 Chrome扩展程序提供了强大的API，允许我们访问和操作网页内容。通过使用content scripts和scripting API，我们可以实现智能的内容提取功能。 技术实现 我们的解决方案主要包含以下几个关键技术点： Content Scripts：在网页上下文中执行JavaScript代码 Scripting API：动态注入脚本到目标页面 DOM解析：智能识别文章内容区域 关键词提取：自动生成内容摘要和标签 核心算法 内容提取算法的核心思路是通过多种CSS选择器来定位文章主体内容。我们预定义了一系列常见的文章容器选择器，包括： 语义化标签：article、main等 通用类名：.content、.article-content等 特定网站：知乎的.RichText、微信的#js_content等 算法会按优先级依次尝试这些选择器，选择内容最丰富的元素作为文章主体。 实际应用 这个功能可以广泛应用于： 个人知识管理系统 内容聚合平台 学术研究工具 新闻摘要服务 总结 通过Chrome扩展程序实现的内容提取功能，不仅提高了信息收集的效率，还为后续的内容分析和处理提供了基础。随着AI技术的发展，我们还可以进一步集成自然语言处理功能，实现更智能的内容理解和分类。",
    "domain": "",
    "content": "在现代Web开发中，内容提取是一个常见需求。本文将介绍如何使用Chrome扩展程序来智能提取网页中的文章内容。 背景介绍 随着信息时代的发展，我们每天都会浏览大量的网页内容。如何有效地收藏和管理这些信息成为了一个重要问题。传统的书签功能只能保存URL，无法保存页面的实际内容。 Chrome扩展程序提供了强大的API，允许我们访问和操作网页内容。通过使用content scripts和scripting API，我们可以实现智能的内容提取功能。 技术实现 我们的解决方案主要包含以下几个关键技术点： Content Scripts：在网页上下文中执行JavaScript代码 Scripting API：动态注入脚本到目标页面 DOM解析：智能识别文章内容区域 关键词提取：自动生成内容摘要和标签 核心算法 内容提取算法的核心思路是通过多种CSS选择器来定位文章主体内容。我们预定义了一系列常见的文章容器选择器，包括： 语义化标签：article、main等 通用类名：.content、.article-content等 特定网站：知乎的.RichText、微信的#js_content等 算法会按优先级依次尝试这些选择器，选择内容最丰富的元素作为文章主体。 实际应用 这个功能可以广泛应用于： 个人知识管理系统 内容聚合平台 学术研究工具 新闻摘要服务 总结 通过Chrome扩展程序实现的内容提取功能，不仅提高了信息收集的效率，还为后续的内容分析和处理提供了基础。随着AI技术的发展，我们还可以进一步集成自然语言处理功能，实现更智能的内容理解和分类。",
    "summary": "在现代Web开发中，内容提取是一个常见需求。本文将介绍如何使用Chrome扩展程序来智能提取网页中的文章内容。 背景介绍 随着信息时代的发展，我们每天都会浏览大量的网页内容。如何有效地收藏和管理这些信息成为了一个重要问题。传统的书签功能只能保存URL，无法保存页面的实际内容。 Chrome扩展程序提供了强大的API，允许我们访问和操作网页内容。通过使用content scripts和scripti...",
    "keywords": [
        "api",
        "content",
        "article",
        "在现代web开发中",
        "内容提取是一个常见需求",
        "本文将介绍如何使用chrome扩展程序来智能提取网页中的文章内容",
        "背景介绍",
        "随着信息时代的发展",
        "我们每天都会浏览大量的网页内容",
        "如何有效地收藏和管理这些信息成为了一个重要问题"
    ],
    "extracted_at": "2025-05-26T07:36:54.091Z",
    "type": "bookmark"
}

def test_validation():
    print("=" * 80)
    print("🧪 测试Pydantic模型验证")
    print("=" * 80)
    
    # 检查各个字段的长度
    print(f"📏 字段长度检查:")
    print(f"   URL: {len(test_data['url'])}")
    print(f"   标题: {len(test_data['title'])}")
    print(f"   备注: {len(test_data['note'])}")
    print(f"   内容: {len(test_data['content'])}")
    print(f"   摘要: {len(test_data['summary'])}")
    print(f"   关键词数量: {len(test_data['keywords'])}")
    print()
    
    try:
        # 尝试创建BookmarkCreate实例
        bookmark = BookmarkCreate(**test_data)
        print("✅ 验证成功！")
        print(f"📝 创建的对象:")
        print(f"   URL: {bookmark.url}")
        print(f"   标题: {bookmark.title}")
        print(f"   类型: {bookmark.type}")
        print(f"   提取时间: {bookmark.extracted_at}")
        
    except Exception as e:
        print("❌ 验证失败！")
        print(f"❌ 错误类型: {type(e).__name__}")
        print(f"❌ 错误信息: {str(e)}")
        
        # 如果是ValidationError，显示详细信息
        if hasattr(e, 'errors'):
            print("❌ 详细错误:")
            for error in e.errors():
                print(f"   字段: {error.get('loc', 'Unknown')}")
                print(f"   错误: {error.get('msg', 'Unknown')}")
                print(f"   类型: {error.get('type', 'Unknown')}")
                print(f"   输入: {error.get('input', 'Unknown')}")
                print("   ---")
    
    print("=" * 80)

if __name__ == "__main__":
    test_validation() 