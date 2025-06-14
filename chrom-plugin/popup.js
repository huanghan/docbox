// 点击收藏按钮弹出界面的主要逻辑
class BookmarkPopup {
    constructor() {
        this.currentTab = null;
        this.init();
    }

    async init() {
        try {
            // 获取当前活动标签页
            await this.getCurrentTab();
            // 显示页面信息
            await this.displayPageInfo();
            // 绑定事件
            this.bindEvents();
            // 加载保存的设置
            await this.loadSettings();
        } catch (error) {
            console.error('初始化失败:', error);
            this.showStatus('初始化失败', 'error');
        }
    }

    async getCurrentTab() {
        try {
            const [tab] = await chrome.tabs.query({
                active: true,
                currentWindow: true
            });
            this.currentTab = tab;
        } catch (error) {
            console.error('获取当前标签页失败:', error);
            throw error;
        }
    }

    async displayPageInfo() {
        if (!this.currentTab) return;

        const titleEl = document.getElementById('title');
        const urlEl = document.getElementById('url');
        const faviconEl = document.getElementById('favicon');

        // 显示标题和URL
        titleEl.textContent = this.currentTab.title || '无标题';
        urlEl.textContent = this.currentTab.url || '';

        // 设置网站图标
        if (this.currentTab.favIconUrl) {
            faviconEl.src = this.currentTab.favIconUrl;
            faviconEl.style.display = 'block';
        } else {
            // 使用默认图标
            faviconEl.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%23667eea"><path d="M12 2L2 7v10c0 5.55 3.84 9.739 9 11 5.16-1.261 9-5.45 9-11V7l-10-5z"/></svg>';
            faviconEl.style.display = 'block';
        }

        // 自动生成建议标签
        await this.generateSuggestedTags();

        // 自动提取文章内容，显示到note
        try {
            const note = document.getElementById('note');
            const articleData = await this.getPageContent();
            if (articleData && articleData.summary) {
                note.value = "标题：" + articleData.title + "\n\n";
                note.value += "自动提取的文章摘要：\n" + articleData.summary + "\n\n" 
                            + "自动提取的文章关键词：\n" + articleData.keywords.join(', ')
                            "\n\n"
                            + "自动提取的文章内容：\n" + articleData.content;

            }
        } catch (error) {
            console.error('自动提取内容失败:', error);
        }
    }

    async getPageContent() {
        try {
            console.log('🔍 开始提取页面内容...');
            // 使用content script提取页面内容，避免跨域问题
            const [result] = await chrome.scripting.executeScript({
                target: { tabId: this.currentTab.id },
                func: extractArticleContent
            });
            
            console.log('✅ 内容提取完成:', result);
            return result.result || {};
        } catch (error) {
            console.error('❌ 获取页面内容失败:', error);
            console.error('错误详情:', error.stack);
            return {};
        }
    }

    async generateSuggestedTags() {
        if (!this.currentTab) return;

        try {
            const url = new URL(this.currentTab.url);
            const domain = url.hostname.replace('www.', '');
            const title = this.currentTab.title || '';
            
            const suggestedTags = [];
            
            // 基于域名生成标签
            if (domain.includes('github')) suggestedTags.push('开发');
            if (domain.includes('stackoverflow')) suggestedTags.push('编程');
            if (domain.includes('medium') || domain.includes('blog')) suggestedTags.push('博客');
            if (domain.includes('youtube') || domain.includes('video')) suggestedTags.push('视频');
            if (domain.includes('news') || domain.includes('bbc') || domain.includes('cnn')) suggestedTags.push('新闻');
            if (domain.includes('shopping') || domain.includes('amazon') || domain.includes('taobao')) suggestedTags.push('购物');
            
            // 基于标题生成标签
            if (title.includes('教程') || title.includes('tutorial')) suggestedTags.push('教程');
            if (title.includes('工具') || title.includes('tool')) suggestedTags.push('工具');
            if (title.includes('文档') || title.includes('doc')) suggestedTags.push('文档');
            
            // 去重并设置到输入框
            const uniqueTags = [...new Set(suggestedTags)];
            if (uniqueTags.length > 0) {
                document.getElementById('tags').placeholder = `建议标签: ${uniqueTags.join(', ')}`;
            }
        } catch (error) {
            console.error('生成建议标签失败:', error);
        }
    }

