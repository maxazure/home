import unittest
from flask import Flask
from models import db, Page, Region, User, IPBlock, Category, Link

class BaseModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(self.app)
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

class PageModelTestCase(BaseModelTestCase):
    def test_page_creation(self):
        with self.app.app_context():
            # 创建一个 Page 实例
            page = Page(name="Homepage")
            db.session.add(page)
            db.session.commit()
            self.assertIsNotNone(page.id)
            queried_page = db.session.get(Page, page.id)
            self.assertEqual(queried_page.name, "Homepage")
            self.assertEqual(queried_page.slug, "homepage")

    def test_page_slug_generation(self):
        with self.app.app_context():
            # 测试基本 slug 生成
            page1 = Page(name="Hello World")
            self.assertEqual(page1.slug, "hello-world")

            # 测试特殊字符处理
            page2 = Page(name="Hello! World@#$%")
            self.assertEqual(page2.slug, "hello-world")

            # 测试中文字符处理
            page3 = Page(name="你好 世界")
            self.assertEqual(page3.slug, "")  # 纯中文会变成空字符串

            # 测试多个空格处理
            page4 = Page(name="Hello    World")
            self.assertEqual(page4.slug, "hello-world")

    def test_page_slug_uniqueness(self):
        with self.app.app_context():
            page1 = Page(name="Test Page")
            db.session.add(page1)
            db.session.commit()

            # 尝试创建具有相同 slug 的页面应该失败
            page2 = Page(name="Test Page")
            db.session.add(page2)
            with self.assertRaises(Exception):  # 应该抛出唯一性约束异常
                db.session.commit()

    def test_page_regions_relationship(self):
        with self.app.app_context():
            # 创建 Page 实例
            page = Page(name="About")
            db.session.add(page)
            db.session.commit()
            
            # 创建多个关联的 Region 实例
            region1 = Region(name="Header", page=page)
            region2 = Region(name="Footer", page=page)
            db.session.add_all([region1, region2])
            db.session.commit()
            
            # 查询页面及其关联的 Region
            queried_page = db.session.get(Page, page.id)
            self.assertEqual(len(queried_page.regions), 2)
            region_names = {region.name for region in queried_page.regions}
            self.assertSetEqual(region_names, {"Header", "Footer"})

    def test_page_update(self):
        with self.app.app_context():
            # 创建并保存 Page
            page = Page(name="Old Name")
            db.session.add(page)
            db.session.commit()
            
            # 更新页面名称
            page.name = "New Name"
            db.session.commit()
            
            queried_page = db.session.get(Page, page.id)
            self.assertEqual(queried_page.name, "New Name")

    def test_page_delete(self):
        with self.app.app_context():
            # 创建并保存 Page
            page = Page(name="To Be Deleted")
            db.session.add(page)
            db.session.commit()
            
            # 删除页面记录
            db.session.delete(page)
            db.session.commit()
            
            queried_page = db.session.get(Page, page.id)
            self.assertIsNone(queried_page)

    def test_cascade_delete_regions(self):
        with self.app.app_context():
            # 创建页面和关联的区域
            page = Page(name="Test Page")
            region1 = Region(name="Region 1", page=page)
            region2 = Region(name="Region 2", page=page)
            db.session.add(page)
            db.session.add_all([region1, region2])
            db.session.commit()

            # 删除页面
            db.session.delete(page)
            db.session.commit()

            # 验证区域是否也被删除
            regions = Region.query.filter_by(page_id=page.id).all()
            self.assertEqual(len(regions), 0)

class RegionModelTestCase(BaseModelTestCase):
    def test_region_creation(self):
        with self.app.app_context():
            page = Page(name="Test Page")
            db.session.add(page)
            db.session.commit()

            region = Region(name="Sidebar", page=page)
            db.session.add(region)
            db.session.commit()

            self.assertIsNotNone(region.id)
            queried_region = db.session.get(Region, region.id)
            self.assertEqual(queried_region.name, "Sidebar")
            self.assertEqual(queried_region.page_id, page.id)

    def test_region_update(self):
        with self.app.app_context():
            page = Page(name="Test Page")
            db.session.add(page)
            db.session.commit()

            region = Region(name="Old Region", page=page)
            db.session.add(region)
            db.session.commit()

            region.name = "New Region"
            db.session.commit()

            queried_region = db.session.get(Region, region.id)
            self.assertEqual(queried_region.name, "New Region")

    def test_region_delete(self):
        with self.app.app_context():
            page = Page(name="Test Page")
            db.session.add(page)
            db.session.commit()

            region = Region(name="To Delete", page=page)
            db.session.add(region)
            db.session.commit()

            db.session.delete(region)
            db.session.commit()

            queried_region = db.session.get(Region, region.id)
            self.assertIsNone(queried_region)

    def test_region_page_relationship(self):
        with self.app.app_context():
            page = Page(name="Test Page")
            db.session.add(page)
            db.session.commit()

            region = Region(name="Test Region", page=page)
            db.session.add(region)
            db.session.commit()

            queried_region = db.session.get(Region, region.id)
            self.assertEqual(queried_region.page.name, "Test Page")

    def test_cascade_delete_categories(self):
        with self.app.app_context():
            # 创建区域和关联的分类
            region = Region(name="Test Region")
            category1 = Category(title="Category 1", section_name="Section 1", region=region)
            category2 = Category(title="Category 2", section_name="Section 1", region=region)
            db.session.add(region)
            db.session.add_all([category1, category2])
            db.session.commit()

            # 删除区域
            db.session.delete(region)
            db.session.commit()

            # 验证分类是否也被删除
            categories = Category.query.filter_by(region_id=region.id).all()
            self.assertEqual(len(categories), 0)

