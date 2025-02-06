import unittest
from app import app, db
from models import Link, Category, User

class TestLinkManagement(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        with app.app_context():
            db.create_all()
            self.create_test_user()
            self.create_test_category()

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

    def create_test_category(self):
        with app.app_context():
            category = Category(title='Test Category', section_name='Test Section')
            db.session.add(category)
            db.session.commit()

    def login(self):
        self.app.post('/api/admin/login', json={
            'username': 'testuser',
            'password': 'testpassword'
        })

    def test_add_link(self):
        self.login()
        with app.app_context():
            category = Category.query.first()
            response = self.app.post('/api/admin/links', json={
                'name': 'Test Link',
                'url': 'http://test.com',
                'category_id': category.id
            })
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertEqual(data['name'], 'Test Link')
            self.assertEqual(data['url'], 'http://test.com')
            self.assertEqual(data['category_id'], category.id)

    def test_update_link(self):
        self.login()
        with app.app_context():
            category = Category.query.first()
            link = Link(name='Old Link', url='http://old.com', category_id=category.id)
            db.session.add(link)
            db.session.commit()
            link_id = link.id

        response = self.app.put(f'/api/admin/links/{link_id}', json={
            'name': 'Updated Link',
            'url': 'http://updated.com',
            'category_id': category.id
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['name'], 'Updated Link')
        self.assertEqual(data['url'], 'http://updated.com')
        self.assertEqual(data['category_id'], category.id)

    def test_delete_link(self):
        self.login()
        with app.app_context():
            category = Category.query.first()
            link = Link(name='Link to Delete', url='http://delete.com', category_id=category.id)
            db.session.add(link)
            db.session.commit()
            link_id = link.id

        response = self.app.delete(f'/api/admin/links/{link_id}')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['message'], 'Link deleted successfully')

if __name__ == '__main__':
    unittest.main()
