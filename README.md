# 个人导航网站

这是一个基于Flask和TailwindCSS构建的个人导航网站，提供分类管理的链接导航功能和后台管理系统。

## 功能特点

- 🚀 清爽简洁的导航界面
- 📂 支持区域和分类两级管理
- 🔗 链接卡片式展示
- 🛠 完整的后台管理系统
- 🔐 用户认证和权限控制
- 💻 响应式设计，支持移动端访问
- 📱 支持区域和分类的拖拽排序
- 🔄 支持数据导入导出

## 技术栈

- 后端: Python Flask
- 前端: TailwindCSS
- 数据库: SQLite
- 认证: Flask-Login
- CSS工具: PostCSS
- 排序: Sortable.js

## 目录结构

```
.
├── app.py              # Flask应用主文件
├── import_data.py      # 数据导入脚本
├── requirements.txt    # Python依赖
├── Dockerfile          # Docker 构建文件
├── docker-compose.yml  # Docker 编排配置
├── migrations/         # 数据库迁移文件
├── instance/          # 实例配置和数据
├── www/               # 前端文件目录
│   ├── css/          # 编译后的CSS
│   ├── src/          # 源CSS文件
│   ├── js/           # JavaScript文件
│   └── admin/        # 后台管理界面
└── README.md         # 项目说明
```

## 功能模块

### 前台导航
- 分区展示：支持多个区域（如常用网址、学习、家庭等）
- 分类管理：每个区域下可包含多个分类
- 链接卡片：美观的卡片式布局
- 响应式设计：完美支持移动端访问

### 后台管理
- 区域管理
  - 添加/编辑/删除区域
  - 区域排序
- 分类管理
  - 添加/编辑/删除分类
  - 分类排序
  - 分类归属区域设置
- 链接管理
  - 添加/编辑/删除链接
  - 链接分类设置
- 用户管理
  - 用户认证
  - 登录保护
  - 失败次数限制

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

### 2. 传统部署

1. 安装 Python 依赖
```bash
pip install -r requirements.txt
```

2. 初始化数据库
```bash
flask db upgrade  # 执行数据库迁移
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
2. 访问管理后台: `http://localhost:5000/admin`
   - 默认管理员账号: admin
   - 默认密码: admin

### 后台功能说明

1. 区域管理
   - 点击"添加区域"按钮创建新区域
   - 使用拖拽功能调整区域顺序
   - 点击编辑按钮修改区域名称

2. 分类管理
   - 在对应区域下添加新分类
   - 使用拖拽功能调整分类顺序
   - 编辑分类信息时可更改所属区域

3. 链接管理
   - 在分类下添加新链接
   - 支持批量导入链接
   - 可以移动链接到其他分类

## 数据备份

### 自动备份
系统在进行数据导入时会自动创建备份文件 `data_backup.json`

### 手动备份
```bash
# 备份数据库
cp instance/links.db instance/links.db.backup
```

## 系统要求
- 最小配置：1核 CPU，1GB 内存
- 推荐配置：2核 CPU，2GB 内存

## 开发说明

### CSS 修改
修改 CSS 后需要重新编译：
```bash
cd www && npx tailwindcss -i ./src/style.css -o ./css/style.css
```

### 数据库迁移
添加新的数据库字段后需要创建迁移：
```bash
flask db migrate -m "迁移说明"
flask db upgrade
```

### 数据更新
1. 本地修改后提交代码：
```bash
git add .
git commit -m "你的提交说明"
git push
```

2. 更新服务器数据：
```bash
./update_server_data.sh  # 将本地的 links.db 文件复制到服务器
```

### Docker 更新
1. SSH 登录服务器：
```bash
ssh www@home
```

2. 更新并重启服务：
```bash
cd /www/wwwroot/home.jayliu.co.nz
git pull

# 如果只是更新了代码，不需要重新构建镜像
docker compose down
docker compose up -d

# 如果修改了 Dockerfile 或需要重新构建镜像
docker compose down
docker compose up -d --build  # 重新构建镜像并启动
```

### 后台界面说明
1. 顶部导航栏
   - 左侧显示"导航管理后台"标题
   - 右侧为退出登录按钮

2. 左侧菜单
   - 分类管理：管理区域和分类
   - 链接管理：管理所有链接
   - 用户管理：管理后台用户
   - 查看首页：跳转到前台页面

3. 主要内容区域
   - 顶部显示当前页面标题（分类管理/链接管理/用户管理）
   - 下方为具体的管理内容

### 注意事项
1. 删除区域时会同时删除该区域下的所有分类和链接
2. 删除分类时会同时删除该分类下的所有链接
3. 每次修改数据库后，请及时执行 update_server_data.sh 更新服务器数据
4. 代码更新后，需要重启 Docker 容器使更改生效

## 贡献指南

欢迎提交 Issue 和 Pull Request 来帮助改进项目。

## 许可证

MIT License