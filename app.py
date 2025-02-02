from flask import Flask, request, jsonify, send_from_directory, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
import os

app = Flask(__name__, static_folder='www', static_url_path='')

# 配置数据库
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:////' + os.path.join(basedir, 'instance/links.db'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key'  # 请更改为随机的密钥

# 初始化扩展
db = SQLAlchemy(app)
ma = Marshmallow(app)
login_manager = LoginManager(app)
login_manager.login_view = 'admin_login'
migrate = Migrate(app, db)

# 用户模型
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 模型定义
class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    section_name = db.Column(db.String(100), nullable=False)
    links = db.relationship('Link', backref='category', lazy=True)

class Link(db.Model):
    __tablename__ = 'links'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)

# Schema 定义
class LinkSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Link
    
    id = ma.auto_field()
    name = ma.auto_field()
    url = ma.auto_field()
    category_id = ma.auto_field()

class CategorySchema(ma.SQLAlchemySchema):
    class Meta:
        model = Category
    
    id = ma.auto_field()
    title = ma.auto_field()
    section_name = ma.auto_field()
    links = ma.Nested(LinkSchema, many=True)

class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User
    
    id = ma.auto_field()
    username = ma.auto_field()
    created_at = ma.auto_field()

# 初始化 schema
category_schema = CategorySchema()
categories_schema = CategorySchema(many=True)
link_schema = LinkSchema()
links_schema = LinkSchema(many=True)
user_schema = UserSchema()
users_schema = UserSchema(many=True)

# 添加根路由处理
@app.route('/')
def index():
    return app.send_static_file('index.html')

# 处理404错误
@app.errorhandler(404)
def not_found(e):
    if request.path.startswith('/api/'):
        return jsonify(error=str(e), path=request.path), 404
    return app.send_static_file('index.html')

# 路由定义
# 分类相关接口
@app.route('/api/categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    return jsonify(categories_schema.dump(categories))

@app.route('/api/categories/<id>', methods=['GET'])
def get_category(id):
    category = Category.query.get_or_404(id)
    return jsonify(category_schema.dump(category))

@app.route('/api/categories', methods=['POST'])
def add_category():
    title = request.json['title']
    section_name = request.json['section_name']
    
    new_category = Category(title=title, section_name=section_name)
    db.session.add(new_category)
    db.session.commit()
    
    return jsonify(category_schema.dump(new_category))

@app.route('/api/categories/<id>', methods=['PUT'])
def update_category(id):
    category = Category.query.get_or_404(id)
    
    category.title = request.json.get('title', category.title)
    category.section_name = request.json.get('section_name', category.section_name)
    
    db.session.commit()
    return jsonify(category_schema.dump(category))

@app.route('/api/categories/<id>', methods=['DELETE'])
def delete_category(id):
    category = Category.query.get_or_404(id)
    db.session.delete(category)
    db.session.commit()
    return jsonify({'message': 'Category deleted successfully'})

# 链接相关接口
@app.route('/api/links', methods=['GET'])
def get_links():
    links = Link.query.all()
    return jsonify(links_schema.dump(links))

@app.route('/api/links/<id>', methods=['GET'])
def get_link(id):
    link = Link.query.get_or_404(id)
    return jsonify(link_schema.dump(link))

@app.route('/api/links', methods=['POST'])
def add_link():
    name = request.json['name']
    url = request.json['url']
    category_id = request.json['category_id']
    
    new_link = Link(name=name, url=url, category_id=category_id)
    db.session.add(new_link)
    db.session.commit()
    
    return jsonify(link_schema.dump(new_link))

@app.route('/api/links/<id>', methods=['PUT'])
def update_link(id):
    link = Link.query.get_or_404(id)
    
    link.name = request.json.get('name', link.name)
    link.url = request.json.get('url', link.url)
    link.category_id = request.json.get('category_id', link.category_id)
    
    db.session.commit()
    return jsonify(link_schema.dump(link))

@app.route('/api/links/<id>', methods=['DELETE'])
def delete_link(id):
    link = Link.query.get_or_404(id)
    db.session.delete(link)
    db.session.commit()
    return jsonify({'message': 'Link deleted successfully'})

# 按分类获取链接
@app.route('/api/categories/<id>/links', methods=['GET'])
def get_category_links(id):
    category = Category.query.get_or_404(id)
    return jsonify(links_schema.dump(category.links))

# 管理员认证相关路由
@app.route('/admin/login', methods=['GET'])
def admin_login_page():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    return app.send_static_file('admin/login.html')

@app.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.json
    user = User.query.filter_by(username=data.get('username')).first()
    if user and user.check_password(data.get('password')):
        login_user(user)
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': '用户名或密码错误'}), 401

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('admin_login_page'))

