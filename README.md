# 个人导航网站

这是一个基于Flask和TailwindCSS构建的个人导航网站，提供分类管理的链接导航功能和后台管理系统。

## 功能特点

- 🚀 清爽简洁的导航界面
- 📂 支持多级分类管理
- 🔗 链接卡片式展示
- 🛠 完整的后台管理系统
- 🔐 用户认证和权限控制
- 💻 响应式设计，支持移动端访问

## 技术栈

- 后端: Python Flask
- 前端: TailwindCSS
- 数据库: SQLite
- 认证: Flask-Login
- CSS工具: PostCSS

## 目录结构

```
.
├── app.py              # Flask应用主文件
├── import_data.py      # 数据导入脚本
├── requirements.txt    # Python依赖
├── Dockerfile          # Docker 构建文件
├── docker-compose.yml  # Docker 编排配置
├── www/               # 前端文件目录
│   ├── css/          # 编译后的CSS
│   ├── src/          # 源CSS文件
│   └── admin/        # 后台管理界面
└── README.md         # 项目说明
```

## 功能模块

- 前台导航
  - 分类展示
  - 链接卡片
  - 响应式布局
- 后台管理
  - 分类管理
  - 链接管理
  - 用户管理
  - 权限控制

## 部署方式

### 1. Docker 部署（推荐）

#### 前提条件
- 安装 Docker
```bash
curl -fsSL https://get.docker.com | sh
```

- 安装 Docker Compose
```bash
sudo apt install docker-compose
```

#### 部署步骤

1. 克隆项目
```bash
git clone https://github.com/maxazure/home.git
cd home
```

2. 启动应用
```bash
docker-compose up -d
```

3. 配置 Nginx 反向代理
```nginx
server {
    listen 80;
    server_name your_domain.com;  # 替换为您的域名

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static {
        alias /path/to/your/project/www;  # 替换为项目 www 目录的实际路径
        expires 30d;
    }
}
```

#### 维护命令

```bash
# 查看容器状态
docker-compose ps

# 查看应用日志
docker-compose logs -f web

# 重启应用
docker-compose restart

# 更新应用
git pull
docker-compose up -d --build
```

### 2. 传统部署

1. 安装 Python 依赖
```bash
pip install -r requirements.txt
```

2. 初始化数据库
```bash
flask init-db
flask create-admin  # 创建管理员账号
python import_data.py  # 导入初始数据
```

3. 编译 CSS
```bash
cd www && npx tailwindcss -i ./src/style.css -o ./css/style.css
```

4. 运行应用
```bash
flask run
```

## 使用说明

1. 访问首页: `http://localhost:5000`
2. 访问管理后台: `http://localhost:5000/admin/login`
   - 默认管理员账号: admin
   - 默认密码: admin123

## 数据备份
数据库文件位于项目根目录的 `links.db`，建议定期备份：
```bash
# 备份数据库
cp links.db links.db.backup
```

## 系统要求
- 最小配置：1核 CPU，1GB 内存
- 推荐配置：2核 CPU，2GB 内存

## 开发说明

- CSS修改后需要重新编译：
```bash
cd www && npx tailwindcss -i ./src/style.css -o ./css/style.css
```

## 贡献指南

欢迎提交Issue和Pull Request来帮助改进项目。

## 许可证

MIT License