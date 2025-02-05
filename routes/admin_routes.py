from flask import Blueprint, request, jsonify, redirect, current_app, send_file
import json
import tempfile
from flask_login import login_required, current_user
from models import Category, Link, User, IPBlock, db
from schemas import (
    category_schema, 
    link_schema, 
    user_schema, 
    users_schema, 
    links_schema,
    categories_schema  # 添加这个导入
)

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
@login_required
def admin_dashboard():
    return current_app.send_static_file('admin/index.html')

@admin_bp.route('/api/admin/categories', methods=['POST'])
@login_required
def admin_add_category():
    title = request.json['title']
    section_name = request.json['section_name']
    
    max_order = db.session.query(db.func.max(Category.category_order)).filter(
        Category.section_name == section_name
    ).scalar() or 0
    
    new_category = Category(
        title=title,
        section_name=section_name,
        category_order=max_order + 1
    )
    db.session.add(new_category)
    db.session.commit()
    
    return jsonify(category_schema.dump(new_category))

@admin_bp.route('/api/admin/categories/<id>', methods=['PUT'])
@login_required
def admin_update_category(id):
    category = db.session.get(Category, id)
    if not category:
        return jsonify({'message': '分类不存在'}), 404
    
    category.title = request.json.get('title', category.title)
    category.section_name = request.json.get('section_name', category.section_name)
    
    db.session.commit()
    return jsonify(category_schema.dump(category))

@admin_bp.route('/api/admin/categories/<id>', methods=['DELETE'])
@login_required
def admin_delete_category(id):
    try:
        category = db.session.get(Category, id)
        if not category:
            return jsonify({'message': '分类不存在'}), 404
        Link.query.filter_by(category_id=id).delete()
        db.session.delete(category)
        db.session.commit()
        return jsonify({'message': 'Category deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'删除失败: {str(e)}'}), 500

@admin_bp.route('/api/admin/links', methods=['POST'])
@login_required
def admin_add_link():
    name = request.json['name']
    url = request.json['url']
    category_id = request.json['category_id']
    
    new_link = Link(name=name, url=url, category_id=category_id)
    db.session.add(new_link)
    db.session.commit()
    
    return jsonify(link_schema.dump(new_link))

@admin_bp.route('/api/admin/links/<id>', methods=['PUT'])
@login_required
def admin_update_link(id):
    link = db.session.get(Link, id)
    if not link:
        return jsonify({'message': '链接不存在'}), 404
    
    link.name = request.json.get('name', link.name)
    link.url = request.json.get('url', link.url)
    link.category_id = request.json.get('category_id', link.category_id)
    
    db.session.commit()
    return jsonify(link_schema.dump(link))

@admin_bp.route('/api/admin/links/<id>', methods=['DELETE'])
@login_required
def admin_delete_link(id):
    link = db.session.get(Link, id)
    if not link:
        return jsonify({'message': '链接不存在'}), 404
    db.session.delete(link)
    db.session.commit()
    return jsonify({'message': 'Link deleted successfully'})

@admin_bp.route('/api/admin/users', methods=['GET'])
@login_required
def admin_get_users():
    users = User.query.all()
    return jsonify(users_schema.dump(users))

@admin_bp.route('/api/admin/users', methods=['POST'])
@login_required
def admin_add_user():
    username = request.json['username']
    password = request.json['password']
    
    if User.query.filter_by(username=username).first():
        return jsonify({'message': '用户名已存在'}), 400
    
    new_user = User(username=username)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify(user_schema.dump(new_user))

@admin_bp.route('/api/admin/users/<id>', methods=['PUT'])
@login_required
def admin_update_user(id):
    user = db.session.get(User, id)
    if not user:
        return jsonify({'message': '用户不存在'}), 404
    
    username = request.json.get('username')
    password = request.json.get('password')
    
    if username and username != user.username:
        if User.query.filter_by(username=username).first():
            return jsonify({'message': '用户名已存在'}), 400
        user.username = username
    
    if password:
        user.set_password(password)
    
    db.session.commit()
    return jsonify(user_schema.dump(user))

@admin_bp.route('/api/admin/users/<id>', methods=['DELETE'])
@login_required
def admin_delete_user(id):
    user = db.session.get(User, id)
    if not user:
        return jsonify({'message': '用户不存在'}), 404
    
    if User.query.count() == 1:
        return jsonify({'message': '不能删除最后一个管理员账户'}), 400
    
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'})

@admin_bp.route('/api/admin/users/<id>/unlock', methods=['POST'])
@login_required
def admin_unlock_user(id):
    user = db.session.get(User, id)
    if not user:
        return jsonify({'message': '用户不存在'}), 404
    user.is_locked = False
    user.failed_login_attempts = 0
    user.last_failed_login = None
    db.session.commit()
    return jsonify({'message': '用户已解锁'})

@admin_bp.route('/api/admin/ip-blocks', methods=['GET'])
@login_required
def admin_get_ip_blocks():
    ip_blocks = IPBlock.query.all()
    return jsonify([{
        'id': block.id,
        'ip_address': block.ip_address,
        'failed_attempts': block.failed_attempts,
        'is_blocked': block.is_blocked,
        'last_attempt': block.last_attempt,
        'created_at': block.created_at
    } for block in ip_blocks])

@admin_bp.route('/api/admin/ip-blocks/<id>/unblock', methods=['POST'])
@login_required
def admin_unblock_ip(id):
    ip_block = db.session.get(IPBlock, id)
    if not ip_block:
        return jsonify({'message': 'IP记录不存在'}), 404
    ip_block.is_blocked = False
    ip_block.failed_attempts = 0
    ip_block.last_attempt = None
    db.session.commit()
    return jsonify({'message': 'IP已解封'})

@admin_bp.route('/api/admin/sections', methods=['POST'])
@login_required
def admin_add_section():
    data = request.get_json()
    section_name = data.get('section_name')
    
    if not section_name:
        return jsonify({'message': '区域名称不能为空'}), 400
        
    if Category.query.filter_by(section_name=section_name).first():
        return jsonify({'message': '区域名称已存在'}), 400
        
    max_order = db.session.query(db.func.max(Category.section_order)).scalar() or 0
    
    new_category = Category(
        title=f"{section_name} 默认分类",
        section_name=section_name,
        section_order=max_order + 1
    )
    
    try:
        db.session.add(new_category)
        db.session.commit()
        return jsonify({'message': '区域添加成功', 'section_name': section_name}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'添加区域失败: {str(e)}'}), 500

@admin_bp.route('/api/admin/sections/update', methods=['POST'])
@login_required
def admin_update_section():
    data = request.get_json()
    old_section_name = data.get('old_section_name')
    new_section_name = data.get('section_name')
    
    if not new_section_name:
        return jsonify({'message': '区域名称不能为空'}), 400
        
    if not old_section_name:
        return jsonify({'message': '原区域名称不能为空'}), 400
        
    if Category.query.filter(
        Category.section_name == new_section_name,
        Category.section_name != old_section_name
    ).first():
        return jsonify({'message': '区域名称已存在'}), 400
        
    try:
        categories = Category.query.filter_by(section_name=old_section_name).all()
        for category in categories:
            category.section_name = new_section_name
        
        db.session.commit()
        return jsonify({'message': '区域更新成功', 'section_name': new_section_name}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'更新区域失败: {str(e)}'}), 500

