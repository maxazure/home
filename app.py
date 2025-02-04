from flask import Flask, request, jsonify, send_from_directory, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from datetime import timedelta
import os

app = Flask(__name__, static_folder='www', static_url_path='')

# 确保instance文件夹存在
instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
if not os.path.exists(instance_path):
    os.makedirs(instance_path)

# 配置数据库
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(instance_path, 'links.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 's2245d-secrd2234esadfa2t-keerea2y'  # 请更改为随机的密钥

# 配置 session
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)  # session 过期时间设为 30 天

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
    is_locked = db.Column(db.Boolean, default=False)
    failed_login_attempts = db.Column(db.Integer, default=0)
    last_failed_login = db.Column(db.DateTime)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def increment_failed_attempts(self):
        self.failed_login_attempts += 1
        self.last_failed_login = db.func.current_timestamp()
        if self.failed_login_attempts >= 10:
            self.is_locked = True
        db.session.commit()

    def reset_failed_attempts(self):
        self.failed_login_attempts = 0
        self.last_failed_login = None
        db.session.commit()

class IPBlock(db.Model):
    __tablename__ = 'ip_blocks'
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(45), unique=True, nullable=False)  # IPv6 最长 45 字符
    failed_attempts = db.Column(db.Integer, default=0)
    is_blocked = db.Column(db.Boolean, default=False)
    last_attempt = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# 模型定义
class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    section_name = db.Column(db.String(100), nullable=False)
    section_order = db.Column(db.Integer, default=0)  # 区域排序
    category_order = db.Column(db.Integer, default=0)  # 分类排序
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
    category = ma.Nested(lambda: CategorySchema(only=('id', 'title')))

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
    return jsonify(error=str(e), path=request.path), 404

# 路由定义
# 分类相关接口
@app.route('/api/categories', methods=['GET'])
def get_categories():
    # 先按区域排序，再按分类排序
    categories = Category.query.order_by(Category.section_order, Category.category_order).all()
    return jsonify(categories_schema.dump(categories))

@app.route('/api/categories/<id>', methods=['GET'])
def get_category(id):
    category = db.session.get(Category, id)
    if not category:
        return jsonify({'message': '分类不存在'}), 404
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
    category = db.session.get(Category, id)
    if not category:
        return jsonify({'message': '分类不存在'}), 404
    
    category.title = request.json.get('title', category.title)
    category.section_name = request.json.get('section_name', category.section_name)
    
    db.session.commit()
    return jsonify(category_schema.dump(category))

@app.route('/api/categories/<id>', methods=['DELETE'])
def delete_category(id):
    category = db.session.get(Category, id)
    if not category:
        return jsonify({'message': '分类不存在'}), 404
    db.session.delete(category)
    db.session.commit()
    return jsonify({'message': 'Category deleted successfully'})

# 链接相关接口
@app.route('/api/links', methods=['GET'])
def get_links():
    links = Link.query.join(Category).all()
    return jsonify(link_schema.dump(links, many=True))

@app.route('/api/links/<id>', methods=['GET'])
def get_link(id):
    link = db.session.get(Link, id)
    if not link:
        return jsonify({'message': '链接不存在'}), 404
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
    link = db.session.get(Link, id)
    if not link:
        return jsonify({'message': '链接不存在'}), 404
    
    link.name = request.json.get('name', link.name)
    link.url = request.json.get('url', link.url)
    link.category_id = request.json.get('category_id', link.category_id)
    
    db.session.commit()
    return jsonify(link_schema.dump(link))

@app.route('/api/links/<id>', methods=['DELETE'])
def delete_link(id):
    link = db.session.get(Link, id)
    if not link:
        return jsonify({'message': '链接不存在'}), 404
    db.session.delete(link)
    db.session.commit()
    return jsonify({'message': 'Link deleted successfully'})

