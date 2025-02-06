from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timezone
import re

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
        self.last_failed_login = datetime.now(timezone.utc)
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
    region_id = db.Column(db.Integer, db.ForeignKey('regions.id', ondelete='CASCADE'), nullable=True)
    links = db.relationship('Link', backref='category', lazy=True,
                          cascade='all, delete-orphan')

class Link(db.Model):
    __tablename__ = 'links'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='CASCADE'), nullable=False)

class Page(db.Model):
    __tablename__ = 'pages'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    regions = db.relationship('Region', backref='page', lazy=True,
                            cascade='all, delete-orphan')

    def generate_slug(self):
        """从名称生成 URL 友好的 slug"""
        # 转换为小写，替换空格为横线
        slug = self.name.lower()
        # 删除特殊字符
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        # 替换空格为横线
        slug = re.sub(r'\s+', '-', slug)
        # 删除多余的横线
        slug = re.sub(r'-+', '-', slug)
        # 去除首尾横线
        slug = slug.strip('-')
        return slug

    def __init__(self, name):
        self.name = name
        self.slug = self.generate_slug()

class Region(db.Model):
    __tablename__ = 'regions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    page_id = db.Column(db.Integer, db.ForeignKey('pages.id', ondelete='CASCADE'), nullable=True)  # 新增外键
    categories = db.relationship('Category', backref='region', lazy=True,
                               cascade='all, delete-orphan')
