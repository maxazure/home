from flask import Blueprint, request, jsonify
from flask_login import login_required
from models import User, db
from schemas import user_schema, users_schema

user_bp = Blueprint('user', __name__)

@user_bp.route('/api/admin/users', methods=['GET'])
@login_required
def admin_get_users():
    users = User.query.all()
    return jsonify(users_schema.dump(users))

@user_bp.route('/api/admin/users', methods=['POST'])
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

@user_bp.route('/api/admin/users/<id>', methods=['PUT'])
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

@user_bp.route('/api/admin/users/<id>', methods=['DELETE'])
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

@user_bp.route('/api/admin/users/<id>/unlock', methods=['POST'])
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