# 按分类获取链接
@app.route('/api/categories/<id>/links', methods=['GET'])
def get_category_links(id):
    category = Category.query.get_or_404(id)
    return jsonify(links_schema.dump(category.links))

# 管理员认证相关路由
@app.route('/api/admin/login', methods=['GET'])
def login():
    if current_user.is_authenticated:
        return redirect('/admin')
    return send_from_directory('www', 'admin/login.html')

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    if not request.is_json:
        return jsonify({'message': '请求格式错误'}), 400
        
    username = request.json.get('username')
    password = request.json.get('password')
    remember = request.json.get('remember', True)  # 默认开启记住我
    
    if not username or not password:
        return jsonify({'message': '用户名和密码不能为空'}), 400
        
    user = User.query.filter_by(username=username).first()
    if user and not user.is_locked and user.check_password(password):
        login_user(user, remember=remember)  # 使用记住我功能
        session.permanent = True  # 设置 session 为永久性
        return jsonify({'success': True})
    
    return jsonify({'message': '用户名或密码错误'}), 401

@app.route('/api/admin/logout')
@login_required
def logout():
    logout_user()
    return redirect('/admin/login.html')

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
    
    # 获取当前区域内最大的排序值
    max_order = db.session.query(db.func.max(Category.category_order)).filter(
        Category.section_name == section_name
    ).scalar() or 0
    
    new_category = Category(
        title=title,
        section_name=section_name,
        category_order=max_order + 1
    )
    db.session.add(new_category)
    db.session.commit()
    
    return jsonify(category_schema.dump(new_category))

@app.route('/api/admin/categories/<id>', methods=['PUT'])
@login_required
def admin_update_category(id):
    category = db.session.get(Category, id)
    if not category:
        return jsonify({'message': '分类不存在'}), 404
    
    category.title = request.json.get('title', category.title)
    category.section_name = request.json.get('section_name', category.section_name)
    
    db.session.commit()
    return jsonify(category_schema.dump(category))

@app.route('/api/admin/categories/<id>', methods=['DELETE'])
@login_required
def admin_delete_category(id):
    try:
        category = db.session.get(Category, id)
        if not category:
            return jsonify({'message': '分类不存在'}), 404
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
    link = db.session.get(Link, id)
    if not link:
        return jsonify({'message': '链接不存在'}), 404
    
    link.name = request.json.get('name', link.name)
    link.url = request.json.get('url', link.url)
    link.category_id = request.json.get('category_id', link.category_id)
    
    db.session.commit()
    return jsonify(link_schema.dump(link))

@app.route('/api/admin/links/<id>', methods=['DELETE'])
@login_required
def admin_delete_link(id):
    link = db.session.get(Link, id)
    if not link:
        return jsonify({'message': '链接不存在'}), 404
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
    user = db.session.get(User, id)
    if not user:
        return jsonify({'message': '用户不存在'}), 404
    
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
    user = db.session.get(User, id)
    if not user:
        return jsonify({'message': '用户不存在'}), 404
    
    # 防止删除最后一个管理员账户
    if User.query.count() == 1:
        return jsonify({'message': '不能删除最后一个管理员账户'}), 400
    
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'})

@app.route('/api/admin/users/<id>/unlock', methods=['POST'])
@login_required
def admin_unlock_user(id):
    user = db.session.get(User, id)
    if not user:
        return jsonify({'message': '用户不存在'}), 404
    user.is_locked = False
    user.failed_login_attempts = 0
    user.last_failed_login = None
    db.session.commit()
    return jsonify({'message': '用户已解锁'})

@app.route('/api/admin/ip-blocks', methods=['GET'])
@login_required
def admin_get_ip_blocks():
    ip_blocks = IPBlock.query.all()
    return jsonify([{
        'id': block.id,
        'ip_address': block.ip_address,
        'failed_attempts': block.failed_attempts,
        'is_blocked': block.is_blocked,
        'last_attempt': block.last_attempt,
        'created_at': block.created_at
    } for block in ip_blocks])

