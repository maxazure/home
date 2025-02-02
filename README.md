# 导航管理系统

## 项目说明
这是一个简单的导航管理系统，支持多区域、多分类的链接管理。

## 功能特点
1. 区域管理
   - 添加/修改/删除区域
   - 区域排序（上下移动）
   - 区域内分类管理

2. 分类管理
   - 添加/修改/删除分类
   - 分类排序（上下移动）
   - 分类下链接管理

3. 链接管理
   - 添加/修改/删除链接
   - 支持空 URL（用于网络共享文件夹）

4. 用户管理
   - 添加/修改/删除用户
   - 用户登录状态管理

## 目录结构
```
.
├── www/                # 网站根目录
│   ├── admin/         # 后台管理界面
│   ├── css/           # 样式文件
│   ├── js/           # JavaScript 文件
│   └── instance/     # 数据库文件目录
├── app.py            # Flask 应用主文件
├── import_data.py    # 数据导入脚本
└── update_server_data.sh  # 服务器数据更新脚本
```

## 开发说明

### 本地开发
1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 运行开发服务器：
```bash
python app.py
```

3. 访问地址：
- 前台：http://localhost:5000
- 后台：http://localhost:5000/admin
- 默认管理员账号：admin/admin

### 数据更新
1. 本地修改后执行以下命令提交代码：
```bash
git add .
git commit -m "你的提交说明"
git push
```

2. 更新服务器数据：
```bash
./update_server_data.sh
```
此脚本会将本地的 links.db 文件复制到服务器。

### Docker 更新
1. 登录服务器：
```bash
ssh www@home
```

2. 进入项目目录：
```bash
cd /www/wwwroot/home.jayliu.co.nz
```

3. 拉取最新代码：
```bash
git pull
```

4. 重启 Docker 容器：
```bash
docker compose down
docker compose up -d
```

## 后台界面说明
1. 顶部导航栏
   - 左侧显示"导航管理后台"标题
   - 右侧为退出登录按钮

2. 左侧菜单
   - 分类管理：管理区域和分类
   - 链接管理：管理所有链接
   - 用户管理：管理后台用户
   - 查看首页：跳转到前台页面

3. 主要内容区域
   - 顶部显示当前页面标题
   - 下方为具体的管理内容

## 注意事项
1. 删除区域时会同时删除该区域下的所有分类和链接
2. 删除分类时会同时删除该分类下的所有链接
3. 每次修改数据库后，请及时执行 update_server_data.sh 更新服务器数据
4. 代码更新后，需要重启 Docker 容器使更改生效