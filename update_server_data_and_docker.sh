#!/bin/bash

# 使用说明：
# 1. 首次使用前，需要在服务器上配置 sudo 权限：
#    - 登录服务器后执行：sudo visudo
#    - 添加以下配置：
#    www ALL=(ALL) NOPASSWD: /usr/bin/docker, /usr/bin/docker-compose
# 2. 此脚本会自动：
#    - 上传本地数据库到服务器
#    - 更新服务器代码
#    - 重启 Docker 容器

# 上传数据库文件
scp instance/links.db www@home:/www/wwwroot/home.jayliu.co.nz/instance/

# 远程执行更新命令
ssh -t www@home << 'EOF'
  cd /www/wwwroot/home.jayliu.co.nz
  git pull
  sudo docker compose down
  sudo docker compose up -d
EOF

echo "服务器更新完成！"
