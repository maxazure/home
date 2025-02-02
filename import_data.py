from app import app, db, Category, Link
import json
import sys
from urllib.parse import urlparse

def validate_url(url):
    """验证URL是否有效"""
    if not url:  # 允许空URL
        return True
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc]) or url.startswith('\\\\')
    except:
        return False

def validate_data(data):
    """验证数据格式是否正确"""
    if not isinstance(data, list):
        raise ValueError("数据必须是列表格式")
    
    for section in data:
        if not isinstance(section, dict):
            raise ValueError("每个section必须是字典格式")
        if 'sectionName' not in section or 'rows' not in section:
            raise ValueError("section必须包含sectionName和rows字段")
        if not isinstance(section['rows'], list):
            raise ValueError("rows必须是列表格式")
        
        for row in section['rows']:
            if not isinstance(row, dict) or 'columns' not in row:
                raise ValueError("每个row必须是包含columns的字典")
            if not isinstance(row['columns'], list):
                raise ValueError("columns必须是列表格式")
            
            for column in row['columns']:
                if not isinstance(column, dict):
                    raise ValueError("每个column必须是字典格式")
                if 'title' not in column or 'links' not in column:
                    raise ValueError("column必须包含title和links字段")
                if not isinstance(column['links'], list):
                    raise ValueError("links必须是列表格式")
                
                for link in column['links']:
                    if not isinstance(link, dict):
                        raise ValueError("每个link必须是字典格式")
                    if 'name' not in link or 'url' not in link:
                        raise ValueError("link必须包含name和url字段")
                    if not validate_url(link['url']):
                        raise ValueError(f"无效的URL: {link['url']}")