class UserModelTestCase(BaseModelTestCase):
    def test_user_creation(self):
        with self.app.app_context():
            user = User(username="testuser")
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()

            queried_user = db.session.get(User, user.id)
            self.assertEqual(queried_user.username, "testuser")
            self.assertTrue(queried_user.check_password("password123"))
            self.assertFalse(queried_user.check_password("wrongpass"))

    def test_user_login_attempts(self):
        with self.app.app_context():
            user = User(username="testuser")
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()

            user.increment_failed_attempts()
            self.assertEqual(user.failed_login_attempts, 1)
            self.assertIsNotNone(user.last_failed_login)

            user.reset_failed_attempts()
            self.assertEqual(user.failed_login_attempts, 0)
            self.assertIsNone(user.last_failed_login)

class IPBlockModelTestCase(BaseModelTestCase):
    def test_ip_block_creation(self):
        with self.app.app_context():
            ip_block = IPBlock(ip_address="192.168.1.1")
            db.session.add(ip_block)
            db.session.commit()

            queried_block = db.session.get(IPBlock, ip_block.id)
            self.assertEqual(queried_block.ip_address, "192.168.1.1")
            self.assertEqual(queried_block.failed_attempts, 0)
            self.assertFalse(queried_block.is_blocked)

class CategoryModelTestCase(BaseModelTestCase):
    def test_category_creation(self):
        with self.app.app_context():
            region = Region(name="Main")
            db.session.add(region)
            db.session.commit()

            category = Category(
                title="Programming",
                section_name="Development",
                section_order=1,
                category_order=1,
                region=region
            )
            db.session.add(category)
            db.session.commit()

            queried_category = db.session.get(Category, category.id)
            self.assertEqual(queried_category.title, "Programming")
            self.assertEqual(queried_category.region.name, "Main")

    def test_category_links_relationship(self):
        with self.app.app_context():
            category = Category(title="Programming", section_name="Development")
            link1 = Link(name="Python", url="https://python.org", category=category)
            link2 = Link(name="Flask", url="https://flask.palletsprojects.com", category=category)
            
            db.session.add(category)
            db.session.add_all([link1, link2])
            db.session.commit()

            queried_category = db.session.get(Category, category.id)
            self.assertEqual(len(queried_category.links), 2)
            link_names = {link.name for link in queried_category.links}
            self.assertSetEqual(link_names, {"Python", "Flask"})

    def test_cascade_delete_links(self):
        with self.app.app_context():
            # 创建分类和关联的链接
            category = Category(title="Test Category", section_name="Test Section")
            link1 = Link(name="Link 1", url="http://example1.com", category=category)
            link2 = Link(name="Link 2", url="http://example2.com", category=category)
            db.session.add(category)
            db.session.add_all([link1, link2])
            db.session.commit()

            # 删除分类
            db.session.delete(category)
            db.session.commit()

            # 验证链接是否也被删除
            links = Link.query.filter_by(category_id=category.id).all()
            self.assertEqual(len(links), 0)

    def test_deep_cascade_delete(self):
        with self.app.app_context():
            # 创建完整的层级结构，更改创建和关联的顺序
            page = Page(name="Test Page")
            db.session.add(page)
            db.session.commit()

            region = Region(name="Test Region")
            page.regions.append(region)  # 使用关系来添加
            db.session.commit()

            category = Category(title="Test Category", section_name="Test Section")
            region.categories.append(category)  # 使用关系来添加
            db.session.commit()

            link1 = Link(name="Link 1", url="http://example1.com")
            link2 = Link(name="Link 2", url="http://example2.com")
            category.links.extend([link1, link2])  # 使用关系来添加
            db.session.commit()

            # 保存所有ID以供后续验证
            region_id = region.id
            category_id = category.id
            link1_id = link1.id
            link2_id = link2.id

            # 删除顶层页面
            db.session.delete(page)
            db.session.commit()

            # 验证所有关联数据是否都被删除
            self.assertIsNone(db.session.get(Region, region_id))
            self.assertIsNone(db.session.get(Category, category_id))
            self.assertIsNone(db.session.get(Link, link1_id))
            self.assertIsNone(db.session.get(Link, link2_id))

class LinkModelTestCase(BaseModelTestCase):
    def test_link_creation(self):
        with self.app.app_context():
            category = Category(title="Programming", section_name="Development")
            db.session.add(category)
            db.session.commit()

            link = Link(
                name="GitHub",
                url="https://github.com",
                category=category
            )
            db.session.add(link)
            db.session.commit()

            queried_link = db.session.get(Link, link.id)
            self.assertEqual(queried_link.name, "GitHub")
            self.assertEqual(queried_link.category.title, "Programming")

    def test_link_update(self):
        with self.app.app_context():
            category = Category(title="Programming", section_name="Development")
            db.session.add(category)
            db.session.commit()

            link = Link(name="Old Name", url="https://old.com", category=category)
            db.session.add(link)
            db.session.commit()

            link.name = "New Name"
            link.url = "https://new.com"
            db.session.commit()

            queried_link = db.session.get(Link, link.id)
            self.assertEqual(queried_link.name, "New Name")
            self.assertEqual(queried_link.url, "https://new.com")

if __name__ == '__main__':
    unittest.main()