@app.route('/admin')
@login_required
def admin_dashboard():
    return app.send_static_file('admin/index.html')

# API 路由添加认证
@app.route('/api/admin/categories', methods=['POST'])
@login_required
def admin_add_category():
    title = request.json['title']
    section_name = request.json['section_name']
    
    new_category = Category(title=title, section_name=section_name)
    db.session.add(new_category)
    db.session.commit()
    
    return jsonify(category_schema.dump(new_category))

@app.route('/api/admin/categories/<id>', methods=['PUT'])
@login_required
def admin_update_category(id):
    category = Category.query.get_or_404(id)
    
    category.title = request.json.get('title', category.title)
    category.section_name = request.json.get('section_name', category.section_name)
    
    db.session.commit()
    return jsonify(category_schema.dump(category))

@app.route('/api/admin/categories/<id>', methods=['DELETE'])
@login_required
def admin_delete_category(id):
    try:
        category = Category.query.get_or_404(id)
        # 先删除该分类下的所有链接
        Link.query.filter_by(category_id=id).delete()
        # 再删除分类
        db.session.delete(category)
        db.session.commit()
        return jsonify({'message': 'Category deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'删除失败: {str(e)}'}), 500

@app.route('/api/admin/links', methods=['POST'])
@login_required
def admin_add_link():
    name = request.json['name']
    url = request.json['url']
    category_id = request.json['category_id']
    
    new_link = Link(name=name, url=url, category_id=category_id)
    db.session.add(new_link)
    db.session.commit()
    
    return jsonify(link_schema.dump(new_link))

@app.route('/api/admin/links/<id>', methods=['PUT'])
@login_required
def admin_update_link(id):
    link = Link.query.get_or_404(id)
    
    link.name = request.json.get('name', link.name)
    link.url = request.json.get('url', link.url)
    link.category_id = request.json.get('category_id', link.category_id)
    
    db.session.commit()
    return jsonify(link_schema.dump(link))

@app.route('/api/admin/links/<id>', methods=['DELETE'])
@login_required
def admin_delete_link(id):
    link = Link.query.get_or_404(id)
    db.session.delete(link)
    db.session.commit()
    return jsonify({'message': 'Link deleted successfully'})

# 用户管理相关API
@app.route('/api/admin/users', methods=['GET'])
@login_required
def admin_get_users():
    users = User.query.all()
    return jsonify(users_schema.dump(users))

@app.route('/api/admin/users', methods=['POST'])
@login_required
def admin_add_user():
    username = request.json['username']
    password = request.json['password']
    
    if User.query.filter_by(username=username).first():
        return jsonify({'message': '用户名已存在'}), 400
    
    new_user = User(username=username)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify(user_schema.dump(new_user))

@app.route('/api/admin/users/<id>', methods=['PUT'])
@login_required
def admin_update_user(id):
    user = User.query.get_or_404(id)
    
    username = request.json.get('username')
    password = request.json.get('password')
    
    if username and username != user.username:
        if User.query.filter_by(username=username).first():
            return jsonify({'message': '用户名已存在'}), 400
        user.username = username
    
    if password:
        user.set_password(password)
    
    db.session.commit()
    return jsonify(user_schema.dump(user))

@app.route('/api/admin/users/<id>', methods=['DELETE'])
@login_required
def admin_delete_user(id):
    user = User.query.get_or_404(id)
    
    # 防止删除最后一个管理员账户
    if User.query.count() == 1:
        return jsonify({'message': '不能删除最后一个管理员账户'}), 400
    
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'})

# 修改初始化数据库命令
@app.cli.command('init-db')
def init_db_command():
    """Clear existing data and create new tables."""
    db.create_all()
    print('数据库表已创建。')

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