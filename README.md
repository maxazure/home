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

## 安装说明

1. 克隆项目
```bash
git clone https://github.com/maxazure/home.git
cd home
```

2. 安装Python依赖
```bash
pip install -r requirements.txt
```

3. 安装前端依赖
```bash
cd www
npm install
```

4. 编译CSS
```bash
cd www
npx tailwindcss -i ./src/style.css -o ./css/style.css
```

5. 初始化数据库
```bash
flask init-db
flask create-admin  # 创建管理员账号
python import_data.py  # 导入初始数据
```

6. 运行项目
```bash
flask run
```

## 使用说明

1. 访问首页: `http://localhost:5000`
2. 访问管理后台: `http://localhost:5000/admin/login`
   - 默认管理员账号: admin
   - 默认密码: admin123

## 目录结构

```
.
├── app.py              # Flask应用主文件
├── import_data.py      # 数据导入脚本
├── requirements.txt    # Python依赖
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

## 开发说明

- CSS修改后需要重新编译：
```bash
cd www && npx tailwindcss -i ./src/style.css -o ./css/style.css
```

## 贡献指南

欢迎提交Issue和Pull Request来帮助改进项目。

## 许可证

MIT License
