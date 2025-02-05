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
