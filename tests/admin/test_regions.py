import unittest
from app import app, db
from models import Region, User

class TestRegionManagement(unittest.TestCase):
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

    def test_add_region(self):
        self.login()
        response = self.app.post('/api/admin/regions', json={
            'name': 'Test Region',
            'page_id': 1
        })
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data['name'], 'Test Region')
        self.assertEqual(data['page_id'], 1)

    def test_update_region(self):
        self.login()
        with app.app_context():
            region = Region(name='Old Region', page_id=1)
            db.session.add(region)
            db.session.commit()
            region_id = region.id

        response = self.app.put(f'/api/admin/regions/{region_id}', json={
            'name': 'Updated Region',
            'page_id': 1
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['name'], 'Updated Region')
        self.assertEqual(data['page_id'], 1)

    def test_delete_region(self):
        self.login()
        with app.app_context():
            region = Region(name='Region to Delete', page_id=1)
            db.session.add(region)
            db.session.commit()
            region_id = region.id

        response = self.app.delete(f'/api/admin/regions/{region_id}')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['message'], 'Region deleted')

if __name__ == '__main__':
    unittest.main()
