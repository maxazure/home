from flask import Blueprint, request, jsonify, redirect, session
from flask_login import login_user, login_required, logout_user, current_user
from models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/admin/login', methods=['GET'])
def login():
    if current_user.is_authenticated:
        return redirect('/admin')
    return send_from_directory('www', 'admin/login.html')

@auth_bp.route('/api/admin/login', methods=['POST'])
def admin_login():
    if not request.is_json:
        return jsonify({'message': '请求格式错误'}), 400
        
    username = request.json.get('username')
    password = request.json.get('password')
    remember = request.json.get('remember', True)  # 默认开启记住我
    
    if not username or not password:
        return jsonify({'message': '用户名和密码不能为空'}), 400
        
    user = User.query.filter_by(username=username).first()
    if user and not user.is_locked and user.check_password(password):
        login_user(user, remember=remember)  # 使用记住我功能
        session.permanent = True  # 设置 session 为永久性
        return jsonify({'success': True})
    
    return jsonify({'message': '用户名或密码错误'}), 401

@auth_bp.route('/api/admin/logout')
@login_required
def logout():
    logout_user()
    return redirect('/admin/login.html')

@auth_bp.route('/api/auth/status')
def auth_status():
    if current_user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'username': current_user.username
        })
    return jsonify({
        'authenticated': False
    })

@auth_bp.route('/api/auth/logout', methods=['POST'])
@login_required
def api_logout():
    logout_user()
    return jsonify({'success': True})
