# 部署文档

## 目录

1. [系统要求](#系统要求)
2. [安装步骤](#安装步骤)
3. [配置说明](#配置说明)
4. [部署方式](#部署方式)
5. [维护指南](#维护指南)

## 系统要求

- Python 3.8+
- SQLite 3
- Nginx
- 操作系统：Linux/Unix/macOS

## 安装步骤

### 1. 准备环境

```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 创建实例目录
mkdir -p instance
```

### 2. 初始化数据库

```bash
# 创建数据库表
flask init-db

# 创建管理员账户
flask create-admin
```

### 3. 配置 Nginx

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 配置说明

### 环境变量

- `DATABASE_URL`: 数据库连接 URL（默认使用 SQLite）
- `SECRET_KEY`: Flask 密钥（必须修改为随机值）
- `FLASK_ENV`: 运行环境（production/development）

### 安全配置

1. 修改 `app.py` 中的密钥：
```python
app.config['SECRET_KEY'] = 'your-random-secret-key'
```

2. 设置管理员密码：
```bash
flask create-admin  # 按提示设置密码
```

## 部署方式

### 使用 Docker 部署

1. 构建镜像：
```bash
docker build -t nav-site .
```

2. 运行容器：
```bash
docker run -d \
    -p 5000:5000 \
    -v $(pwd)/instance:/app/instance \
    --name nav-site \
    nav-site
```

### 使用 Gunicorn 部署

1. 安装 Gunicorn：
```bash
pip install gunicorn
```

2. 启动服务：
```bash
gunicorn -w 4 -b 127.0.0.1:5000 app:app
```

### 使用 Supervisor 管理进程

1. Supervisor 配置文件 `/etc/supervisor/conf.d/nav-site.conf`：
```ini
[program:nav-site]
directory=/path/to/nav-site
command=gunicorn -w 4 -b 127.0.0.1:5000 app:app
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/nav-site/err.log
stdout_logfile=/var/log/nav-site/out.log
```

2. 启动服务：
```bash
supervisorctl reread
supervisorctl update
supervisorctl start nav-site
```

## 维护指南

### 数据库备份

1. 备份数据库：
```bash
cp instance/links.db instance/links.db.backup
```

2. 使用 SQLite 导出数据：
```bash
sqlite3 instance/links.db .dump > backup.sql
```

### 日志管理

1. 应用日志位置：
- Nginx 日志：`/var/log/nginx/`
- 应用日志：`/var/log/nav-site/`

2. 日志轮转配置 `/etc/logrotate.d/nav-site`：
```
/var/log/nav-site/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        supervisorctl restart nav-site
    endscript
}
```

### 更新部署

1. 拉取最新代码：
```bash
git pull origin main
```

2. 更新依赖：
```bash
pip install -r requirements.txt
```

3. 执行数据库迁移：
```bash
flask db upgrade
```

4. 重启服务：
```bash
supervisorctl restart nav-site
```

### 监控

1. 检查服务状态：
```bash
supervisorctl status nav-site
```

2. 检查日志：
```bash
tail -f /var/log/nav-site/err.log
```

3. 检查数据库状态：
```bash
sqlite3 instance/links.db "SELECT count(*) FROM users;"
``` 