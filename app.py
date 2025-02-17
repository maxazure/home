from flask import Flask, request, jsonify, send_from_directory, redirect, url_for, session, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate
from datetime import timedelta
import os
import json
import tempfile

# 首先初始化 Flask 应用
app = Flask(__name__, static_folder='www', static_url_path='')

# 初始化数据库配置
instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
if not os.path.exists(instance_path):
    os.makedirs(instance_path)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(instance_path, 'links.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 's2245d-secrd2234esadfa2t-keerea2y'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)

# 然后按顺序导入模型和其他模块
from models import (
    db, User, IPBlock, Category, Link, 
    Page, Region  # 添加新模型
)
db.init_app(app)

# 初始化 marshmallow
from schemas import (
    ma, category_schema, categories_schema, 
    link_schema, links_schema, 
    user_schema, users_schema,
    page_schema, pages_schema,  # 添加新的 schema
    region_schema, regions_schema,
    ipblock_schema, ipblocks_schema
)
ma.init_app(app)

# 设置登录管理器
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

# 初始化数据库迁移
migrate = Migrate(app, db)

# 最后导入路由模块
from routes.auth_routes import auth_bp
from routes.category_routes import category_bp
from routes.link_routes import link_bp
from routes.admin.categories import category_bp as admin_category_bp
from routes.admin.links import link_bp as admin_link_bp
from routes.admin.users import user_bp as admin_user_bp
from routes.admin.sections import section_bp as admin_section_bp
from routes.admin.pages import page_bp as admin_page_bp
from routes.admin.regions import region_bp as admin_region_bp
from routes.admin.backup import backup_bp as admin_backup_bp
from routes.page_routes import page_bp  # 新增页面路由
from routes.region_routes import region_bp  # 新增区域路由

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# 添加根路由处理
@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/<slug>')
def page_view(slug):
    page = Page.query.filter_by(slug=slug).first()
    if page:
        return app.send_static_file('index.html')
    return app.send_static_file('404.html'), 404

# 处理404错误
@app.errorhandler(404)
def not_found(e):
    return jsonify(error=str(e), path=request.path), 404

# 注册蓝图
app.register_blueprint(auth_bp)
app.register_blueprint(category_bp)
app.register_blueprint(link_bp)
app.register_blueprint(admin_category_bp, url_prefix='/api/admin')
app.register_blueprint(admin_link_bp, url_prefix='/api/admin')
app.register_blueprint(admin_user_bp, url_prefix='/api/admin')
app.register_blueprint(admin_section_bp, url_prefix='/api/admin')
app.register_blueprint(admin_page_bp, url_prefix='/api/admin')
app.register_blueprint(admin_region_bp, url_prefix='/api/admin')
app.register_blueprint(admin_backup_bp, url_prefix='/api/admin')
app.register_blueprint(page_bp)  # 注册页面路由
app.register_blueprint(region_bp)  # 注册区域路由

# 修改初始化数据库命令
@app.cli.command('init-db')
def init_db_command():
    """Clear existing data and create new tables."""
    db.create_all()
    # 创建默认首页
    if not Page.query.filter_by(slug='home').first():
        home_page = Page(name="Home")
        db.session.add(home_page)
        db.session.commit()
    print('数据库表已创建，并添加了默认首页。')

# 添加数据库迁移命令
@app.cli.command('db-migrate')
def db_migrate_command():
    """Run database migrations."""
    print('正在执行数据库迁移...')
    os.system('flask db migrate -m "自动迁移"')
    print('迁移文件已创建。')

@app.cli.command('db-upgrade')
def db_upgrade_command():
    """Apply database migrations."""
    print('正在应用数据库迁移...')
    os.system('flask db upgrade')
    print('数据库迁移已完成。')

# 初始化管理员账号的命令
@app.cli.command('create-admin')
def create_admin():
    username = 'admin'
    password = 'admin123'  # 请修改为安全的密码
    
    if User.query.filter_by(username=username).first():
        print('Admin user already exists')
        return
    
    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    print('Admin user created successfully')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # 确保应用启动时创建所有表
    app.run(debug=True, port=5000)
