#!/bin/bash

# 上传数据库文件
scp instance/links.db www@home:/www/wwwroot/home.jayliu.co.nz/instance/

# 远程执行更新命令
ssh www@home << 'EOF'
  cd /www/wwwroot/home.jayliu.co.nz
  git pull
EOF

ssh maxazure@home << 'EOF'
  cd /www/wwwroot/home.jayliu.co.nz
  sudo docker compose down
  sudo docker compose up -d
EOF

echo "服务器更新完成！"
