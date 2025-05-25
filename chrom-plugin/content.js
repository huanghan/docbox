// 内容脚本 - 在网页中运行的脚本

class BookmarkContent {
    constructor() {
        this.init();
    }

    init() {
        // 监听来自background script的消息
        chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
            this.handleMessage(request, sender, sendResponse);
        });

        // 添加快捷键支持
        this.addKeyboardShortcuts();

        // 检查是否已收藏当前页面
        this.checkIfBookmarked();

        console.log('收藏助手内容脚本已加载');
    }

    // 处理消息
    handleMessage(request, sender, sendResponse) {
        switch (request.action) {
            case 'getPageContent':
                this.getPageContent()
                    .then(content => sendResponse({ success: true, content }))
                    .catch(error => sendResponse({ success: false, error: error.message }));
                return true;

            case 'highlightBookmarked':
                this.highlightBookmarkedElements();
                sendResponse({ success: true });
                break;

            case 'getSelection':
                const selection = this.getSelectedText();
                sendResponse({ success: true, selection });
                break;

            default:
                sendResponse({ success: false, error: '未知的操作' });
        }
    }

    // 获取页面内容摘要
    async getPageContent() {
        try {
            const content = {
                title: document.title,
                url: window.location.href,
                description: this.getPageDescription(),
                keywords: this.getPageKeywords(),
                mainContent: this.getMainContent(),
                images: this.getPageImages(),
                links: this.getImportantLinks()
            };

            return content;
        } catch (error) {
            console.error('获取页面内容失败:', error);
            throw error;
        }
    }

    // 获取页面描述
    getPageDescription() {
        // 尝试从meta标签获取描述
        const metaDesc = document.querySelector('meta[name="description"]');
        if (metaDesc) {
            return metaDesc.getAttribute('content');
        }

        // 尝试从第一个段落获取
        const firstP = document.querySelector('p');
        if (firstP && firstP.textContent.length > 50) {
            return firstP.textContent.substring(0, 200) + '...';
        }

        return '';
    }

    // 获取页面关键词
    getPageKeywords() {
        const metaKeywords = document.querySelector('meta[name="keywords"]');
        if (metaKeywords) {
            return metaKeywords.getAttribute('content').split(',').map(k => k.trim());
        }

        // 从h1, h2标签提取关键词
        const headings = document.querySelectorAll('h1, h2');
        const keywords = Array.from(headings)
            .map(h => h.textContent.trim())
            .filter(text => text.length > 0 && text.length < 50);

        return keywords.slice(0, 5);
    }

    // 获取主要内容
    getMainContent() {
        // 尝试获取article标签内容
        const article = document.querySelector('article');
        if (article) {
            return this.cleanText(article.textContent).substring(0, 500);
        }

        // 尝试获取main标签内容
        const main = document.querySelector('main');
        if (main) {
            return this.cleanText(main.textContent).substring(0, 500);
        }

        // 获取最长的文本节点
        const textNodes = this.getTextNodes();
        if (textNodes.length > 0) {
            const longestText = textNodes
                .sort((a, b) => b.textContent.length - a.textContent.length)[0];
            return this.cleanText(longestText.textContent).substring(0, 500);
        }

        return '';
    }

    // 获取页面图片
    getPageImages() {
        const images = Array.from(document.querySelectorAll('img'))
            .filter(img => img.src && img.width > 100 && img.height > 100)
            .slice(0, 3)
            .map(img => ({
                src: img.src,
                alt: img.alt || '',
                width: img.width,
                height: img.height
            }));

        return images;
    }

    // 获取重要链接
    getImportantLinks() {
        const links = Array.from(document.querySelectorAll('a[href]'))
            .filter(link => {
                const href = link.getAttribute('href');
                return href && 
                       !href.startsWith('#') && 
                       !href.startsWith('javascript:') &&
                       link.textContent.trim().length > 0;
            })
            .slice(0, 10)
            .map(link => ({
                url: link.href,
                text: link.textContent.trim(),
                title: link.getAttribute('title') || ''
            }));

        return links;
    }

    // 获取选中的文本
    getSelectedText() {
        const selection = window.getSelection();
        if (selection.rangeCount > 0) {
            return {
                text: selection.toString().trim(),
                html: this.getSelectionHTML(),
                range: this.getSelectionRange()
            };
        }
        return null;
    }

    // 获取选中内容的HTML
    getSelectionHTML() {
        const selection = window.getSelection();
        if (selection.rangeCount > 0) {
            const range = selection.getRangeAt(0);
            const container = document.createElement('div');
            container.appendChild(range.cloneContents());
            return container.innerHTML;
        }
        return '';
    }

    // 获取选中范围信息
    getSelectionRange() {
        const selection = window.getSelection();
        if (selection.rangeCount > 0) {
            const range = selection.getRangeAt(0);
            return {
                startOffset: range.startOffset,
                endOffset: range.endOffset,
                commonAncestor: range.commonAncestorContainer.nodeName
            };
        }
        return null;
    }

    // 添加键盘快捷键
    addKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl+Shift+S 快速收藏
            if (e.ctrlKey && e.shiftKey && e.key === 'S') {
                e.preventDefault();
                this.quickBookmark();
            }

            // Ctrl+Shift+D 打开收藏弹窗
            if (e.ctrlKey && e.shiftKey && e.key === 'D') {
                e.preventDefault();
                chrome.runtime.sendMessage({ action: 'openPopup' });
            }
        });
    }

    // 快速收藏当前页面
    async quickBookmark() {
        try {
            const pageContent = await this.getPageContent();
            chrome.runtime.sendMessage({
                action: 'quickBookmark',
                url: window.location.href,
                title: document.title,
                content: pageContent
            }, (response) => {
                if (response.success) {
                    this.showNotification('收藏成功', 'success');
                } else {
                    this.showNotification('收藏失败: ' + response.error, 'error');
                }
            });
        } catch (error) {
            console.error('快速收藏失败:', error);
            this.showNotification('快速收藏失败', 'error');
        }
    }

    // 检查当前页面是否已收藏
    async checkIfBookmarked() {
        try {
            chrome.runtime.sendMessage({
                action: 'checkBookmark',
                url: window.location.href
            }, (response) => {
                if (response.isBookmarked) {
                    this.addBookmarkedIndicator();
                }
            });
        } catch (error) {
            console.error('检查收藏状态失败:', error);
        }
    }

    // 添加已收藏指示器
    addBookmarkedIndicator() {
        // 在页面右上角添加一个小图标表示已收藏
        const indicator = document.createElement('div');
        indicator.id = 'bookmark-indicator';
        indicator.innerHTML = '⭐';
        indicator.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            z-index: 10000;
            background: #4CAF50;
            color: white;
            padding: 8px;
            border-radius: 50%;
            font-size: 16px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            cursor: pointer;
            opacity: 0.8;
            transition: opacity 0.3s ease;
        `;

        indicator.addEventListener('mouseenter', () => {
            indicator.style.opacity = '1';
        });

        indicator.addEventListener('mouseleave', () => {
            indicator.style.opacity = '0.8';
        });

        indicator.addEventListener('click', () => {
            chrome.runtime.sendMessage({ action: 'viewBookmarks' });
        });

        document.body.appendChild(indicator);
    }

    // 高亮已收藏的元素
    highlightBookmarkedElements() {
        // 可以高亮页面中的已收藏链接等
        const links = document.querySelectorAll('a[href]');
        links.forEach(link => {
            // 检查链接是否已收藏
            chrome.runtime.sendMessage({
                action: 'checkBookmark',
                url: link.href
            }, (response) => {
                if (response.isBookmarked) {
                    link.style.borderLeft = '3px solid #4CAF50';
                    link.style.paddingLeft = '8px';
                    link.title = (link.title || '') + ' (已收藏)';
                }
            });
        });
    }

    // 显示页面内通知
    showNotification(message, type = 'info') {
        // 创建通知元素
        const notification = document.createElement('div');
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10001;
            padding: 12px 20px;
            border-radius: 6px;
            color: white;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 14px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            opacity: 0;
            transform: translateY(-10px);
            transition: all 0.3s ease;
            max-width: 300px;
            word-wrap: break-word;
        `;

        // 设置背景颜色
        if (type === 'success') {
            notification.style.background = '#4CAF50';
        } else if (type === 'error') {
            notification.style.background = '#f44336';
        } else {
            notification.style.background = '#2196F3';
        }

        document.body.appendChild(notification);

        // 显示动画
        setTimeout(() => {
            notification.style.opacity = '1';
            notification.style.transform = 'translateY(0)';
        }, 100);

        // 自动消失
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateY(-10px)';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }

    // 清理文本
    cleanText(text) {
        return text
            .replace(/\s+/g, ' ')
            .replace(/\n+/g, ' ')
            .trim();
    }

    // 获取所有文本节点
    getTextNodes() {
        const walker = document.createTreeWalker(
            document.body,
            NodeFilter.SHOW_TEXT,
            {
                acceptNode: function(node) {
                    if (node.parentNode.tagName === 'SCRIPT' || 
                        node.parentNode.tagName === 'STYLE') {
                        return NodeFilter.FILTER_REJECT;
                    }
                    if (node.textContent.trim().length < 50) {
                        return NodeFilter.FILTER_REJECT;
                    }
                    return NodeFilter.FILTER_ACCEPT;
                }
            }
        );

        const textNodes = [];
        let node;
        while (node = walker.nextNode()) {
            textNodes.push(node);
        }

        return textNodes;
    }
}

// 初始化内容脚本
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new BookmarkContent();
    });
} else {
    new BookmarkContent();
} 