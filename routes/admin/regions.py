from flask import Blueprint, jsonify, request
from flask_login import login_required
from models import db, Region
from schemas import region_schema, regions_schema

region_bp = Blueprint('admin_region', __name__, url_prefix='/api/regions')

@region_bp.route('/', methods=['GET'])
def get_regions():
    regions = Region.query.all()
    return jsonify(regions_schema.dump(regions))

@region_bp.route('/<id>', methods=['GET'])
def get_region(id):
    region = db.session.get(Region, id)
    if region:
        return jsonify(region_schema.dump(region))
    return jsonify({'message': 'Region not found'}), 404

@region_bp.route('/', methods=['POST'])
@login_required
def create_region():
    data = request.get_json()
    region = region_schema.load(data)
    db.session.add(region)
    db.session.commit()
    return jsonify(region_schema.dump(region)), 201

@region_bp.route('/<id>', methods=['PUT'])
@login_required
def update_region(id):
    region = db.session.get(Region, id)
    if not region:
        return jsonify({'message': 'Region not found'}), 404
    
    data = request.get_json()
    region = region_schema.load(data, instance=region)
    db.session.commit()
    return jsonify(region_schema.dump(region))

@region_bp.route('/<id>', methods=['DELETE'])
@login_required
def delete_region(id):
    region = db.session.get(Region, id)
    if not region:
        return jsonify({'message': 'Region not found'}), 404
    
    db.session.delete(region)
    db.session.commit()
    return jsonify({'message': 'Region deleted'})
