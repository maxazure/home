from flask import Blueprint, request, jsonify, send_file
import json
import io
from flask_login import login_required
from models import Page, Region, Category, Link, db
from schemas import pages_schema, regions_schema, categories_schema, links_schema

backup_bp = Blueprint('admin_backup', __name__)

@backup_bp.route('/backup/export', methods=['GET'])
@login_required
def export_data():
    try:
        pages = Page.query.order_by(Page.id).all()
        export_data_dict = {
            'pages': pages_schema.dump(pages),
            'regions': regions_schema.dump(Region.query.all()),
            'categories': categories_schema.dump(Category.query.all()),
            'links': links_schema.dump(Link.query.all())
        }
        
        json_data = json.dumps(export_data_dict, ensure_ascii=False, indent=2)
        buffer = io.BytesIO(json_data.encode('utf-8'))
        buffer.seek(0)
        response = send_file(
            buffer,
            mimetype='application/json',
            as_attachment=True,
            download_name='backup.json'
        )
        response.call_on_close(buffer.close)
        return response
    except Exception as e:
        return jsonify({'message': f'导出失败: {str(e)}'}), 500

@backup_bp.route('/backup/import', methods=['POST'])
@login_required
def import_data():
    try:
        if 'file' not in request.files:
            return jsonify({'message': '没有上传文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'message': '未选择文件'}), 400
        
        if not file.filename.endswith('.json'):
            return jsonify({'message': '只支持.json格式文件'}), 400
        
        try:
            try:
                content = file.read().decode('utf-8')
            except UnicodeDecodeError:
                file.seek(0)
                content = file.read().decode('gbk')
                
            import_data = json.loads(content)
            
            required_keys = ['pages', 'regions', 'categories', 'links']
            if not all(key in import_data for key in required_keys):
                return jsonify({'message': '无效的数据格式，缺少必要的数据字段'}), 400
            
            page_map = {}
            
            for page_data in import_data.get('pages', []):
                if 'name' not in page_data or 'slug' not in page_data:
                    continue
                existing_page = Page.query.filter_by(slug=page_data['slug']).first()
                if existing_page:
                    page_map[page_data['slug']] = existing_page.id
                    continue
                page = Page(name=page_data['name'])
                page.slug = page_data['slug']
                db.session.add(page)
                db.session.flush()
                page_map[page_data['slug']] = page.id
            
            region_map = {}
            for region_data in import_data.get('regions', []):
                if 'name' not in region_data or 'page_slug' not in region_data:
                    continue
                    
                page_id = page_map.get(region_data['page_slug'])
                if not page_id:
                    continue
                
                existing_region = Region.query.filter_by(
                    name=region_data['name'],
                    page_id=page_id
                ).first()
                
                if existing_region:
                    region_map[region_data['name']] = existing_region.id
                    continue
                    
                region = Region(
                    name=region_data['name'],
                    page_id=page_id
                )
                db.session.add(region)
                db.session.flush()
                region_map[region_data['name']] = region.id
            
            category_map = {}
            for category_data in import_data.get('categories', []):
                if not all(k in category_data for k in ['title', 'section_name', 'region_name']):
                    continue
                    
                region_id = region_map.get(category_data['region_name'])
                if not region_id:
                    continue
                    
                existing_category = Category.query.filter_by(
                    title=category_data['title'],
                    region_id=region_id
                ).first()
                
                if existing_category:
                    category_map[category_data['title']] = existing_category.id
                    continue
                    
                category = Category(
                    title=category_data['title'],
                    section_name=category_data['section_name'],
                    section_order=category_data.get('section_order', 0),
                    category_order=category_data.get('category_order', 0),
                    region_id=region_id
                )
                db.session.add(category)
                db.session.flush()
                category_map[category_data['title']] = category.id
            
            for link_data in import_data.get('links', []):
                if not all(k in link_data for k in ['name', 'url', 'category_title']):
                    continue
                    
                category_id = category_map.get(link_data['category_title'])
                if not category_id:
                    continue
                    
                existing_link = Link.query.filter_by(
                    name=link_data['name'],
                    category_id=category_id
                ).first()
                
                if existing_link:
                    continue
                    
                link = Link(
                    name=link_data['name'],
                    url=link_data['url'],
                    category_id=category_id
                )
                db.session.add(link)
            
            db.session.commit()
            return jsonify({'message': '数据导入成功'}), 200
            
        except json.JSONDecodeError:
            return jsonify({'message': '无效的JSON文件格式'}), 400
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'导入失败: {str(e)}'}), 500
