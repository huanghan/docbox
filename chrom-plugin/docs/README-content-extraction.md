# Chrome插件内容提取功能说明

## 🚀 功能概述

Chrome插件现在支持智能提取当前网页的文章内容，包括：
- 📝 文章标题和正文
- 📄 内容摘要（前200字符）
- 🏷️ 自动关键词提取
- 🌐 页面元数据（URL、域名、时间戳）

## 🔧 技术实现

### 核心机制
使用 `chrome.scripting.executeScript` API 在目标页面中执行内容提取脚本，避免跨域限制。

### 支持的网站类型
- ✅ 知乎文章和专栏
- ✅ 微信公众号文章  
- ✅ GitHub README
- ✅ 博客文章
- ✅ 新闻网站
- ✅ 通用文章页面

### 智能选择器
```javascript
const articleSelectors = [
    'article',              // HTML5语义化标签
    '[role="main"]',        // ARIA角色
    '.article-content',     // 通用类名
    '.post-content',
    '.entry-content',
    '.content',
    '.main-content',
    '.article-body',
    '.post-body',
    '.RichText',           // 知乎
    '.Post-RichText',      // 知乎专栏
    '.content_area',       // 微信公众号
    '.rich_media_content', // 微信公众号
    '#js_content',         // 微信公众号
    '.markdown-body',      // GitHub
    'main',
    '#main'
];
```

## 📊 数据结构

提取的数据包含以下字段：

```javascript
{
    title: "文章标题",
    content: "完整文章内容",
    summary: "文章摘要（前200字符）...",
    keywords: ["关键词1", "关键词2", ...],
    url: "https://example.com/article",
    domain: "example.com",
    timestamp: "2024-01-15T10:30:00.000Z",
    extractedAt: "2024-01-15T10:30:00.000Z"
}
```

## 🎯 使用方法

1. **打开目标网页**：导航到包含文章内容的页面
2. **点击插件图标**：在浏览器工具栏点击收藏插件
3. **自动提取内容**：插件会自动分析页面结构并提取文章内容
4. **添加标签和备注**：可选择性添加自定义标签和备注
5. **保存收藏**：点击"保存收藏"按钮

## 🔍 内容过滤

自动过滤以下不需要的元素：
- `<script>` 脚本标签
- `<style>` 样式标签  
- `<nav>` 导航菜单
- `<header>` 页面头部
- `<footer>` 页面底部
- `<aside>` 侧边栏
- `.ad` 广告内容
- `.advertisement` 广告内容
- `.social-share` 社交分享
- `.comments` 评论区域

## 🧠 关键词提取算法

1. **文本预处理**：移除标点符号，转换为小写
2. **分词**：按空格分割，过滤长度小于3的词
3. **词频统计**：计算每个词的出现频率
4. **排序筛选**：返回频率最高的前10个词

## 🛠️ 权限要求

在 `manifest.json` 中需要以下权限：

```json
{
    "permissions": [
        "activeTab",
        "scripting",
        "storage"
    ],
    "host_permissions": [
        "<all_urls>"
    ]
}
```

## 🧪 测试方法

1. 打开 `test-article.html` 测试页面
2. 使用插件提取内容
3. 验证提取结果是否正确

## ⚠️ 注意事项

- 某些网站可能有反爬虫机制，影响内容提取
- 动态加载的内容可能需要等待页面完全加载
- 复杂的页面结构可能影响提取准确性
- 建议在内容完全加载后再使用插件

## 🔄 错误处理

- 如果无法提取内容，会回退到页面标题
- 网络错误时会显示相应错误信息
- 权限不足时会提示用户检查设置

## 📈 未来改进

- [ ] 支持更多网站的特定选择器
- [ ] 集成AI进行更智能的内容识别
- [ ] 支持图片内容提取
- [ ] 添加内容质量评分
- [ ] 支持多语言内容处理 