    bindEvents() {
        const saveBtn = document.getElementById('saveBtn');
        const cancelBtn = document.getElementById('cancelBtn');
        const tagsInput = document.getElementById('tags');

        saveBtn.addEventListener('click', () => this.saveBookmark());
        cancelBtn.addEventListener('click', () => window.close());
        
        // 回车键保存
        tagsInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.saveBookmark();
            }
        });

        // 自动保存输入的标签
        tagsInput.addEventListener('input', () => {
            this.saveSettings();
        });
    }

    async saveBookmark() {
        if (!this.currentTab) {
            this.showStatus('没有找到当前页面信息', 'error');
            return;
        }

        const saveBtn = document.getElementById('saveBtn');
        const tags = document.getElementById('tags').value.trim();
        const note = document.getElementById('note').value.trim();

        // 禁用按钮，显示加载状态
        saveBtn.disabled = true;
        saveBtn.textContent = '正在提取内容...';

        try {
            // 提取页面文章内容
            console.log('🚀 开始保存收藏...');
            this.showStatus('正在提取文章内容...', 'info');
            
            console.log('📄 当前标签页信息:', this.currentTab);
            const articleData = await this.getPageContent();
            console.log('📝 提取的文章数据:', articleData);

            const bookmarkData = {
                url: this.currentTab.url,
                title: articleData.title || this.currentTab.title ,
                tags: tags.split(',').map(tag => tag.trim()).filter(tag => tag),
                note: note,
                favicon: this.currentTab.favIconUrl,
                domain: new URL(this.currentTab.url).hostname,
                // 新增的文章内容字段
                content: articleData.content || '',
                summary: articleData.summary || '',
                keywords: articleData.keywords || [],
                extracted_at: articleData.timestamp || new Date().toISOString(),
                type: 'bookmark'
            };

            console.log('📦 准备发送的收藏数据:', bookmarkData);

            // 发送到收藏服务器
            this.showStatus('正在保存到服务器...', 'info');
            await this.sendToServer(bookmarkData);
            
            // 保存到本地存储（备份）
            await this.saveToLocal(bookmarkData);

            this.showStatus('✅ 收藏成功！已提取文章内容', 'success');
            
            // 2秒后自动关闭
            setTimeout(() => {
                window.close();
            }, 2000);

        } catch (error) {
            console.error('❌ 保存失败:', error);
            console.error('错误堆栈:', error.stack);
            this.showStatus('❌ 保存失败: ' + error.message, 'error');
        } finally {
            console.log('🔄 保存流程结束');
            saveBtn.disabled = false;
            saveBtn.textContent = '保存收藏';
        }
    }

    async sendToServer(bookmarkData) {
        // 从存储中获取服务器配置
        const result = await chrome.storage.sync.get(['serverUrl', 'apiKey', 'userId']);
        const serverUrl = result.serverUrl ; // 默认服务器地址
        const apiKey = result.apiKey || '';
        const userId = result.userId || 1; // 默认用户ID

        // 转换数据格式以匹配新的文档接口
        const documentData = {
            uid: userId,
            url: bookmarkData.url || '',
            title: bookmarkData.title || 'Untitled',
            summary: this.generateSummary(bookmarkData),
            content: this.generateContent(bookmarkData),
            source: bookmarkData.url || '',
            favicon: bookmarkData.favicon || '',
            tags: Array.isArray(bookmarkData.tags) ? bookmarkData.tags.join(', ') : (bookmarkData.tags || ''),
            evaluate: 0
        };

        const response = await fetch(`${serverUrl}/api/documents`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': apiKey ? `Bearer ${apiKey}` : '',
                'User-Agent': 'BookmarkExtension/1.0.0'
            },
            body: JSON.stringify(documentData)
        });

        if (!response.ok) {
            const errorText = await response.text();
            if (response.status === 401) {
                throw new Error('API密钥无效');
            } else if (response.status === 404) {
                throw new Error('服务器接口不存在');
            } else {
                throw new Error(`服务器错误 ${response.status}: ${errorText}`);
            }
        }

        return await response.json();
    }

    // 生成摘要
    generateSummary(bookmarkData) {
        const parts = [];
        
        if (bookmarkData.domain) {
            parts.push(`来自 ${bookmarkData.domain}`);
        }
        
        if (bookmarkData.summary) {
            parts.push(bookmarkData.summary);
        } else if (bookmarkData.note) {
            parts.push(bookmarkData.note);
        }
        
        return parts.join(' - ') || `网页收藏: ${bookmarkData.title || ''}`;
    }

    // 生成内容
    generateContent(bookmarkData) {
        const content = [];
        
        content.push(`# ${bookmarkData.title || 'Untitled'}`);
        content.push('');
        content.push(`**网址**: ${bookmarkData.url || ''}`);
        
        if (bookmarkData.domain) {
            content.push(`**域名**: ${bookmarkData.domain}`);
        }
        
        if (bookmarkData.extracted_at) {
            content.push(`**收藏时间**: ${new Date(bookmarkData.extracted_at).toLocaleString('zh-CN')}`);
        }
        
        if (bookmarkData.tags && bookmarkData.tags.length > 0) {
            const tags = Array.isArray(bookmarkData.tags) ? bookmarkData.tags : [bookmarkData.tags];
            content.push(`**标签**: ${tags.join(', ')}`);
        }
        
        if (bookmarkData.keywords && bookmarkData.keywords.length > 0) {
            content.push(`**关键词**: ${bookmarkData.keywords.join(', ')}`);
        }
        
        if (bookmarkData.note) {
            content.push('');
            content.push('## 备注');
            content.push(bookmarkData.note);
        }
        
        if (bookmarkData.summary && bookmarkData.summary !== bookmarkData.note) {
            content.push('');
            content.push('## 摘要');
            content.push(bookmarkData.summary);
        }
        
        if (bookmarkData.content) {
            content.push('');
            content.push('## 文章内容');
            content.push(bookmarkData.content);
        }
        
        return content.join('\n');
    }

    async saveToLocal(bookmarkData) {
        try {
            // 获取现有的收藏数据
            const result = await chrome.storage.local.get(['bookmarks']);
            const bookmarks = result.bookmarks || [];
            
            // 添加新收藏
            bookmarks.unshift(bookmarkData);
            
            // 保持最新的100条记录
            if (bookmarks.length > 100) {
                bookmarks.splice(100);
            }
            
            // 保存到本地
            await chrome.storage.local.set({ bookmarks });
        } catch (error) {
            console.error('保存到本地失败:', error);
        }
    }

    async loadSettings() {
        try {
            const result = await chrome.storage.sync.get(['defaultTags', 'autoFillTags']);
            
            if (result.defaultTags && result.autoFillTags) {
                document.getElementById('tags').value = result.defaultTags;
            }
        } catch (error) {
            console.error('加载设置失败:', error);
        }
    }

    async saveSettings() {
        try {
            const tags = document.getElementById('tags').value.trim();
            await chrome.storage.sync.set({
                defaultTags: tags,
                autoFillTags: true
            });
        } catch (error) {
            console.error('保存设置失败:', error);
        }
    }

    showStatus(message, type = 'info') {
        const statusEl = document.getElementById('status');
        statusEl.textContent = message;
        statusEl.className = `status ${type}`;
        
        // 3秒后清除状态
        setTimeout(() => {
            statusEl.textContent = '';
            statusEl.className = 'status';
        }, 3000);
    }
}

