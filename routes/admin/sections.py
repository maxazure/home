from flask import Blueprint, request, jsonify
from models import Category, db
from schemas import category_schema, categories_schema

section_bp = Blueprint('section', __name__)

@section_bp.route('/api/admin/sections', methods=['POST'])
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

@section_bp.route('/api/admin/sections/update', methods=['POST'])
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

@section_bp.route('/api/admin/sections/reorder', methods=['POST'])
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

@section_bp.route('/api/admin/sections/delete', methods=['POST'])
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
            db.session.delete(category)
        
        db.session.commit()
        return jsonify({'message': '区域删除成功'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'删除区域失败: {str(e)}'}), 500
