import unittest
from flask import Flask
from models import db, Page, Region, User, IPBlock, Category, Link
from schemas import (
    page_schema, region_schema, user_schema, ipblock_schema,
    category_schema, link_schema
)
from marshmallow import ValidationError  # 添加这行导入
from datetime import datetime

class BaseSchemaTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(self.app)
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

class LinkSchemaTestCase(BaseSchemaTestCase):
    def test_link_serialization(self):
        with self.app.app_context():
            category = Category(title="Programming", section_name="Development")
            link = Link(name="GitHub", url="https://github.com", category=category)
            db.session.add(category)
            db.session.add(link)
            db.session.commit()

            result = link_schema.dump(link)
            self.assertEqual(result['name'], "GitHub")
            self.assertEqual(result['url'], "https://github.com")
            self.assertIn('category', result)
            self.assertEqual(result['category']['title'], "Programming")

    def test_link_validation(self):
        with self.app.app_context():
            category = Category(title="Test", section_name="Test")
            db.session.add(category)
            db.session.commit()

            # 测试空名称
            invalid_data = {
                'url': 'https://example.com',
                'category_id': category.id
            }
            with self.assertRaises(ValidationError):
                link_schema.load(invalid_data)

            # 测试过长的 URL
            invalid_data = {
                'name': 'Test',
                'url': 'https://' + 'a' * 500,
                'category_id': category.id
            }
            with self.assertRaises(ValidationError):
                link_schema.load(invalid_data)

class CategorySchemaTestCase(BaseSchemaTestCase):
    def test_category_serialization(self):
        with self.app.app_context():
            category = Category(
                title="Programming",
                section_name="Development",
                section_order=1,
                category_order=1
            )
            db.session.add(category)
            db.session.commit()

            result = category_schema.dump(category)
            self.assertEqual(result['title'], "Programming")
            self.assertEqual(result['section_name'], "Development")
            self.assertEqual(result['section_order'], 1)
            self.assertEqual(result['category_order'], 1)

class UserSchemaTestCase(BaseSchemaTestCase):
    def test_user_serialization(self):
        with self.app.app_context():
            user = User(username="testuser")
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()

            result = user_schema.dump(user)
            self.assertEqual(result['username'], "testuser")
            self.assertNotIn('password_hash', result)
            self.assertIn('created_at', result)

    def test_user_validation(self):
        with self.app.app_context():
            # 创建用户
            user = User(username="testuser")
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()

            with self.assertRaises(ValidationError):
                user_schema.load(
                    {'username': 'testuser', 'password': 'newpassword'},
                    instance=None
                )

class PageSchemaTestCase(BaseSchemaTestCase):
    def test_page_serialization(self):
        with self.app.app_context():
            page = Page(name="Test Page")
            region = Region(name="Header", page=page)
            db.session.add(page)
            db.session.add(region)
            db.session.commit()

            result = page_schema.dump(page)
            self.assertEqual(result['name'], "Test Page")
            self.assertEqual(result['slug'], "test-page")
            self.assertEqual(len(result['regions']), 1)
            self.assertEqual(result['regions'][0]['name'], "Header")

    def test_page_validation(self):
        with self.app.app_context():
            # 测试无效的 slug 格式
            invalid_data = {
                'name': 'Test Page',
                'slug': 'Invalid Slug!'
            }
            with self.assertRaises(ValidationError):
                page_schema.load(invalid_data)

            # 测试 slug 唯一性
            page = Page(name="Test Page")
            db.session.add(page)
            db.session.commit()

            duplicate_data = {
                'name': 'Another Page',
                'slug': page.slug
            }
            with self.assertRaises(ValidationError):
                page_schema.load(duplicate_data, instance=None)

class RegionSchemaTestCase(BaseSchemaTestCase):
    def test_region_serialization(self):
        with self.app.app_context():
            page = Page(name="Test Page")
            region = Region(name="Sidebar", page=page)
            category = Category(title="Links", section_name="Main", region=region)
            db.session.add_all([page, region, category])
            db.session.commit()

            result = region_schema.dump(region)
            self.assertEqual(result['name'], "Sidebar")
            self.assertEqual(result['page_id'], page.id)
            self.assertEqual(len(result['categories']), 1)
            self.assertEqual(result['categories'][0]['title'], "Links")

class IPBlockSchemaTestCase(BaseSchemaTestCase):
    def test_ipblock_serialization(self):
        with self.app.app_context():
            ip_block = IPBlock(
                ip_address="192.168.1.1",
                failed_attempts=3,
                is_blocked=True
            )
            db.session.add(ip_block)
            db.session.commit()

            result = ipblock_schema.dump(ip_block)
            self.assertEqual(result['ip_address'], "192.168.1.1")
            self.assertEqual(result['failed_attempts'], 3)
            self.assertTrue(result['is_blocked'])

    def test_ipblock_validation(self):
        with self.app.app_context():
            # 测试无效的 IP 地址格式
            invalid_data = {
                'ip_address': 'invalid-ip'
            }
            with self.assertRaises(ValidationError):
                ipblock_schema.load(invalid_data)

            # 测试有效但重复的 IP 地址
            valid_ip = "192.168.1.1"
            ip_block = IPBlock(ip_address=valid_ip)
            db.session.add(ip_block)
            db.session.commit()

            with self.assertRaises(ValidationError):
                ipblock_schema.load({'ip_address': valid_ip}, instance=None)

if __name__ == '__main__':
    unittest.main()
