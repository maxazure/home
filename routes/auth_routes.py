from flask import Blueprint, request, jsonify, redirect, session, current_app
from flask_login import login_user, login_required, logout_user, current_user
from models import db, User, IPBlock
from schemas import user_schema, ipblock_schema
from marshmallow import ValidationError
from datetime import datetime, timezone

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/admin/login')
def login():
    if current_user.is_authenticated:
        return redirect('/admin')
    return current_app.send_static_file('admin/index.html')

@auth_bp.route('/api/login', methods=['POST'])
def admin_login():
    if not request.is_json:
        return jsonify({'message': '请求格式错误'}), 400

    data = request.json
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': '用户名和密码不能为空'}), 400

    ip_address = request.remote_addr
    ip_block = IPBlock.query.filter_by(ip_address=ip_address).first()

    # 如果 IP 已被封禁，返回通用拒绝
    if ip_block and ip_block.is_blocked:
        return jsonify({'message': '访问被拒绝'}), 403

    user = User.query.filter_by(username=data['username']).first()

    # 用户名或密码错误
    if not user or not user.check_password(data['password']):
        current_time = datetime.now(timezone.utc)
        if not ip_block:
            ip_block = IPBlock(ip_address=ip_address, failed_attempts=1, last_attempt=current_time)
            db.session.add(ip_block)
        else:
            ip_block.failed_attempts += 1
            ip_block.last_attempt = current_time
            if ip_block.failed_attempts >= 10:
                ip_block.is_blocked = True
        db.session.commit()

        # 若刚好封禁 IP，则统一返回 403
        if ip_block and ip_block.is_blocked:
            return jsonify({'message': '访问被拒绝'}), 403

        # 更新用户失败次数，若达到锁定就 403
        if user:
            user.increment_failed_attempts()
            if user.is_locked:
                return jsonify({'message': '访问被拒绝'}), 403

        return jsonify({'message': '用户名或密码错误'}), 401

    # 用户名密码正确后，若用户锁定则统一返回 403
    if user.is_locked:
        return jsonify({'message': '访问被拒绝'}), 403

    # 重置 IPBlock 和用户失败计数
    if ip_block:
        ip_block.failed_attempts = 0
        ip_block.last_attempt = None
    user.reset_failed_attempts()
    
    login_user(user, remember=data.get('remember', True))
    session.permanent = True
    
    return jsonify({
        'success': True,
        'user': user_schema.dump(user)
    })

@auth_bp.route('/api/logout')
@login_required
def logout():
    logout_user()
    return jsonify({'success': True})

@auth_bp.route('/api/auth/status')
def auth_status():
    if current_user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'user': user_schema.dump(current_user)
        })
    return jsonify({'authenticated': False})
