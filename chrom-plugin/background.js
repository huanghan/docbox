// 后台脚本 - 处理右键菜单和其他后台任务

class BookmarkBackground {
    constructor() {
        this.init();
    }

    init() {
        // 监听扩展安装事件
        chrome.runtime.onInstalled.addListener(() => {
            this.createContextMenu();
            this.setDefaultSettings();
        });

        // 监听右键菜单点击事件
        chrome.contextMenus.onClicked.addListener((info, tab) => {
            this.handleContextMenuClick(info, tab);
        });

        // 监听来自popup的消息
        chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
            this.handleMessage(request, sender, sendResponse);
        });

        // 监听标签页更新事件
        chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
            this.handleTabUpdate(tabId, changeInfo, tab);
        });
    }

    // 创建右键菜单
    createContextMenu() {
        // 清除现有菜单项
        chrome.contextMenus.removeAll(() => {
            // 在页面上右键显示收藏选项
            chrome.contextMenus.create({
                id: 'bookmark-page',
                title: '📚 收藏当前网页',
                contexts: ['page'],
                documentUrlPatterns: ['http://*/*', 'https://*/*']
            });

            // 在链接上右键显示收藏选项
            chrome.contextMenus.create({
                id: 'bookmark-link',
                title: '🔗 收藏这个链接',
                contexts: ['link'],
                documentUrlPatterns: ['http://*/*', 'https://*/*']
            });

            // 在选中文本上右键显示收藏选项
            chrome.contextMenus.create({
                id: 'bookmark-selection',
                title: '📝 收藏选中内容',
                contexts: ['selection'],
                documentUrlPatterns: ['http://*/*', 'https://*/*']
            });

            // 分隔符
            chrome.contextMenus.create({
                id: 'separator',
                type: 'separator',
                contexts: ['page', 'link', 'selection']
            });

            // 查看收藏夹
            chrome.contextMenus.create({
                id: 'view-bookmarks',
                title: '📋 查看我的收藏',
                contexts: ['page']
            });

            console.log('右键菜单创建完成');
        });
    }

    // 处理右键菜单点击
    async handleContextMenuClick(info, tab) {
        try {
            switch (info.menuItemId) {
                case 'bookmark-page':
                    await this.bookmarkCurrentPage(tab);
                    break;
                
                case 'bookmark-link':
                    await this.bookmarkLink(info.linkUrl, tab);
                    break;
                
                case 'bookmark-selection':
                    await this.bookmarkSelection(info.selectionText, tab);
                    break;
                
                case 'view-bookmarks':
                    await this.openBookmarksPage();
                    break;
                
                default:
                    console.log('未知的菜单项:', info.menuItemId);
            }
        } catch (error) {
            console.error('处理右键菜单点击失败:', error);
            this.showNotification('操作失败', error.message, 'error');
        }
    }

    // 收藏当前页面
    async bookmarkCurrentPage(tab) {
        try {
            // 打开弹出窗口让用户编辑信息
            chrome.action.openPopup();
            
            // 发送消息给popup
            setTimeout(() => {
                chrome.runtime.sendMessage({
                    action: 'openPopup',
                    source: 'contextMenu',
                    tab: tab
                });
            }, 100);
        } catch (error) {
            console.error('打开收藏界面失败:', error);
            // 如果无法打开popup，直接保存
            await this.quickBookmark(tab.url, tab.title, tab);
        }
    }

    // 收藏链接
    async bookmarkLink(linkUrl, tab) {
        try {
            // 获取链接的标题（如果可能的话）
            const title = await this.getLinkTitle(linkUrl) || linkUrl;
            await this.quickBookmark(linkUrl, title, tab, ['链接']);
        } catch (error) {
            console.error('收藏链接失败:', error);
            this.showNotification('收藏失败', error.message, 'error');
        }
    }

    // 收藏选中内容
    async bookmarkSelection(selectionText, tab) {
        try {
            const bookmarkData = {
                url: tab.url,
                title: `${tab.title} - 选中内容`,
                content: selectionText,
                tags: ['选中内容', '文本'],
                note: `从 ${tab.title} 选中的内容`,
                favicon: tab.favIconUrl,
                timestamp: new Date().toISOString(),
                domain: new URL(tab.url).hostname,
                type: 'selection'
            };

            await this.saveBookmark(bookmarkData);
            this.showNotification('收藏成功', '选中内容已保存', 'success');
        } catch (error) {
            console.error('收藏选中内容失败:', error);
            this.showNotification('收藏失败', error.message, 'error');
        }
    }

    // 快速收藏（不显示弹窗）
    async quickBookmark(url, title, tab, tags = []) {
        try {
            // 自动生成标签
            const autoTags = this.generateAutoTags(url, title);
            const allTags = [...new Set([...tags, ...autoTags])];

            const bookmarkData = {
                url: url,
                title: title,
                tags: allTags,
                note: '通过右键菜单快速收藏',
                favicon: tab?.favIconUrl,
                timestamp: new Date().toISOString(),
                domain: new URL(url).hostname,
                type: 'quick'
            };

            await this.saveBookmark(bookmarkData);
            this.showNotification('收藏成功', `已收藏: ${title}`, 'success');
        } catch (error) {
            console.error('快速收藏失败:', error);
            this.showNotification('收藏失败', error.message, 'error');
        }
    }

    // 自动生成标签
    generateAutoTags(url, title) {
        const tags = [];
        
        try {
            const domain = new URL(url).hostname.replace('www.', '');
            
            // 基于域名的标签
            const domainTags = {
                'github.com': ['开发', '代码'],
                'stackoverflow.com': ['编程', '问答'],
                'medium.com': ['博客', '文章'],
                'youtube.com': ['视频'],
                'bilibili.com': ['视频', 'B站'],
                'zhihu.com': ['知乎', '问答'],
                'juejin.cn': ['掘金', '技术'],
                'csdn.net': ['CSDN', '技术'],
                'baidu.com': ['百度', '搜索'],
                'google.com': ['谷歌', '搜索']
            };

            // 检查完整域名
            if (domainTags[domain]) {
                tags.push(...domainTags[domain]);
            } else {
                // 检查部分匹配
                for (const [key, value] of Object.entries(domainTags)) {
                    if (domain.includes(key.split('.')[0])) {
                        tags.push(...value);
                        break;
                    }
                }
            }

            // 基于标题的标签
            const titleLower = title.toLowerCase();
            if (titleLower.includes('tutorial') || titleLower.includes('教程')) tags.push('教程');
            if (titleLower.includes('api') || titleLower.includes('文档')) tags.push('文档');
            if (titleLower.includes('tool') || titleLower.includes('工具')) tags.push('工具');
            if (titleLower.includes('news') || titleLower.includes('新闻')) tags.push('新闻');

        } catch (error) {
            console.error('生成自动标签失败:', error);
        }

        return [...new Set(tags)];
    }

    // 保存收藏
    async saveBookmark(bookmarkData) {
        try {
            // 发送到服务器
            await this.sendToServer(bookmarkData);
            // 保存到本地
            await this.saveToLocal(bookmarkData);
        } catch (error) {
            // 如果服务器失败，至少保存到本地
            await this.saveToLocal(bookmarkData);
            throw error;
        }
    }

    // 发送到服务器
    async sendToServer(bookmarkData) {
        const result = await chrome.storage.sync.get(['serverUrl', 'apiKey', 'userId']);
        const serverUrl = result.serverUrl ;
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
            throw new Error(`服务器错误 ${response.status}: ${errorText}`);
        }

        return await response.json();
    }

    // 生成摘要
    generateSummary(bookmarkData) {
        const parts = [];
        
        if (bookmarkData.domain) {
            parts.push(`来自 ${bookmarkData.domain}`);
        }
        
        if (bookmarkData.type) {
            const typeMap = {
                'selection': '选中内容',
                'quick': '快速收藏',
                'manual': '手动收藏'
            };
            parts.push(typeMap[bookmarkData.type] || bookmarkData.type);
        }
        
        if (bookmarkData.note) {
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
        
        if (bookmarkData.timestamp) {
            content.push(`**收藏时间**: ${new Date(bookmarkData.timestamp).toLocaleString('zh-CN')}`);
        }
        
        if (bookmarkData.tags && bookmarkData.tags.length > 0) {
            const tags = Array.isArray(bookmarkData.tags) ? bookmarkData.tags : [bookmarkData.tags];
            content.push(`**标签**: ${tags.join(', ')}`);
        }
        
        if (bookmarkData.note) {
            content.push('');
            content.push('## 备注');
            content.push(bookmarkData.note);
        }
        
        if (bookmarkData.content) {
            content.push('');
            content.push('## 内容');
            content.push(bookmarkData.content);
        }
        
        return content.join('\n');
    }

    // 保存到本地
    async saveToLocal(bookmarkData) {
        const result = await chrome.storage.local.get(['bookmarks']);
        const bookmarks = result.bookmarks || [];
        
        bookmarks.unshift(bookmarkData);
        
        if (bookmarks.length > 100) {
            bookmarks.splice(100);
        }
        
        await chrome.storage.local.set({ bookmarks });
    }

    // 获取链接标题
    async getLinkTitle(url) {
        try {
            const response = await fetch(url, { method: 'HEAD' });
            // 这里简化处理，实际可能需要更复杂的逻辑来获取标题
            return null;
        } catch (error) {
            return null;
        }
    }

    // 打开收藏页面
    async openBookmarksPage() {
        // 可以打开一个新标签页显示收藏列表
        chrome.tabs.create({
            url: chrome.runtime.getURL('bookmarks.html')
        });
    }

    // 显示通知
    showNotification(title, message, type = 'info') {
        const iconUrl = type === 'success' ? 'icons/icon32.png' : 
                       type === 'error' ? 'icons/icon32.png' : 'icons/icon32.png';

        chrome.notifications.create({
            type: 'basic',
            iconUrl: iconUrl,
            title: title,
            message: message
        });
    }

    // 设置默认配置
    async setDefaultSettings() {
        const result = await chrome.storage.sync.get(['serverUrl', 'apiKey', 'userId']);
        
        if (!result.serverUrl) {
            await chrome.storage.sync.set({
                serverUrl: 'http://127.0.0.1:80',
                apiKey: '',
                userId: 1,
                autoTags: true,
                notifications: true
            });
        }
    }

    // 处理消息
    handleMessage(request, sender, sendResponse) {
        switch (request.action) {
            case 'quickBookmark':
                this.quickBookmark(request.url, request.title, request.tab, request.tags)
                    .then(() => sendResponse({ success: true }))
                    .catch(error => sendResponse({ success: false, error: error.message }));
                return true; // 保持消息通道开放
            
            case 'getBookmarks':
                chrome.storage.local.get(['bookmarks'])
                    .then(result => sendResponse({ bookmarks: result.bookmarks || [] }))
                    .catch(error => sendResponse({ error: error.message }));
                return true;
            
            default:
                sendResponse({ error: '未知的操作' });
        }
    }

    // 处理标签页更新
    handleTabUpdate(tabId, changeInfo, tab) {
        // 可以在这里处理标签页变化，比如检测是否是收藏过的页面
        if (changeInfo.status === 'complete' && tab.url) {
            // 这里可以添加检查是否已收藏的逻辑
        }
    }
}

// 初始化后台脚本
new BookmarkBackground(); 