@admin_bp.route('/api/admin/sections/reorder', methods=['POST'])
@login_required
def admin_reorder_sections():
    data = request.get_json()
    section_name = data.get('section_name')
    direction = data.get('direction')
    
    if not section_name or not direction:
        return jsonify({'message': '参数不完整'}), 400
        
    try:
        current_categories = Category.query.filter_by(section_name=section_name).all()
        if not current_categories:
            return jsonify({'message': '区域不存在'}), 404
            
        current_order = current_categories[0].section_order
        
        if direction == 'up':
            prev_category = Category.query.filter(
                Category.section_order < current_order
            ).order_by(Category.section_order.desc()).first()
            
            if prev_category:
                prev_order = prev_category.section_order
                prev_section_name = prev_category.section_name
                
                Category.query.filter_by(section_name=prev_section_name).update(
                    {"section_order": current_order}
                )
                Category.query.filter_by(section_name=section_name).update(
                    {"section_order": prev_order}
                )
                
        elif direction == 'down':
            next_category = Category.query.filter(
                Category.section_order > current_order
            ).order_by(Category.section_order).first()
            
            if next_category:
                next_order = next_category.section_order
                next_section_name = next_category.section_name
                
                Category.query.filter_by(section_name=next_section_name).update(
                    {"section_order": current_order}
                )
                Category.query.filter_by(section_name=section_name).update(
                    {"section_order": next_order}
                )
        
        db.session.commit()
        return jsonify({'message': '区域排序更新成功'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'更新区域排序失败: {str(e)}'}), 500

