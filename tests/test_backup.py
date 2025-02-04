import unittest
import json
import os
from app import app, db, Category, Link, User
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
        response = self.client.get('/api/admin/export')
        self.assertEqual(response.status_code, 200)
        
        # 验证导出的JSON格式
        data = response.json
        self.assertIn('categories', data)
        self.assertIn('links', data)
        self.assertEqual(len(data['categories']), 0)
        self.assertEqual(len(data['links']), 0)
    
    def test_export_with_data(self):
        """测试导出包含数据的情况"""
        # 创建测试数据
        with app.app_context():
            category = Category(
                title='测试分类',
                section_name='测试区域',
                section_order=1,
                category_order=1
            )
            db.session.add(category)
            db.session.flush()
            
            link = Link(
                name='测试链接',
                url='http://test.com',
                category_id=category.id
            )
            db.session.add(link)
            db.session.commit()
        
        # 测试导出
        response = self.client.get('/api/admin/export')
        self.assertEqual(response.status_code, 200)
        
        # 验证导出的数据
        data = response.json
        self.assertEqual(len(data['categories']), 1)
        self.assertEqual(len(data['links']), 1)
        self.assertEqual(data['categories'][0]['title'], '测试分类')
        self.assertEqual(data['links'][0]['name'], '测试链接')
    
    def test_import_valid_data(self):
        """测试导入有效数据"""
        # 准备测试数据
        test_data = {
            'categories': [{
                'title': '导入测试分类',
                'section_name': '导入测试区域',
                'section_order': 1,
                'category_order': 1
            }],
            'links': [{
                'name': '导入测试链接',
                'url': 'http://import-test.com',
                'category_title': '导入测试分类',
                'section_name': '导入测试区域'
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
        
        self.assertEqual(response.status_code, 200)
        
        # 验证导入的数据
        with app.app_context():
            categories = Category.query.all()
            links = Link.query.all()
            
            self.assertEqual(len(categories), 1)
            self.assertEqual(len(links), 1)
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
        
        self.assertEqual(response.status_code, 400)
    
    def test_import_with_different_encodings(self):
        """测试导入不同编码的文件"""
        # 准备测试数据
        test_data = {
            'categories': [{
                'title': '中文测试分类',
                'section_name': '中文测试区域',
                'section_order': 1,
                'category_order': 1
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
        
        # 测试 GBK 编码
        gbk_data = json.dumps(test_data, ensure_ascii=False).encode('gbk')
        gbk_file = (BytesIO(gbk_data), 'gbk.json')
        response = self.client.post(
            '/api/admin/import',
            data={'file': gbk_file},
            content_type='multipart/form-data'
        )
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main() 