@app.route('/api/admin/ip-blocks/<id>/unblock', methods=['POST'])
@login_required
def admin_unblock_ip(id):
    ip_block = db.session.get(IPBlock, id)
    if not ip_block:
        return jsonify({'message': 'IP记录不存在'}), 404
    ip_block.is_blocked = False
    ip_block.failed_attempts = 0
    ip_block.last_attempt = None
    db.session.commit()
    return jsonify({'message': 'IP已解封'})

# 区域管理相关API
@app.route('/api/admin/sections', methods=['POST'])
@login_required
def admin_add_section():
    data = request.get_json()
    section_name = data.get('section_name')
    
    if not section_name:
        return jsonify({'message': '区域名称不能为空'}), 400
        
    # 检查区域名称是否已存在
    if Category.query.filter_by(section_name=section_name).first():
        return jsonify({'message': '区域名称已存在'}), 400
        
    # 获取最大的 section_order
    max_order = db.session.query(db.func.max(Category.section_order)).scalar() or 0
    
    # 创建新分类作为区域的占位
    new_category = Category(
        title=f"{section_name} 默认分类",
        section_name=section_name,
        section_order=max_order + 1
    )
    
    try:
        db.session.add(new_category)
        db.session.commit()
        return jsonify({'message': '区域添加成功', 'section_name': section_name}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'添加区域失败: {str(e)}'}), 500

@app.route('/api/admin/sections/update', methods=['POST'])
@login_required
def admin_update_section():
    data = request.get_json()
    old_section_name = data.get('old_section_name')
    new_section_name = data.get('section_name')
    
    if not new_section_name:
        return jsonify({'message': '区域名称不能为空'}), 400
        
    if not old_section_name:
        return jsonify({'message': '原区域名称不能为空'}), 400
        
    # 检查新区域名称是否已存在（排除当前区域）
    if Category.query.filter(
        Category.section_name == new_section_name,
        Category.section_name != old_section_name
    ).first():
        return jsonify({'message': '区域名称已存在'}), 400
        
    try:
        # 更新所有相关分类的区域名称
        categories = Category.query.filter_by(section_name=old_section_name).all()
        for category in categories:
            category.section_name = new_section_name
        
        db.session.commit()
        return jsonify({'message': '区域更新成功', 'section_name': new_section_name}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'更新区域失败: {str(e)}'}), 500

@app.route('/api/admin/sections/reorder', methods=['POST'])
@login_required
def admin_reorder_sections():
    data = request.get_json()
    section_name = data.get('section_name')
    direction = data.get('direction')
    
    if not section_name or not direction:
        return jsonify({'message': '参数不完整'}), 400
        
    try:
        # 获取当前区域的所有分类
        current_categories = Category.query.filter_by(section_name=section_name).all()
        if not current_categories:
            return jsonify({'message': '区域不存在'}), 404
            
        current_order = current_categories[0].section_order
        
        if direction == 'up':
            # 获取上一个区域
            prev_category = Category.query.filter(
                Category.section_order < current_order
            ).order_by(Category.section_order.desc()).first()
            
            if prev_category:
                # 交换顺序
                prev_order = prev_category.section_order
                prev_section_name = prev_category.section_name
                
                # 更新所有相关分类的顺序
                Category.query.filter_by(section_name=prev_section_name).update(
                    {"section_order": current_order}
                )
                Category.query.filter_by(section_name=section_name).update(
                    {"section_order": prev_order}
                )
                
        elif direction == 'down':
            # 获取下一个区域
            next_category = Category.query.filter(
                Category.section_order > current_order
            ).order_by(Category.section_order).first()
            
            if next_category:
                # 交换顺序
                next_order = next_category.section_order
                next_section_name = next_category.section_name
                
                # 更新所有相关分类的顺序
                Category.query.filter_by(section_name=next_section_name).update(
                    {"section_order": current_order}
                )
                Category.query.filter_by(section_name=section_name).update(
                    {"section_order": next_order}
                )
        
        db.session.commit()
        return jsonify({'message': '区域排序更新成功'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'更新区域排序失败: {str(e)}'}), 500

