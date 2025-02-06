import unittest
from app import app, db
from models import User, IPBlock
from schemas import user_schema, ipblock_schema
import json
from datetime import datetime
from flask_login import current_user

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app  # 保存 app 引用
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_login_success(self):
        """测试登录成功"""
        with self.app.app_context():
            # 创建测试用户
            user = User(username="testuser")
            user.set_password("testpass")
            db.session.add(user)
            db.session.commit()

            response = self.client.post('/api/login',
                json={'username': 'testuser', 'password': 'testpass'})
            data = json.loads(response.data)
            
            self.assertEqual(response.status_code, 200)
            self.assertTrue(data['success'])
            self.assertEqual(data['user']['username'], 'testuser')

    def test_login_validation(self):
        """测试登录数据验证"""
        # 空数据测试
        response = self.client.post('/api/login', json={})
        self.assertEqual(response.status_code, 400)

        # 缺少密码测试
        response = self.client.post('/api/login',
            json={'username': 'testuser'})
        self.assertEqual(response.status_code, 400)

        # 缺少用户名测试
        response = self.client.post('/api/login',
            json={'password': 'testpass'})
        self.assertEqual(response.status_code, 400)

    def test_ip_blocking(self):
        """测试 IP 封禁功能"""
        with self.app.app_context():
            IPBlock.query.delete()
            db.session.commit()

            # 不存在的用户，触发 IP 失败计数
            for _ in range(10):
                response = self.client.post(
                    '/api/login',
                    json={'username': 'nonexistentuser', 'password': 'any'}
                )
            # 第 10 次应返回 403
            self.assertEqual(response.status_code, 403)
            self.assertIn('访问被拒绝', response.get_json()['message'])

            # 验证 IP 封禁
            ip_block = IPBlock.query.filter_by(ip_address='127.0.0.1').first()
            self.assertTrue(ip_block.is_blocked)

            # 尝试正确登录，仍应 403，且提示同样消息
            response = self.client.post(
                '/api/login',
                json={'username': 'testuser', 'password': 'testpass'}
            )
            self.assertEqual(response.status_code, 403)
            self.assertIn('访问被拒绝', response.get_json()['message'])

    def test_ip_blocking_early_prevention(self):
        """测试 IP 封禁应在验证用户名密码前阻止访问"""
        with self.app.app_context():
            blocked_ip = IPBlock(ip_address='127.0.0.1', is_blocked=True)
            db.session.add(blocked_ip)
            db.session.commit()

            user = User(username="blocked_ip_user")
            user.set_password("testpass")
            db.session.add(user)
            db.session.commit()

            response = self.client.post('/api/login',
                json={'username': 'blocked_ip_user', 'password': 'testpass'})
            self.assertEqual(response.status_code, 403)
            self.assertIn('访问被拒绝', response.get_json()['message'])

    def test_account_locking(self):
        """测试账户锁定功能"""
        with self.app.app_context():
            User.query.filter(User.username == "testuser").delete()
            IPBlock.query.delete()
            db.session.commit()

            user = User(username="testuser")
            user.set_password("testpass")
            db.session.add(user)
            db.session.commit()

            # 前 9 次错误在 IP 2.2.2.2
            for _ in range(9):
                response = self.client.post(
                    '/api/login',
                    json={'username': 'testuser', 'password': 'wrongpass'},
                    environ_base={'REMOTE_ADDR': '2.2.2.2'}
                )

            # 第 10 次错误在 IP 3.3.3.3
            response = self.client.post(
                '/api/login',
                json={'username': 'testuser', 'password': 'wrongpass'},
                environ_base={'REMOTE_ADDR': '3.3.3.3'}
            )

            # 此时应锁定用户，返回 403
            self.assertEqual(response.status_code, 403)
            self.assertIn('访问被拒绝', response.get_json()['message'])

            # 验证用户被锁定
            locked_user = User.query.filter_by(username='testuser').first()
            self.assertTrue(locked_user.is_locked)
            self.assertEqual(locked_user.failed_login_attempts, 10)

            # 使用正确密码仍应 403
            response = self.client.post(
                '/api/login',
                json={'username': 'testuser', 'password': 'testpass'}
            )
            self.assertEqual(response.status_code, 403)
            self.assertIn('访问被拒绝', response.get_json()['message'])

    def test_auth_status(self):
        """测试认证状态接口"""
        with self.app.app_context():
            # 未登录状态
            response = self.client.get('/api/auth/status')
            self.assertEqual(response.status_code, 200)
            self.assertFalse(response.get_json()['authenticated'])

            # 登录后状态
            user = User(username="testuser")
            user.set_password("testpass")
            db.session.add(user)
            db.session.commit()

            self.client.post('/api/login',
                json={'username': 'testuser', 'password': 'testpass'})
        
            response = self.client.get('/api/auth/status')
            data = response.get_json()
            self.assertTrue(data['authenticated'])
            self.assertEqual(data['user']['username'], 'testuser')

    def test_logout(self):
        """测试登出功能"""
        with self.app.app_context():
            # 先登录
            user = User(username="testuser")
            user.set_password("testpass")
            db.session.add(user)
            db.session.commit()

            self.client.post('/api/login',
                json={'username': 'testuser', 'password': 'testpass'})
        
            # 测试登出
            response = self.client.get('/api/logout')
            self.assertEqual(response.status_code, 200)
        
            # 验证登出后状态
            response = self.client.get('/api/auth/status')
            self.assertFalse(response.get_json()['authenticated'])

if __name__ == '__main__':
    unittest.main()