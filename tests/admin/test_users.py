import unittest
from app import app, db
from models import User

class TestUserManagement(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        with app.app_context():
            db.create_all()
            self.create_test_user()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def create_test_user(self):
        with app.app_context():
            user = User(username='testuser')
            user.set_password('testpassword')
            db.session.add(user)
            db.session.commit()

    def login(self):
        self.app.post('/api/admin/login', json={
            'username': 'testuser',
            'password': 'testpassword'
        })

    def test_add_user(self):
        self.login()
        response = self.app.post('/api/admin/users', json={
            'username': 'newuser',
            'password': 'newpassword'
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['username'], 'newuser')

    def test_update_user(self):
        self.login()
        with app.app_context():
            user = User(username='olduser')
            user.set_password('oldpassword')
            db.session.add(user)
            db.session.commit()
            user_id = user.id

        response = self.app.put(f'/api/admin/users/{user_id}', json={
            'username': 'updateduser',
            'password': 'updatedpassword'
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['username'], 'updateduser')

    def test_delete_user(self):
        self.login()
        with app.app_context():
            user = User(username='user_to_delete')
            user.set_password('password')
            db.session.add(user)
            db.session.commit()
            user_id = user.id

        response = self.app.delete(f'/api/admin/users/{user_id}')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['message'], 'User deleted successfully')

    def test_unlock_user(self):
        self.login()
        with app.app_context():
            user = User(username='lockeduser', is_locked=True)
            user.set_password('password')
            db.session.add(user)
            db.session.commit()
            user_id = user.id

        response = self.app.post(f'/api/admin/users/{user_id}/unlock')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['message'], '用户已解锁')

if __name__ == '__main__':
    unittest.main()