@app.route('/api/admin/categories/reorder', methods=['POST'])
@login_required
def admin_reorder_category():
    source_id = request.json.get('source_id')
    target_id = request.json.get('target_id')
    
    if not source_id or not target_id:
        return jsonify({'message': '参数不完整'}), 400
    
    source = Category.query.get(source_id)
    target = Category.query.get(target_id)
    
    if not source or not target:
        return jsonify({'message': '分类不存在'}), 404
    
    # 确保在同一区域内排序
    if source.section_name != target.section_name:
        return jsonify({'message': '只能在同一区域内排序'}), 400
    
    # 获取排序值
    source_order = source.category_order
    target_order = target.category_order
    
    if source_order < target_order:
        # 向下移动
        Category.query.filter(
            Category.section_name == source.section_name,
            Category.category_order > source_order,
            Category.category_order <= target_order
        ).update({
            Category.category_order: Category.category_order - 1
        })
        source.category_order = target_order
    else:
        # 向上移动
        Category.query.filter(
            Category.section_name == source.section_name,
            Category.category_order < source_order,
            Category.category_order >= target_order
        ).update({
            Category.category_order: Category.category_order + 1
        })
        source.category_order = target_order
    
    db.session.commit()
    return jsonify({'message': '排序更新成功'})

@app.route('/api/admin/categories/move', methods=['POST'])
@login_required
def admin_move_category():
    category_id = request.json.get('category_id')
    direction = request.json.get('direction')
    
    if not category_id or not direction:
        return jsonify({'message': '参数不完整'}), 400
    
    category = Category.query.get(category_id)
    if not category:
        return jsonify({'message': '分类不存在'}), 404
    
    if direction == 'up':
        # 获取同一区域中的上一个分类
        prev_category = Category.query.filter(
            Category.section_name == category.section_name,
            Category.category_order < category.category_order
        ).order_by(Category.category_order.desc()).first()
        
        if prev_category:
            # 交换排序值
            prev_order = prev_category.category_order
            prev_category.category_order = category.category_order
            category.category_order = prev_order
            db.session.commit()
    
    elif direction == 'down':
        # 获取同一区域中的下一个分类
        next_category = Category.query.filter(
            Category.section_name == category.section_name,
            Category.category_order > category.category_order
        ).order_by(Category.category_order).first()
        
        if next_category:
            # 交换排序值
            next_order = next_category.category_order
            next_category.category_order = category.category_order
            category.category_order = next_order
            db.session.commit()
    
    return jsonify({'message': '移动成功'})

@app.route('/api/admin/sections/delete', methods=['POST'])
@login_required
def admin_delete_section():
    data = request.get_json()
    section_name = data.get('section_name')
    
    if not section_name:
        return jsonify({'message': '区域名称不能为空'}), 400
        
    try:
        # 获取该区域下的所有分类
        categories = Category.query.filter_by(section_name=section_name).all()
        if not categories:
            return jsonify({'message': '区域不存在'}), 404
            
        # 删除每个分类下的所有链接
        for category in categories:
            Link.query.filter_by(category_id=category.id).delete()
            
        # 删除该区域下的所有分类
        Category.query.filter_by(section_name=section_name).delete()
        
        db.session.commit()
        return jsonify({'message': '区域删除成功'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'删除区域失败: {str(e)}'}), 500

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

@app.route('/api/auth/status')
def auth_status():
    if current_user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'username': current_user.username
        })
    return jsonify({
        'authenticated': False
    })

@app.route('/api/auth/logout', methods=['POST'])
@login_required
def api_logout():
    logout_user()
    return jsonify({'success': True})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # 确保应用启动时创建所有表
    app.run(debug=True, port=5000) 