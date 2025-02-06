import unittest
import json
import os
from app import app, db
from models import Category, Link, User, Page, Region
from io import BytesIO

class TestBackupFeatures(unittest.TestCase):
    def setUp(self):
        # 配置测试数据库
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        
        # 创建测试客户端
        self.client = app.test_client()
        
        # 创建数据库表
        with app.app_context():
            db.create_all()
            
            # 创建测试用户
            user = User(username='test_admin')
            user.set_password('test_password')
            db.session.add(user)
            db.session.commit()
            
            # 登录用户
            self.client.post('/api/admin/login', json={
                'username': 'test_admin',
                'password': 'test_password'
            })
    
    def tearDown(self):
        # 清理数据库
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_export_empty_data(self):
        """测试导出空数据"""
        with self.client as client:
            response = client.get('/api/admin/export')
            self.assertEqual(response.status_code, 200)
            
            # 验证响应类型和内容
            self.assertTrue(response.content_type.startswith('application/json'))
            # 获取响应内容并解析
            content = response.get_data(as_text=True)
            data = json.loads(content)
            
            self.assertIn('pages', data)
            self.assertIn('regions', data)
            self.assertIn('categories', data)
            self.assertIn('links', data)
            self.assertEqual(len(data['pages']), 0)
            self.assertEqual(len(data['regions']), 0)
            self.assertEqual(len(data['categories']), 0)
            self.assertEqual(len(data['links']), 0)
    
    def test_export_with_data(self):
        """测试导出包含数据的情况"""
        # 创建测试数据
        with app.app_context():
            # 创建页面
            page = Page(name='测试页面')
            db.session.add(page)
            db.session.flush()
            
            # 创建区域
            region = Region(name='测试区域', page_id=page.id)
            db.session.add(region)
            db.session.flush()
            
            # 创建分类
            category = Category(
                title='测试分类',
                section_name='测试区域',
                section_order=1,
                category_order=1,
                region_id=region.id
            )
            db.session.add(category)
            db.session.flush()
            
            # 创建链接
            link = Link(
                name='测试链接',
                url='http://test.com',
                category_id=category.id
            )
            db.session.add(link)
            db.session.commit()
        
        # 测试导出
        with self.client as client:
            response = client.get('/api/admin/export')
            self.assertEqual(response.status_code, 200)
            
            # 验证响应类型和内容
            self.assertTrue(response.content_type.startswith('application/json'))
            # 获取响应内容并解析
            content = response.get_data(as_text=True)
            data = json.loads(content)
            
            self.assertEqual(len(data['pages']), 1)
            self.assertEqual(len(data['regions']), 1)
            self.assertEqual(len(data['categories']), 1)
            self.assertEqual(len(data['links']), 1)
            self.assertEqual(data['pages'][0]['name'], '测试页面')
            self.assertEqual(data['regions'][0]['name'], '测试区域')
            self.assertEqual(data['categories'][0]['title'], '测试分类')
            self.assertEqual(data['links'][0]['name'], '测试链接')
    
    def test_import_valid_data(self):
        """测试导入有效数据"""
        # 准备测试数据
        test_data = {
            'pages': [{
                'name': '导入测试页面',
                'slug': 'import-test-page'
            }],
            'regions': [{
                'name': '导入测试区域',
                'page_slug': 'import-test-page'
            }],
            'categories': [{
                'title': '导入测试分类',
                'section_name': '导入测试区域',
                'section_order': 1,
                'category_order': 1,
                'region_name': '导入测试区域'
            }],
            'links': [{
                'name': '导入测试链接',
                'url': 'http://import-test.com',
                'category_title': '导入测试分类'
            }]
        }
        
        # 创建测试文件
        data = json.dumps(test_data, ensure_ascii=False).encode('utf-8')
        file = (BytesIO(data), 'test_backup.json')
        
        # 测试导入
        response = self.client.post(
            '/api/admin/import',
            data={'file': file},
            content_type='multipart/form-data'
        )
        file[0].close()  # 关闭文件以避免 ResourceWarning
        
        self.assertEqual(response.status_code, 200)
        
        # 验证导入的数据
        with app.app_context():
            pages = Page.query.all()
            regions = Region.query.all()
            categories = Category.query.all()
            links = Link.query.all()
            
            self.assertEqual(len(pages), 1)
            self.assertEqual(len(regions), 1)
            self.assertEqual(len(categories), 1)
            self.assertEqual(len(links), 1)
            self.assertEqual(pages[0].name, '导入测试页面')
            self.assertEqual(regions[0].name, '导入测试区域')
            self.assertEqual(categories[0].title, '导入测试分类')
            self.assertEqual(links[0].name, '导入测试链接')
    
    def test_import_invalid_json(self):
        """测试导入无效的JSON数据"""
        # 创建无效的JSON文件
        invalid_data = b'{"invalid": "json"'
        file = (BytesIO(invalid_data), 'invalid.json')
        
        # 测试导入
        response = self.client.post(
            '/api/admin/import',
            data={'file': file},
            content_type='multipart/form-data'
        )
        file[0].close()  # 关闭文件以避免 ResourceWarning
        
        self.assertEqual(response.status_code, 400)
    
    def test_import_invalid_format(self):
        """测试导入格式错误的数据"""
        # 准备格式错误的数据
        invalid_data = {
            'wrong_key': []
        }
        
        # 创建测试文件
        data = json.dumps(invalid_data).encode('utf-8')
        file = (BytesIO(data), 'invalid_format.json')
        
        # 测试导入
        response = self.client.post(
            '/api/admin/import',
            data={'file': file},
            content_type='multipart/form-data'
        )
        file[0].close()  # 关闭文件以避免 ResourceWarning
        
        self.assertEqual(response.status_code, 400)
    
    def test_import_with_different_encodings(self):
        """测试导入不同编码的文件"""
        # 准备测试数据
        test_data = {
            'pages': [{
                'name': '测试页面',
                'slug': 'test-page'
            }],
            'regions': [{
                'name': '测试区域',
                'page_slug': 'test-page'
            }],
            'categories': [{
                'title': '中文测试分类',
                'section_name': '中文测试区域',
                'section_order': 1,
                'category_order': 1,
                'region_name': '测试区域'
            }],
            'links': []
        }
        
        # 测试 UTF-8 编码
        utf8_data = json.dumps(test_data, ensure_ascii=False).encode('utf-8')
        utf8_file = (BytesIO(utf8_data), 'utf8.json')
        response = self.client.post(
            '/api/admin/import',
            data={'file': utf8_file},
            content_type='multipart/form-data'
        )
        self.assertEqual(response.status_code, 200)
        utf8_file[0].close()  # 关闭文件以避免 ResourceWarning
        
        # 测试 GBK 编码
        gbk_data = json.dumps(test_data, ensure_ascii=False).encode('gbk')
        gbk_file = (BytesIO(gbk_data), 'gbk.json')
        response = self.client.post(
            '/api/admin/import',
            data={'file': gbk_file},
            content_type='multipart/form-data'
        )
        self.assertEqual(response.status_code, 200)
        gbk_file[0].close()  # 关闭文件以避免 ResourceWarning

if __name__ == '__main__':
    unittest.main()
