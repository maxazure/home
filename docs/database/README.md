# 数据库说明文档

## 目录

1. [数据库概述](#数据库概述)
2. [数据模型](#数据模型)
3. [数据关系](#数据关系)
4. [数据库迁移](#数据库迁移)
5. [Schema定义](#schema定义)

## 数据库概述

本项目使用 SQLite 作为数据库，通过 SQLAlchemy ORM 进行数据库操作。数据库文件位于 `instance/links.db`。

主要特点：
- 使用 Flask-SQLAlchemy 作为 ORM
- 使用 Flask-Migrate 进行数据库迁移
- 使用 Flask-Marshmallow 进行数据序列化

## 数据模型

### User 模型
用户表，用于存储管理员账户信息。

```python
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    is_locked = db.Column(db.Boolean, default=False)
    failed_login_attempts = db.Column(db.Integer, default=0)
    last_failed_login = db.Column(db.DateTime)
```

### IPBlock 模型
IP封禁表，用于存储IP限制信息。

```python
class IPBlock(db.Model):
    __tablename__ = 'ip_blocks'
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(45), unique=True, nullable=False)
    failed_attempts = db.Column(db.Integer, default=0)
    is_blocked = db.Column(db.Boolean, default=False)
    last_attempt = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
```

### Category 模型
分类表，用于存储导航分类信息。

```python
class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    section_name = db.Column(db.String(100), nullable=False)
    section_order = db.Column(db.Integer, default=0)  # 区域排序
    category_order = db.Column(db.Integer, default=0)  # 分类排序
    links = db.relationship('Link', backref='category', lazy=True)
```

### Link 模型
链接表，用于存储导航链接信息。

```python
class Link(db.Model):
    __tablename__ = 'links'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
```

## 数据关系

1. Category 和 Link 是一对多关系：
   - 一个分类可以包含多个链接
   - 每个链接必须属于一个分类
   - 通过 `category_id` 外键关联

2. 区域组织：
   - 通过 `section_name` 字段对分类进行分组
   - 使用 `section_order` 控制区域排序
   - 使用 `category_order` 控制分类在区域内的排序

## 数据库迁移

### 迁移历史

1. 初始迁移 (4133e604cdf7)：
   - 创建基础表结构：categories、user、links
   - 建立外键关系

2. 用户锁定迁移 (49fd44a5afe9)：
   - 添加用户锁定功能
   - 添加登录失败计数
   - 添加最后失败时间

3. 分类排序迁移 (af90b1b6c237)：
   - 添加区域排序字段 (section_order)

4. 分类内部排序迁移 (01a57a76ae49)：
   - 添加分类排序字段 (category_order)

### 迁移命令

```bash
# 创建新的迁移
flask db migrate -m "迁移说明"

# 应用迁移
flask db upgrade

# 回滚迁移
flask db downgrade
```

## Schema定义

使用 Flask-Marshmallow 进行数据序列化，主要包含以下 Schema：

### LinkSchema
```python
class LinkSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Link
    id = ma.auto_field()
    name = ma.auto_field()
    url = ma.auto_field()
    category_id = ma.auto_field()
```

### CategorySchema
```python
class CategorySchema(ma.SQLAlchemySchema):
    class Meta:
        model = Category
    id = ma.auto_field()
    title = ma.auto_field()
    section_name = ma.auto_field()
    links = ma.Nested(LinkSchema, many=True)
```

### UserSchema
```python
class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User
    id = ma.auto_field()
    username = ma.auto_field()
    created_at = ma.auto_field()
```

## 数据库管理

### 初始化数据库
```bash
flask init-db  # 创建数据库表
flask create-admin  # 创建管理员账户
```

### 数据导入导出
使用 `import_data.py` 脚本进行数据导入：
```bash
python import_data.py  # 使用默认数据
python import_data.py data.json  # 从JSON文件导入
```

### 数据备份
每次导入数据时会自动创建备份文件 `data_backup.json`。

### 安全建议
1. 定期备份数据库文件
2. 使用强密码保护管理员账户
3. 及时更新数据库迁移
4. 监控异常登录尝试 