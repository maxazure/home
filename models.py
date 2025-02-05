from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

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
