from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, g
from app.utils.firebase_auth import (
    firebase_login_required, admin_required, verify_firebase_token, 
    get_user, list_users, delete_user, update_user, set_admin_claim, 
    disable_user, user_to_dict
)

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET'])
def login():
    """Render the login page"""
    return render_template('auth/login.html')


@auth.route('/signup', methods=['GET'])
def signup():
    """Render the signup page"""
    return render_template('auth/signup.html')


@auth.route('/forgot-password', methods=['GET'])
def forgot_password():
    """Render the forgot password page"""
    return render_template('auth/forgot_password.html')


@auth.route('/logout')
def logout():
    """Client-side logout - just redirects to login page"""
    return redirect(url_for('auth.login'))


# API endpoints for Firebase authentication
@auth.route('/api/verify-token', methods=['POST'])
def verify_token():
    """Verify a Firebase ID token from client and return user info"""
    data = request.get_json()
    if not data or 'token' not in data:
        return jsonify({'error': 'No token provided'}), 400
    
    id_token = data['token']
    decoded_token = verify_firebase_token(id_token)
    
    if not decoded_token:
        return jsonify({'error': 'Invalid token'}), 401
    
    return jsonify({
        'success': True,
        'user': {
            'uid': decoded_token.get('uid'),
            'email': decoded_token.get('email'),
            'name': decoded_token.get('name', ''),
            'isAdmin': decoded_token.get('custom_claims', {}).get('admin', False),
            'emailVerified': decoded_token.get('email_verified', False)
        }
    })


@auth.route('/api/user-info', methods=['GET'])
@firebase_login_required
def get_user_info():
    """Get the current user's information"""
    user_info = g.user
    uid = user_info.get('uid')
    
    # Get detailed info from Firebase
    firebase_user = get_user(uid)
    if not firebase_user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'success': True,
        'user': user_to_dict(firebase_user)
    })


@auth.route('/api/users', methods=['GET'])
@admin_required
def get_users():
    """Get all users (admin only)"""
    users = list_users()
    return jsonify({
        'success': True,
        'users': [user_to_dict(user) for user in users]
    })


@auth.route('/api/users/<uid>', methods=['GET'])
@admin_required
def get_user_by_id(uid):
    """Get user by UID (admin only)"""
    user = get_user(uid)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'success': True,
        'user': user_to_dict(user)
    })


@auth.route('/api/users/<uid>', methods=['DELETE'])
@admin_required
def delete_user_by_id(uid):
    """Delete a user (admin only)"""
    success = delete_user(uid)
    if not success:
        return jsonify({'error': 'Failed to delete user'}), 500
    
    return jsonify({
        'success': True,
        'message': 'User deleted successfully'
    })


@auth.route('/api/users/<uid>/disable', methods=['POST'])
@admin_required
def disable_user_by_id(uid):
    """Disable or enable a user (admin only)"""
    data = request.get_json() or {}
    disable = data.get('disable', True)
    
    user = disable_user(uid, disable=disable)
    if not user:
        return jsonify({'error': 'Failed to update user status'}), 500
    
    action = 'disabled' if disable else 'enabled'
    return jsonify({
        'success': True,
        'message': f'User {action} successfully',
        'user': user_to_dict(user)
    })


@auth.route('/api/users/<uid>/admin', methods=['POST'])
@admin_required
def set_admin_status(uid):
    """Set or remove admin privilege for a user (admin only)"""
    data = request.get_json() or {}
    is_admin = data.get('admin', True)
    
    success = set_admin_claim(uid, is_admin=is_admin)
    if not success:
        return jsonify({'error': 'Failed to update admin status'}), 500
    
    action = 'granted' if is_admin else 'removed'
    return jsonify({
        'success': True,
        'message': f'Admin privileges {action} successfully'
    })