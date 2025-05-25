// 弹出界面的主要逻辑
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

        try {
            const bookmarkData = {
                url: this.currentTab.url,
                title: this.currentTab.title,
                tags: tags.split(',').map(tag => tag.trim()).filter(tag => tag),
                note: note,
                favicon: this.currentTab.favIconUrl,
                timestamp: new Date().toISOString(),
                domain: new URL(this.currentTab.url).hostname
            };

            // 发送到收藏服务器
            await this.sendToServer(bookmarkData);
            
            // 保存到本地存储（备份）
            await this.saveToLocal(bookmarkData);

            this.showStatus('✅ 收藏成功！', 'success');
            
            // 2秒后自动关闭
            setTimeout(() => {
                window.close();
            }, 2000);

        } catch (error) {
            console.error('保存失败:', error);
            this.showStatus('❌ 保存失败: ' + error.message, 'error');
        } finally {
            saveBtn.disabled = false;
        }
    }

    async sendToServer(bookmarkData) {
        // 从存储中获取服务器配置
        const result = await chrome.storage.sync.get(['serverUrl', 'apiKey']);
        const serverUrl = result.serverUrl || 'http://localhost:3000'; // 默认服务器地址
        const apiKey = result.apiKey || '';

        const response = await fetch(`${serverUrl}/api/bookmarks`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': apiKey ? `Bearer ${apiKey}` : '',
                'User-Agent': 'BookmarkExtension/1.0.0'
            },
            body: JSON.stringify(bookmarkData)
        });

        if (!response.ok) {
            if (response.status === 401) {
                throw new Error('API密钥无效');
            } else if (response.status === 404) {
                throw new Error('服务器接口不存在');
            } else {
                throw new Error(`服务器错误: ${response.status}`);
            }
        }

        return await response.json();
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