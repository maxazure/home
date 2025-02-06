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
            response = self.client.post('/api/login', json={
                'username': 'test_admin',
                'password': 'test_password'
            })
            self.assertEqual(response.status_code, 200)
            
            # 验证登录状态
            response = self.client.get('/api/auth/status')
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertTrue(data['authenticated'])
    
    def tearDown(self):
        # 清理数据库
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_export_empty_data(self):
        """测试导出空数据"""
        with self.client as client:
            response = client.get('/api/admin/backup/export')
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
        with app.app_context():
            # 创建测试数据
            page = Page(name='Test Page')
            db.session.add(page)
            db.session.commit()

        with self.client as client:
            response = client.get('/api/admin/backup/export')
            self.assertEqual(response.status_code, 200)
            
            # 验证响应类型和内容
            self.assertTrue(response.content_type.startswith('application/json'))
            # 获取响应内容并解析
            content = response.get_data(as_text=True)
            data = json.loads(content)
            
            self.assertEqual(len(data['pages']), 1)
            self.assertEqual(len(data['regions']), 0)
            self.assertEqual(len(data['categories']), 0)
            self.assertEqual(len(data['links']), 0)
            self.assertEqual(data['pages'][0]['name'], 'Test Page')
    
    def test_import_valid_data(self):
        """测试导入有效数据"""
        test_data = {
            'pages': [],
            'regions': [],
            'categories': [],
            'links': []
        }
        
        data = json.dumps(test_data).encode('utf-8')
        data = BytesIO(data)
        
        with self.client as client:
            response = client.post('/api/admin/backup/import',
                                 data={'file': (data, 'backup.json')},
                                 content_type='multipart/form-data')
            self.assertEqual(response.status_code, 200)
        
        # 验证导入的数据
        with app.app_context():
            pages = Page.query.all()
            regions = Region.query.all()
            categories = Category.query.all()
            links = Link.query.all()
            
            self.assertEqual(len(pages), 0)
            self.assertEqual(len(regions), 0)
            self.assertEqual(len(categories), 0)
            self.assertEqual(len(links), 0)
    
    def test_import_invalid_json(self):
        """测试导入无效的JSON数据"""
        data = BytesIO(b'invalid json data')
        
        with self.client as client:
            response = client.post('/api/admin/backup/import',
                                 data={'file': (data, 'backup.json')},
                                 content_type='multipart/form-data')
            self.assertEqual(response.status_code, 400)
    
    def test_import_invalid_format(self):
        """测试导入格式错误的数据"""
        data = BytesIO(b'test data')
        
        with self.client as client:
            response = client.post('/api/admin/backup/import',
                                 data={'file': (data, 'backup.txt')},
                                 content_type='multipart/form-data')
            self.assertEqual(response.status_code, 400)
    
    def test_import_with_different_encodings(self):
        """测试导入不同编码的文件"""
        test_data = {
            'pages': [],
            'regions': [],
            'categories': [],
            'links': []
        }
        
        # UTF-8编码
        data = json.dumps(test_data).encode('utf-8')
        data = BytesIO(data)
        
        with self.client as client:
            response = client.post('/api/admin/backup/import',
                                 data={'file': (data, 'backup.json')},
                                 content_type='multipart/form-data')
            self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()