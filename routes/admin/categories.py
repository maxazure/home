from flask import Blueprint, request, jsonify
from models import Category, db
from schemas import category_schema, categories_schema

category_bp = Blueprint('category', __name__)

@category_bp.route('/api/categories', methods=['GET'])
def get_categories():
    categories = Category.query.order_by(Category.section_order, Category.category_order).all()
    return jsonify(categories_schema.dump(categories))

@category_bp.route('/api/categories/<id>', methods=['GET'])
def get_category(id):
    category = db.session.get(Category, id)
    if not category:
        return jsonify({'message': '分类不存在'}), 404
    return jsonify(category_schema.dump(category))

@category_bp.route('/api/categories', methods=['POST'])
def add_category():
    title = request.json['title']
    section_name = request.json['section_name']
    
    new_category = Category(title=title, section_name=section_name)
    db.session.add(new_category)
    db.session.commit()
    
    return jsonify(category_schema.dump(new_category))

@category_bp.route('/api/categories/<id>', methods=['PUT'])
def update_category(id):
    category = db.session.get(Category, id)
    if not category:
        return jsonify({'message': '分类不存在'}), 404
    
    category.title = request.json.get('title', category.title)
    category.section_name = request.json.get('section_name', category.section_name)
    
    db.session.commit()
    return jsonify(category_schema.dump(category))

@category_bp.route('/api/categories/<id>', methods=['DELETE'])
def delete_category(id):
    category = db.session.get(Category, id)
    if not category:
        return jsonify({'message': '分类不存在'}), 404
    db.session.delete(category)
    db.session.commit()
    return jsonify({'message': 'Category deleted successfully'})

@category_bp.route('/api/admin/categories/reorder', methods=['POST'])
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
