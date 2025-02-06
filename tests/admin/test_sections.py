import unittest
from app import app, db
from models import Category, User

class TestSectionManagement(unittest.TestCase):
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

    def test_add_section(self):
        self.login()
        response = self.app.post('/api/admin/sections', json={
            'section_name': 'Test Section'
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['message'], '区域添加成功')
        self.assertEqual(data['section_name'], 'Test Section')

    def test_update_section(self):
        self.login()
        with app.app_context():
            category = Category(title='Old Category', section_name='Old Section')
            db.session.add(category)
            db.session.commit()

        response = self.app.post('/api/admin/sections/update', json={
            'old_section_name': 'Old Section',
            'section_name': 'Updated Section'
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['message'], '区域更新成功')
        self.assertEqual(data['section_name'], 'Updated Section')

    def test_delete_section(self):
        self.login()
        with app.app_context():
            category = Category(title='Category to Delete', section_name='Section to Delete')
            db.session.add(category)
            db.session.commit()

        response = self.app.post('/api/admin/sections/delete', json={
            'section_name': 'Section to Delete'
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['message'], '区域删除成功')

    def test_reorder_section(self):
        self.login()
        with app.app_context():
            category1 = Category(title='Category 1', section_name='Section 1', section_order=1)
            category2 = Category(title='Category 2', section_name='Section 2', section_order=2)
            db.session.add_all([category1, category2])
            db.session.commit()

        response = self.app.post('/api/admin/sections/reorder', json={
            'section_name': 'Section 1',
            'direction': 'down'
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['message'], '区域排序更新成功')

        with app.app_context():
            updated_category1 = db.session.get(Category, category1.id)
            updated_category2 = db.session.get(Category, category2.id)
            self.assertEqual(updated_category1.section_order, 2)
            self.assertEqual(updated_category2.section_order, 1)

if __name__ == '__main__':
    unittest.main()
