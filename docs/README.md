# 导航网站项目文档

## 目录

1. [项目概述](#项目概述)
2. [技术栈](#技术栈)
3. [目录结构](#目录结构)
4. [快速开始](#快速开始)
5. [详细文档](#详细文档)

## 项目概述

这是一个基于 Flask 的导航网站项目，提供分类链接管理功能，包含前台展示和后台管理系统。

### 主要功能

- 前台链接展示
- 用户认证系统
- 后台管理界面
- 分类和链接管理
- 安全防护机制

## 技术栈

- 后端：Flask + SQLAlchemy + Flask-Login
- 前端：TailwindCSS + 原生 JavaScript
- 数据库：SQLite
- 测试：Python unittest

## 目录结构

```
home.jayliu.co.nz/
├── app.py              # 主应用文件
├── instance/          # 实例文件夹（数据库等）
├── migrations/        # 数据库迁移文件
├── tests/            # 测试文件
├── www/              # 静态文件和前端代码
│   ├── admin/       # 管理后台页面
│   ├── css/         # 样式文件
│   ├── js/          # JavaScript 文件
│   └── index.html   # 主页
└── docs/            # 文档
    ├── api/         # API 文档
    ├── testing/     # 测试文档
    └── deployment/  # 部署文档
```

## 快速开始

1. 克隆项目：
```bash
git clone https://github.com/maxazure/home.git
cd home
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 初始化数据库：
```bash
flask init-db
flask create-admin  # 创建管理员账户
```

4. 运行项目：
```bash
python app.py
```

## 详细文档

- [API 文档](api/README.md)
- [测试文档](testing/README.md)
- [部署文档](deployment/README.md) 