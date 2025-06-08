-- 创建notedocs数据库
CREATE DATABASE IF NOT EXISTS notedocs CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 使用notedocs数据库
USE notedocs;

-- 创建docs表
CREATE TABLE IF NOT EXISTS docs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL UNIQUE,
    content LONGTEXT NOT NULL,
    time VARCHAR(50) NOT NULL,
    uid VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_docs_title (title),
    INDEX idx_docs_uid (uid),
    INDEX idx_docs_time (time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 插入测试数据
INSERT INTO docs (title, content, time, uid) VALUES 
('欢迎文档', '欢迎使用NoteDocs文档管理系统！', '2024-01-01 12:00:00', 'system'),
('使用指南', '这是一个基于FastAPI和MySQL的文档管理系统。', '2024-01-01 12:01:00', 'system'); 