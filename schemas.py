from flask_marshmallow import Marshmallow
from models import Link, Category, User, Page, Region

ma = Marshmallow()

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

class PageSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Page
    
    id = ma.auto_field()
    name = ma.auto_field()
    regions = ma.Nested(lambda: RegionSchema(only=('id', 'name')), many=True)

class RegionSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Region
    
    id = ma.auto_field()
    name = ma.auto_field()
    page_id = ma.auto_field()
    categories = ma.Nested(CategorySchema, many=True)

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