@admin_bp.route('/api/admin/categories/reorder', methods=['POST'])
@login_required
def admin_reorder_category():
    source_id = request.json.get('source_id')
    target_id = request.json.get('target_id')
    
    if not source_id or not target_id:
        return jsonify({'message': '参数不完整'}), 400
    
    source = Category.query.get(source_id)
    target = Category.query.get(target_id)
    
    if not source or not target:
        return jsonify({'message': '分类不存在'}), 404
    
    if source.section_name != target.section_name:
        return jsonify({'message': '只能在同一区域内排序'}), 400
    
    source_order = source.category_order
    target_order = target.category_order
    
    if source_order < target_order:
        Category.query.filter(
            Category.section_name == source.section_name,
            Category.category_order > source_order,
            Category.category_order <= target_order
        ).update({
            Category.category_order: Category.category_order - 1
        })
        source.category_order = target_order
    else:
        Category.query.filter(
            Category.section_name == source.section_name,
            Category.category_order < source_order,
            Category.category_order >= target_order
        ).update({
            Category.category_order: Category.category_order + 1
        })
        source.category_order = target_order
    
    db.session.commit()
    return jsonify({'message': '排序更新成功'})

@admin_bp.route('/api/admin/categories/move', methods=['POST'])
@login_required
def admin_move_category():
    category_id = request.json.get('category_id')
    direction = request.json.get('direction')
    
    if not category_id or not direction:
        return jsonify({'message': '参数不完整'}), 400
    
    category = Category.query.get(category_id)
    if not category:
        return jsonify({'message': '分类不存在'}), 404
    
    if direction == 'up':
        prev_category = Category.query.filter(
            Category.section_name == category.section_name,
            Category.category_order < category.category_order
        ).order_by(Category.category_order.desc()).first()
        
        if prev_category:
            prev_order = prev_category.category_order
            prev_category.category_order = category.category_order
            category.category_order = prev_order
            db.session.commit()
    
    elif direction == 'down':
        next_category = Category.query.filter(
            Category.section_name == category.section_name,
            Category.category_order > category.category_order
        ).order_by(Category.category_order).first()
        
        if next_category:
            next_order = next_category.category_order
            next_category.category_order = category.category_order
            category.category_order = next_order
            db.session.commit()
    
    return jsonify({'message': '移动成功'})

@admin_bp.route('/api/admin/sections/delete', methods=['POST'])
@login_required
def admin_delete_section():
    data = request.get_json()
    section_name = data.get('section_name')
    
    if not section_name:
        return jsonify({'message': '区域名称不能为空'}), 400
        
    try:
        categories = Category.query.filter_by(section_name=section_name).all()
        if not categories:
            return jsonify({'message': '区域不存在'}), 404
            
        for category in categories:
            Link.query.filter_by(category_id=category.id).delete()
            
        Category.query.filter_by(section_name=section_name).delete()
        
        db.session.commit()
        return jsonify({'message': '区域删除成功'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'删除区域失败: {str(e)}'}), 500

@admin_bp.route('/api/admin/export', methods=['GET'])
@login_required
def export_data():
    try:
        # 获取所有分类和链接数据
        categories = Category.query.order_by(Category.section_order, Category.category_order).all()
        export_data = categories_schema.dump(categories)
        
        # 创建临时文件
        temp = tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.json')
        json.dump(export_data, temp, ensure_ascii=False, indent=2)
        temp.close()
        
        # 发送文件
        return send_file(
            temp.name,
            mimetype='application/json',
            as_attachment=True,
            download_name='backup.json'
        )
    except Exception as e:
        return jsonify({'message': f'导出失败: {str(e)}'}), 500

@admin_bp.route('/api/admin/import', methods=['POST'])
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
            
        # 读取并解析JSON数据
        import_data = json.loads(file.read().decode('utf-8'))
        
        # 开始导入数据
        for category_data in import_data:
            # 检查分类是否已存在
            existing_category = Category.query.filter_by(
                section_name=category_data['section_name'],
                title=category_data['title']
            ).first()
            
            if existing_category:
                category = existing_category
            else:
                # 创建新分类
                category = Category(
                    title=category_data['title'],
                    section_name=category_data['section_name']
                )
                db.session.add(category)
                db.session.flush()  # 获取新分类的ID
            
            # 导入链接
            if 'links' in category_data:
                for link_data in category_data['links']:
                    # 检查链接是否已存在
                    existing_link = Link.query.filter_by(
                        name=link_data['name'],
                        url=link_data['url'],
                        category_id=category.id
                    ).first()
                    
                    if not existing_link:
                        link = Link(
                            name=link_data['name'],
                            url=link_data['url'],
                            category_id=category.id
                        )
                        db.session.add(link)
        
        db.session.commit()
        return jsonify({'message': '数据导入成功'}), 200
        
    except json.JSONDecodeError:
        return jsonify({'message': '无效的JSON文件格式'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'导入失败: {str(e)}'}), 500
