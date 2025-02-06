from flask import Blueprint, request, jsonify
from models import Link, Category, db
from schemas import link_schema, links_schema

link_bp = Blueprint('admin_link', __name__)

@link_bp.route('/api/links', methods=['GET'])
def get_links():
    links = Link.query.join(Category).all()
    return jsonify(link_schema.dump(links, many=True))

@link_bp.route('/api/links/<id>', methods=['GET'])
def get_link(id):
    link = db.session.get(Link, id)
    if not link:
        return jsonify({'message': '链接不存在'}), 404
    return jsonify(link_schema.dump(link))

@link_bp.route('/api/links', methods=['POST'])
def add_link():
    name = request.json['name']
    url = request.json['url']
    category_id = request.json['category_id']
    
    new_link = Link(name=name, url=url, category_id=category_id)
    db.session.add(new_link)
    db.session.commit()
    
    return jsonify(link_schema.dump(new_link))

@link_bp.route('/api/links/<id>', methods=['PUT'])
def update_link(id):
    link = db.session.get(Link, id)
    if not link:
        return jsonify({'message': '链接不存在'}), 404
    
    link.name = request.json.get('name', link.name)
    link.url = request.json.get('url', link.url)
    link.category_id = request.json.get('category_id', link.category_id)
    
    db.session.commit()
    return jsonify(link_schema.dump(link))

@link_bp.route('/api/links/<id>', methods=['DELETE'])
def delete_link(id):
    link = db.session.get(Link, id)
    if not link:
        return jsonify({'message': '链接不存在'}), 404
    db.session.delete(link)
    db.session.commit()
    return jsonify({'message': 'Link deleted successfully'})

@link_bp.route('/api/categories/<id>/links', methods=['GET'])
def get_category_links(id):
    category = Category.query.get_or_404(id)
    return jsonify(links_schema.dump(category.links))
