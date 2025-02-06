import unittest
from app import app, db
from models import Page, User

class TestPageManagement(unittest.TestCase):
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

    def test_add_page(self):
        self.login()
        response = self.app.post('/api/admin/pages', json={
            'name': 'Test Page'
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['name'], 'Test Page')

    def test_update_page(self):
        self.login()
        with app.app_context():
            page = Page(name='Old Page')
            db.session.add(page)
            db.session.commit()
            page_id = page.id

        response = self.app.put(f'/api/admin/pages/{page_id}', json={
            'name': 'Updated Page'
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['name'], 'Updated Page')

    def test_delete_page(self):
        self.login()
        with app.app_context():
            page = Page(name='Page to Delete')
            db.session.add(page)
            db.session.commit()
            page_id = page.id

        response = self.app.delete(f'/api/admin/pages/{page_id}')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['message'], 'Page deleted successfully')

if __name__ == '__main__':
    unittest.main()