// 在页面中执行的内容提取函数（独立函数，不属于类）
function extractArticleContent() {
    try {
    // 常见的文章内容选择器
    const articleSelectors = [
        'article',
        '[role="main"]',
        '.article-content',
        '.post-content',
        '.entry-content',
        '.content',
        '.main-content',
        '.article-body',
        '.post-body',
        '.RichText', // 知乎
        '.Post-RichText', // 知乎专栏
        '.content_area', // 微信公众号
        '.rich_media_content', // 微信公众号
        '#js_content', // 微信公众号
        '.article', // 通用
        'main',
        '#main',
        '.markdown-body', // GitHub
        '.post', // 博客
        '.entry' // 博客
    ];

    let content = '';
    let title = '';
    let summary = '';

    // 提取标题
    const currentUrl = window.location.href || '';
    if(currentUrl.startsWith('https://github.com/')){
        title = currentUrl.replace('https://github.com/', '');
    }else{
        const titleSelectors = ['h1', 'title', '.title', '.post-title', '.article-title'];
        for (const selector of titleSelectors) {
            const titleEl = document.querySelector(selector);
            if (titleEl && titleEl.textContent.trim()) {
                title = titleEl.textContent.trim();
                break;
            }
        }
    }

    // 提取正文内容
    for (const selector of articleSelectors) {
        const element = document.querySelector(selector);
        if (element) {
            // 移除脚本、样式等不需要的元素
            const clonedElement = element.cloneNode(true);
            const unwantedElements = clonedElement.querySelectorAll('script, style, nav, header, footer, aside, .ad, .advertisement, .social-share, .comments');
            unwantedElements.forEach(el => el.remove());
            
            content = clonedElement.textContent || clonedElement.innerText || '';
            content = content.replace(/\s+/g, ' ').trim();
            
            if (content.length > 100) { // 确保内容足够长
                break;
            }
        }
    }

    // 如果没有找到文章内容，尝试提取body内容
    if (!content || content.length < 100) {
        const bodyContent = document.body.textContent || document.body.innerText || '';
        content = bodyContent.replace(/\s+/g, ' ').trim();
    }

    // 简单的关键词提取函数（在content script中定义）
    function extractKeywords(text) {
        if (!text || typeof text !== 'string') return [];
        
        try {
            // 移除标点符号，转换为小写，分割成词
            const words = text.toLowerCase()
                .replace(/[^\w\s\u4e00-\u9fff]/g, ' ')
                .split(/\s+/)
                .filter(word => word && word.length > 2); // 过滤太短的词

            // 统计词频
            const wordCount = {};
            words.forEach(word => {
                wordCount[word] = (wordCount[word] || 0) + 1;
            });

            // 排序并返回前10个高频词
            return Object.entries(wordCount)
                .sort((a, b) => b[1] - a[1])
                .slice(0, 10)
                .map(([word]) => word);
        } catch (error) {
            console.error('关键词提取失败:', error);
            return [];
        }
    }

    // 生成摘要（前200字符）
    if (content && content.length > 200) {
        summary = content.substring(0, 200) + '...';
    } else {
        summary = content || '';
    }

    // 提取关键词
    const keywords = extractKeywords(content);

    // 安全获取页面信息
    const getPageTitle = () => {
        try {
            console.info("title:"+title)
            console.info("document.title:"+document.title)
            return title || document.title || '无标题';
        } catch (error) {
            console.error('获取页面标题失败:', error);
            return '无标题';
        }
    };

    const getPageUrl = () => {
        try {
            return window.location.href || '';
        } catch (error) {
            console.error('获取页面URL失败:', error);
            return '';
        }
    };

    const getPageDomain = () => {
        try {
            return window.location.hostname || '';
        } catch (error) {
            console.error('获取页面域名失败:', error);
            return '';
        }
    };

    return {
        title: getPageTitle(),
        content: content || '',
        summary: summary,
        keywords: keywords,
        url: getPageUrl(),
        domain: getPageDomain(),
        timestamp: new Date().toISOString()
    };
    } catch (error) {
        console.error('内容提取失败:', error);
        // 返回安全的默认值
        return {
            title: '无标题',
            content: '',
            summary: '',
            keywords: [],
            url: '',
            domain: '',
            timestamp: new Date().toISOString()
        };
    }
}

// 当页面加载完成时初始化
document.addEventListener('DOMContentLoaded', () => {
    new BookmarkPopup();
});

// 处理来自background script的消息
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'openPopup') {
        // 如果是通过右键菜单打开的，可以在这里做特殊处理
        console.log('通过右键菜单打开收藏界面');
    }
}); 