import unittest
from flask import url_for
from app import app, db
from models import User, Page

class BaseTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app
        self.client = app.test_client()
        self.ctx = app.test_request_context()
        self.ctx.push()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()
        self.ctx.pop()

class AppTestCase(BaseTestCase):
    def test_index_route(self):
        """测试首页路由"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_page_route_with_valid_slug(self):
        """测试有效的页面 slug 路由"""
        with self.app.app_context():
            # 创建测试页面
            page = Page(name="Test Page")
            db.session.add(page)
            db.session.commit()

            response = self.client.get(f'/{page.slug}')
            self.assertEqual(response.status_code, 200)

    def test_page_route_with_invalid_slug(self):
        """测试无效的页面 slug 路由"""
        with self.app.app_context():
            response = self.client.get('/nonexistent-page')
            self.assertEqual(response.status_code, 404)

    def test_404_error_handler(self):
        """测试 404 错误处理"""
        with self.app.app_context():
            response = self.client.get('/nonexistent-route')
            self.assertEqual(response.status_code, 404)
            self.assertIn('error', response.json)
            self.assertIn('path', response.json)

class CommandsTestCase(BaseTestCase):
    def test_init_db_command(self):
        """测试初始化数据库命令"""
        runner = app.test_cli_runner()
        result = runner.invoke(args=['init-db'])
        
        self.assertEqual(result.exit_code, 0)
        # 验证是否创建了默认首页
        home_page = Page.query.filter_by(slug='home').first()
        self.assertIsNotNone(home_page)
        self.assertEqual(home_page.name, "Home")

    def test_create_admin_command(self):
        """测试创建管理员命令"""
        runner = app.test_cli_runner()
        result = runner.invoke(args=['create-admin'])
        
        self.assertEqual(result.exit_code, 0)
        # 验证管理员用户是否创建
        admin = User.query.filter_by(username='admin').first()
        self.assertIsNotNone(admin)
        self.assertTrue(admin.check_password('admin123'))

    def test_create_admin_command_duplicate(self):
        """测试重复创建管理员的情况"""
        # 先创建一个管理员
        user = User(username='admin')
        user.set_password('admin123')
        db.session.add(user)
        db.session.commit()

        # 尝试再次创建
        runner = app.test_cli_runner()
        result = runner.invoke(args=['create-admin'])
        
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Admin user already exists', result.output)

class ConfigTestCase(BaseTestCase):
    def test_app_configuration(self):
        """测试应用配置"""
        self.assertTrue(app.config['TESTING'])
        self.assertFalse(app.config['SQLALCHEMY_TRACK_MODIFICATIONS'])
        self.assertIsNotNone(app.config['SECRET_KEY'])
        self.assertEqual(app.static_url_path, '')

    def test_database_configuration(self):
        """测试数据库配置"""
        self.assertTrue(app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite://'))

    def test_session_configuration(self):
        """测试会话配置"""
        self.assertIsNotNone(app.config['PERMANENT_SESSION_LIFETIME'])
        self.assertEqual(app.config['PERMANENT_SESSION_LIFETIME'].days, 30)

class BlueprintTestCase(BaseTestCase):
    def test_blueprints_registered(self):
        """测试蓝图注册"""
        blueprints = ['auth', 'category', 'link', 'admin_category', 'admin_link', 'admin_page', 'admin_region', 'page', 'region']
        for blueprint in blueprints:
            self.assertIn(blueprint, app.blueprints)

    def test_blueprint_url_prefixes(self):
        """测试蓝图 URL 前缀"""
        self.assertEqual(app.blueprints['admin_page'].url_prefix, '/api/pages')
        self.assertEqual(app.blueprints['admin_region'].url_prefix, '/api/regions')

if __name__ == '__main__':
    unittest.main()
