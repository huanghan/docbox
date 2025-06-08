-- 创建notedocs数据库
CREATE DATABASE IF NOT EXISTS notedocs CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 使用notedocs数据库
USE notedocs;

CREATE TABLE IF NOT EXISTS users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL DEFAULT '',
    password VARCHAR(255) NOT NULL DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建docs表
CREATE TABLE IF NOT EXISTS docs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uid BIGINT NOT NULL DEFAULT 0,
    title VARCHAR(255) NOT NULL DEFAULT  '',
    summary VARCHAR(4096) NOT NULL DEFAULT '',
    content LONGTEXT NOT NULL,
    source VARCHAR(1024) NOT NULL DEFAULT '',
    tags VARCHAR(1024) NOT NULL DEFAULT '',
    evaluate INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_docs_title (title),
    INDEX idx_docs_uid (uid)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 插入测试数据
INSERT INTO docs (uid, title, summary, content, source, tags, evaluate) VALUES 
(1, '欢迎文档', '系统欢迎文档', '欢迎使用NoteDocs文档管理系统！', 'system', 'welcome,system', 5),
(1, '使用指南', 'FastAPI文档系统使用说明', '这是一个基于FastAPI和MySQL的文档管理系统。', 'manual', 'guide,fastapi,mysql', 4); 