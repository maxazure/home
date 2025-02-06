from flask_marshmallow import Marshmallow
from marshmallow import validates, ValidationError, fields, validate, Schema, EXCLUDE
from models import Link, Category, User, Page, Region, IPBlock
import re

ma = Marshmallow()

class BaseSchema(ma.SQLAlchemySchema):
    class Meta:
        model = None
        unknown = EXCLUDE
    
    def load(self, data, **kwargs):
        self.instance = kwargs.pop('instance', None)
        return super().load(data, **kwargs)

class LinkSchema(BaseSchema):
    class Meta:
        model = Link
        load_instance = True
    
    id = ma.auto_field()
    name = ma.auto_field()
    url = ma.auto_field()
    category_id = ma.auto_field()
    category = ma.Nested(lambda: CategorySchema(only=('id', 'title')))

    @validates('name')
    def validate_name(self, value):
        if not value:
            raise ValidationError('Name cannot be empty')
        if len(value) > 100:
            raise ValidationError('Name must be less than 100 characters')

    @validates('url')
    def validate_url(self, value):
        if not value:
            raise ValidationError('URL cannot be empty')
        if len(value) > 500:
            raise ValidationError('URL must be less than 500 characters')

class CategorySchema(BaseSchema):
    class Meta:
        model = Category
        load_instance = True
    
    id = ma.auto_field()
    title = ma.auto_field()
    section_name = ma.auto_field()
    section_order = ma.auto_field()
    category_order = ma.auto_field()
    region_id = ma.auto_field()
    links = ma.Nested(LinkSchema, many=True)

    @validates('title')
    def validate_title(self, value):
        if not value:
            raise ValidationError('Title cannot be empty')
        if len(value) > 100:
            raise ValidationError('Title must be less than 100 characters')

class IPBlockSchema(BaseSchema):
    class Meta:
        model = IPBlock
        load_instance = True
    
    id = ma.auto_field()
    ip_address = ma.auto_field()
    failed_attempts = ma.auto_field()
    is_blocked = ma.auto_field()
    last_attempt = ma.auto_field()
    created_at = ma.auto_field()

    @validates('ip_address')
    def validate_ip_address(self, value):
        if not value:
            raise ValidationError('IP address cannot be empty')
        if len(value) > 45:
            raise ValidationError('IP address must be less than 45 characters')
        if not re.match(r'^(\d{1,3}\.){3}\d{1,3}$', value):
            raise ValidationError('Invalid IP address format')

        existing_block = IPBlock.query.filter_by(ip_address=value).first()
        instance = getattr(self, 'instance', None)
        if existing_block and (not instance or existing_block.id != instance.id):
            raise ValidationError('IP address must be unique')

class UserSchema(BaseSchema):
    class Meta:
        model = User
        load_instance = True
    
    id = ma.auto_field()
    username = ma.auto_field()
    password = fields.String(load_only=True)  # 添加密码字段，仅用于加载
    created_at = ma.auto_field()
    is_locked = ma.auto_field()
    failed_login_attempts = ma.auto_field()
    last_failed_login = ma.auto_field()

    @validates('username')
    def validate_username(self, value):
        if not value:
            raise ValidationError('Username cannot be empty')
        if len(value) > 80:
            raise ValidationError('Username must be less than 80 characters')
        
        existing_user = User.query.filter_by(username=value).first()
        instance = getattr(self, 'instance', None)
        if existing_user and (not instance or existing_user.id != instance.id):
            raise ValidationError('Username must be unique')

class PageSchema(BaseSchema):
    class Meta:
        model = Page
    
    id = ma.auto_field()
    name = ma.auto_field()
    slug = fields.String(required=True)
    regions = ma.Nested(lambda: RegionSchema(only=('id', 'name')), many=True)

    @validates('slug')
    def validate_slug(self, value):
        # 验证 slug 不能为空
        if not value:
            raise ValidationError('Slug cannot be empty')
        
        # 验证长度
        if len(value) > 100:
            raise ValidationError('Slug must be less than 100 characters')
        
        # 验证格式（只允许小写字母、数字和连字符）
        if not re.match(r'^[a-z0-9-]+$', value):
            raise ValidationError('Slug can only contain lowercase letters, numbers, and hyphens')

        # 验证唯一性（如果需要）
        existing_page = Page.query.filter_by(slug=value).first()
        instance = getattr(self, 'instance', None)
        if existing_page and (not instance or existing_page.id != instance.id):
            raise ValidationError('Slug must be unique')

    @validates('name')
    def validate_name(self, value):
        if not value:
            raise ValidationError('Name cannot be empty')

class RegionSchema(BaseSchema):
    class Meta:
        model = Region
        load_instance = True
    
    id = ma.auto_field()
    name = ma.auto_field()
    page_id = ma.auto_field()
    categories = ma.Nested(CategorySchema, many=True)

    @validates('name')
    def validate_name(self, value):
        if not value:
            raise ValidationError('Name cannot be empty')
        if len(value) > 100:
            raise ValidationError('Name must be less than 100 characters')

# 创建schema实例
link_schema = LinkSchema()
links_schema = LinkSchema(many=True)
category_schema = CategorySchema()
categories_schema = CategorySchema(many=True)
user_schema = UserSchema()
users_schema = UserSchema(many=True)
page_schema = PageSchema()
pages_schema = PageSchema(many=True)
region_schema = RegionSchema()
regions_schema = RegionSchema(many=True)
ipblock_schema = IPBlockSchema()
ipblocks_schema = IPBlockSchema(many=True)