def import_data(filename=None):
    """导入数据
    
    Args:
        filename: JSON数据文件路径，如果为None则使用内置数据
    """
    try:
        with app.app_context():
            # 如果提供了文件名，从文件读取数据
            if filename:
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                except Exception as e:
                    print(f"读取文件失败: {e}")
                    return
            else:
                # 使用内置数据
                data = [
                    {
                        "sectionName": "常用网址",
                        "rows": [
                            {
                                "columns": [
                                    {
                                        "title": "必备网站",
                                        "links": [
                                            {"name": "Google", "url": "https://www.google.com"},
                                            {"name": "ChatGPT", "url": "https://chat.openai.com"},
                                            {"name": "Youtube", "url": "https://www.youtube.com"},
                                            {"name": "哔哩哔哩", "url": "https://www.bilibili.com"}
                                        ]
                                    },
                                    {
                                        "title": "编程",
                                        "links": [
                                            {"name": "Stack Overflow", "url": "https://stackoverflow.com"},
                                            {"name": "GitHub", "url": "https://github.com"},
                                            {"name": "uviewui", "url": "https://www.uviewui.com/"},
                                            {"name": "CoreShop", "url": "https://www.coreshop.cn/"}
                                        ]
                                    },
                                    {
                                        "title": "生活与购物",
                                        "links": [
                                            {"name": "新西兰比价网（PriceSpy）", "url": "https://www.pricespy.co.nz/"},
                                            {"name": "Bunnings", "url": "https://www.bunnings.co.nz/"},
                                            {"name": "The Warehouse", "url": "https://www.thewarehouse.co.nz/"},
                                            {"name": "Trade Me", "url": "https://www.trademe.co.nz/"},
                                            {"name": "Kmart NZ", "url": "https://www.kmart.co.nz/"}
                                        ]
                                    }
                                ]
                            },
                            {
                                "columns": [
                                    {
                                        "title": "游戏网站",
                                        "links": [
                                            {"name": "POKI", "url": "https://poki.com/zh"},
                                            {"name": "7k7k小游戏", "url": "http://www.7k7k.com/"}
                                        ]
                                    },
                                    {
                                        "title": "设计",
                                        "links": [
                                            {"name": "CANVA AI作图工具", "url": "https://www.canva.com/"},
                                            {"name": "Figma 原型设计工具", "url": "https://www.figma.com/"}
                                        ]
                                    },
                                    {
                                        "title": "3D打印模型",
                                        "links": [
                                            {"name": "Thingiverse", "url": "https://www.thingiverse.com"},
                                            {"name": "Printables", "url": "https://www.printables.com"},
                                            {"name": "MyMiniFactory", "url": "https://www.myminifactory.com"},
                                            {"name": "Cults", "url": "https://cults3d.com"},
                                            {"name": "Pinshape", "url": "https://www.pinshape.com"},
                                            {"name": "CGTrader", "url": "https://www.cgtrader.com"},
                                            {"name": "GrabCAD", "url": "https://grabcad.com"},
                                            {"name": "TurboSquid", "url": "https://www.turbosquid.com"}
                                        ]
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "sectionName": "学习",
                        "rows": [
                            {
                                "columns": [
                                    {
                                        "title": "工作常用",
                                        "links": [
                                            {"name": "1stdomains", "url": "https://1stdomains.nz/"},
                                            {"name": "Microsoft Teams", "url": "https://www.microsoft.com/en/microsoft-teams/group-chat-software"},
                                            {"name": "Aliyun", "url": "https://account.aliyun.com/"},
                                            {"name": "腾讯云", "url": "https://console.cloud.tencent.com/"}
                                        ]
                                    },
                                    {
                                        "title": "文件共享",
                                        "links": [
                                            {"name": "Google Drive", "url": "https://drive.google.com"},
                                            {"name": "Dropbox", "url": "https://www.dropbox.com"}
                                        ]
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "sectionName": "家庭",
                        "rows": [
                            {
                                "columns": [
                                    {
                                        "title": "私有云",
                                        "links": [
                                            {"name": "Portainer(Docker)", "url": "http://192.168.31.205:9000/"},
                                            {"name": "PVE", "url": "https://192.168.31.221:8006/"},
                                            {"name": "Baota", "url": "https://192.168.31.205:12006/jayliu"},
                                            {"name": "Teamcity", "url": "https://teamcity.jayliu.co.nz/"},
                                            {"name": "Home Assistant", "url": "http://192.168.31.198:8123/"},
                                            {"name": "家庭相册", "url": "http://192.168.31.143:9989/"}
                                        ]
                                    },
                                    {
                                        "title": "共享文件夹",
                                        "links": [
                                            {"name": "\\\\192.168.31.205\\data", "url": ""},
                                            {"name": "Apple Music", "url": "https://www.apple.com/apple-music/"},
                                            {"name": "修改Home网址导航", "url": "http://192.168.31.205:8081/?folder=/www/wwwroot/home.jayliu.co.nz"}
                                        ]
                                    },
                                    {
                                        "title": "PROJECTS",
                                        "links": [
                                            {"name": "KTATTOO", "url": "https://www.ktattoo.co.nz"},
                                            {"name": "云想门店", "url": "https://admin.storeyx.com/"}
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            
            # 验证数据格式
            try:
                validate_data(data)
            except ValueError as e:
                print(f"数据验证失败: {e}")
                return
            
            # 备份现有数据（如果需要的话）
            try:
                existing_categories = Category.query.all()
                existing_links = Link.query.all()
                backup_data = {
                    'categories': [
                        {'id': c.id, 'title': c.title, 'section_name': c.section_name}
                        for c in existing_categories
                    ],
                    'links': [
                        {'id': l.id, 'name': l.name, 'url': l.url, 'category_id': l.category_id}
                        for l in existing_links
                    ]
                }
                with open('data_backup.json', 'w', encoding='utf-8') as f:
                    json.dump(backup_data, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"备份数据失败: {e}")
                return
            
            # 清空现有数据
            try:
                Link.query.delete()
                Category.query.delete()
                db.session.commit()
            except Exception as e:
                print(f"清空数据失败: {e}")
                db.session.rollback()
                return
            
            # 导入新数据
            try:
                for section in data:
                    section_name = section['sectionName']
                    for row in section['rows']:
                        for column in row['columns']:
                            # 创建分类
                            category = Category(
                                title=column['title'],
                                section_name=section_name
                            )
                            db.session.add(category)
                            db.session.commit()
                            
                            # 创建链接
                            for link_data in column['links']:
                                link = Link(
                                    name=link_data['name'],
                                    url=link_data['url'],
                                    category_id=category.id
                                )
                                db.session.add(link)
                            db.session.commit()
                
                print("数据导入完成！")
                
            except Exception as e:
                print(f"导入数据失败: {e}")
                db.session.rollback()
                # 尝试恢复备份
                try:
                    for category in backup_data['categories']:
                        c = Category(
                            id=category['id'],
                            title=category['title'],
                            section_name=category['section_name']
                        )
                        db.session.add(c)
                    db.session.commit()
                    
                    for link in backup_data['links']:
                        l = Link(
                            id=link['id'],
                            name=link['name'],
                            url=link['url'],
                            category_id=link['category_id']
                        )
                        db.session.add(l)
                    db.session.commit()
                    print("已恢复到原有数据")
                except Exception as e:
                    print(f"恢复数据失败: {e}")
                    print("请手动恢复 data_backup.json 中的数据")
                
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == '__main__':
    # 如果提供了文件名参数，则从文件导入数据
    filename = sys.argv[1] if len(sys.argv) > 1 else None
    import_data(filename) 