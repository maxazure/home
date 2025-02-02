import unittest
from app import app, db, User, IPBlock
from flask_login import current_user
import json

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        """测试前的设置"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # 使用内存数据库进行测试
        self.client = app.test_client()
        
        with app.app_context():
            db.create_all()
            # 创建测试用户
            user = User(username='testuser')
            user.set_password('testpass')
            db.session.add(user)
            db.session.commit()
    
    def tearDown(self):
        """测试后的清理"""
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_login_success(self):
        """测试登录成功"""
        response = self.client.post('/api/admin/login',
            json={'username': 'testuser', 'password': 'testpass'})
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
    
    def test_login_wrong_password(self):
        """测试密码错误"""
        response = self.client.post('/api/admin/login',
            json={'username': 'testuser', 'password': 'wrongpass'})
        self.assertEqual(response.status_code, 401)
    
    def test_login_nonexistent_user(self):
        """测试用户不存在"""
        response = self.client.post('/api/admin/login',
            json={'username': 'nonexistentuser', 'password': 'wrongpass'})
        self.assertEqual(response.status_code, 401)
    
    def test_login_rate_limit(self):
        """测试登录频率限制"""
        for _ in range(5):
            response = self.client.post('/api/admin/login',
                json={'username': 'testuser', 'password': 'wrongpass'})
            self.assertEqual(response.status_code, 429)
    
    def test_failed_login_user_lock(self):
        """测试用户多次登录失败导致账户锁定"""
        with app.app_context():
            # 先创建一个新用户专门用于测试锁定
            test_user = User(username='locktest')
            test_user.set_password('testpass')
            db.session.add(test_user)
            db.session.commit()
            
            # 尝试9次错误登录
            for i in range(9):
                response = self.client.post('/admin/login', 
                    json={'username': 'locktest', 'password': 'wrongpass'})
                self.assertEqual(response.status_code, 401)
            
            # 第10次尝试登录，应该导致账户锁定
            response = self.client.post('/admin/login', 
                json={'username': 'locktest', 'password': 'wrongpass'})
            
            # 验证用户确实被锁定
            user = User.query.filter_by(username='locktest').first()
            self.assertTrue(user.is_locked)
            self.assertEqual(user.failed_login_attempts, 10)
    
    def test_ip_block(self):
        """测试IP限制功能"""
        with app.app_context():
            # 尝试10次错误登录
            for i in range(10):
                response = self.client.post('/admin/login', 
                    json={'username': 'wronguser', 'password': 'wrongpass'})
                self.assertEqual(response.status_code, 401)
            
            # 第11次尝试登录，应该返回IP被封禁信息
            response = self.client.post('/admin/login', 
                json={'username': 'wronguser', 'password': 'wrongpass'})
            data = json.loads(response.data)
            self.assertEqual(response.status_code, 403)
            self.assertIn('IP已被封禁', data['message'])
            
            # 验证IP确实被封禁
            ip_block = IPBlock.query.filter_by(ip_address='127.0.0.1').first()
            self.assertIsNotNone(ip_block)
            self.assertTrue(ip_block.is_blocked)
    
    def test_unblock_ip(self):
        """测试解封IP功能"""
        with app.app_context():
            # 创建一个管理员用户
            admin = User(username='admin')
            admin.set_password('adminpass')
            db.session.add(admin)
            db.session.commit()
            
            # 先登录管理员
            response = self.client.post('/admin/login', 
                json={'username': 'admin', 'password': 'adminpass'})
            self.assertEqual(response.status_code, 200)
            
            # 创建一个被封禁的IP
            ip_block = IPBlock(
                ip_address='192.168.1.1',  # 使用不同的IP地址
                failed_attempts=10,
                is_blocked=True
            )
            db.session.add(ip_block)
            db.session.commit()
            
            # 解封IP
            response = self.client.post(f'/api/admin/ip-blocks/{ip_block.id}/unblock')
            data = json.loads(response.data)
            self.assertEqual(response.status_code, 200)
            self.assertIn('IP已解封', data['message'])
            
            # 验证IP已解封
            ip_block = IPBlock.query.filter_by(ip_address='192.168.1.1').first()
            self.assertFalse(ip_block.is_blocked)
            self.assertEqual(ip_block.failed_attempts, 0)
    
    def test_unlock_user(self):
        """测试解锁用户功能"""
        with app.app_context():
            # 创建一个管理员用户
            admin = User(username='admin')
            admin.set_password('adminpass')
            db.session.add(admin)
            db.session.commit()
            
            # 先登录管理员
            response = self.client.post('/admin/login', 
                json={'username': 'admin', 'password': 'adminpass'})
            self.assertEqual(response.status_code, 200)
            
            # 创建一个被锁定的测试用户
            test_user = User(username='lockeduser')
            test_user.set_password('testpass')
            test_user.is_locked = True
            test_user.failed_login_attempts = 10
            db.session.add(test_user)
            db.session.commit()
            
            # 解锁用户
            response = self.client.post(f'/api/admin/users/{test_user.id}/unlock')
            data = json.loads(response.data)
            self.assertEqual(response.status_code, 200)
            self.assertIn('用户已解锁', data['message'])
            
            # 验证用户已解锁
            user = User.query.filter_by(username='lockeduser').first()
            self.assertFalse(user.is_locked)
            self.assertEqual(user.failed_login_attempts, 0)
    
    def test_reset_on_successful_login(self):
        """测试成功登录后重置失败计数"""
        with app.app_context():
            # 先尝试几次失败登录
            for i in range(5):
                self.client.post('/admin/login', 
                    json={'username': 'testuser', 'password': 'wrongpass'})
            
            # 然后成功登录
            response = self.client.post('/admin/login', 
                json={'username': 'testuser', 'password': 'testpass'})
            self.assertEqual(response.status_code, 200)
            
            # 验证失败计数被重置
            user = User.query.filter_by(username='testuser').first()
            self.assertEqual(user.failed_login_attempts, 0)
            
            # 验证IP失败计数也被重置
            ip_block = IPBlock.query.filter_by(ip_address='127.0.0.1').first()
            self.assertEqual(ip_block.failed_attempts, 0)

if __name__ == '__main__':
    unittest.main() 