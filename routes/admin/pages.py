from flask import Blueprint, request, jsonify
from flask_login import login_required
from models import db, Page
from schemas import page_schema, pages_schema

page_bp = Blueprint('admin_page', __name__, url_prefix='/api/pages')

@page_bp.route('/', methods=['GET'])
def get_pages():
    pages = Page.query.all()
    return jsonify(pages_schema.dump(pages))

@page_bp.route('/<id>', methods=['GET'])
def get_page(id):
    page = db.session.get(Page, id)
    if page:
        return jsonify(page_schema.dump(page))
    return jsonify({'message': 'Page not found'}), 404

@page_bp.route('/', methods=['POST'])
@login_required
def create_page():
    data = request.get_json()
    page = page_schema.load(data)
    db.session.add(page)
    db.session.commit()
    return jsonify(page_schema.dump(page)), 201

@page_bp.route('/<id>', methods=['PUT'])
@login_required
def update_page(id):
    page = db.session.get(Page, id)
    if not page:
        return jsonify({'message': 'Page not found'}), 404
    
    data = request.get_json()
    page = page_schema.load(data, instance=page)
    db.session.commit()
    return jsonify(page_schema.dump(page))

@page_bp.route('/<id>', methods=['DELETE'])
@login_required
def delete_page(id):
    page = db.session.get(Page, id)
    if not page:
        return jsonify({'message': 'Page not found'}), 404
    
    db.session.delete(page)
    db.session.commit()
    return jsonify({'message': 'Page deleted'})
