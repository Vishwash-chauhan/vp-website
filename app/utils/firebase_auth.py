import firebase_admin
from firebase_admin import credentials, auth, exceptions
from functools import wraps
from flask import request, jsonify, session, g, current_app
import os
import json
# Initialize Firebase Admin SDK

def init_firebase_app():
    """Initialize Firebase Admin SDK with the service account credentials"""
    if not firebase_admin._apps:
        cred = credentials.Certificate('firebase-auth.json')
        firebase_admin.initialize_app(cred)


# Token verification and user handling
def verify_firebase_token(id_token):
    """Verify Firebase ID token and return the decoded token"""
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        current_app.logger.error(f"Error verifying token: {str(e)}")
        return None


def get_token_from_request():
    """Extract the token from the Authorization header"""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None
    
    parts = auth_header.split()
    if parts[0].lower() != 'bearer' or len(parts) == 1:
        return None
    
    return parts[1]


def get_current_user():
    """Get the current Firebase user from the token in the request"""
    token = get_token_from_request()
    if not token:
        return None
    
    user_info = verify_firebase_token(token)
    return user_info


# Admin functionality
def set_admin_claim(uid, is_admin=True):
    """Set or remove admin claim for a user"""
    try:
        # Get the user's current claims
        user = auth.get_user(uid)
        current_claims = user.custom_claims or {}
        
        # Update the admin claim
        if is_admin:
            current_claims['admin'] = True
        elif 'admin' in current_claims:
            del current_claims['admin']
        
        # Set the custom claims
        auth.set_custom_user_claims(uid, current_claims)
        return True
    except Exception as e:
        current_app.logger.error(f"Error setting admin claim: {str(e)}")
        return False


def is_admin(user_info):
    """Check if the user has admin privileges"""
    if not user_info:
        return False
    
    # Check for admin claim in the token
    custom_claims = user_info.get('custom_claims', {})
    return custom_claims.get('admin', False) if custom_claims else False


# User management functions
def get_user(uid):
    """Get a user by UID"""
    try:
        return auth.get_user(uid)
    except exceptions.FirebaseError as e:
        current_app.logger.error(f"Error getting user: {str(e)}")
        return None


def list_users(limit=1000):
    """List all users (up to limit)"""
    try:
        users = []
        page = auth.list_users(max_results=limit)
        for user in page.iterate_all():
            users.append(user)
        return users
    except exceptions.FirebaseError as e:
        current_app.logger.error(f"Error listing users: {str(e)}")
        return []


def create_user(email, password=None, display_name=None, phone_number=None):
    """Create a new user in Firebase"""
    try:
        user_data = {
            'email': email,
            'email_verified': False
        }
        
        if password:
            user_data['password'] = password
        if display_name:
            user_data['display_name'] = display_name
        if phone_number:
            user_data['phone_number'] = phone_number
            
        user = auth.create_user(**user_data)
        return user
    except exceptions.FirebaseError as e:
        current_app.logger.error(f"Error creating user: {str(e)}")
        return None


def update_user(uid, display_name=None, email=None, phone_number=None, disabled=None):
    """Update a user's information"""
    try:
        user_data = {}
        
        if display_name is not None:
            user_data['display_name'] = display_name
        if email is not None:
            user_data['email'] = email
        if phone_number is not None:
            user_data['phone_number'] = phone_number
        if disabled is not None:
            user_data['disabled'] = disabled
            
        user = auth.update_user(uid, **user_data)
        return user
    except exceptions.FirebaseError as e:
        current_app.logger.error(f"Error updating user: {str(e)}")
        return None


def delete_user(uid):
    """Delete a user from Firebase"""
    try:
        auth.delete_user(uid)
        return True
    except exceptions.FirebaseError as e:
        current_app.logger.error(f"Error deleting user: {str(e)}")
        return False


def disable_user(uid, disable=True):
    """Disable or enable a user"""
    return update_user(uid, disabled=disable)


# Authentication decorators
def firebase_login_required(f):
    """Decorator to require Firebase authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = get_token_from_request()
        if not token:
            return jsonify({'error': 'Authentication required'}), 401
        
        user_info = verify_firebase_token(token)
        if not user_info:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Store the user info in Flask's g object for access in the route
        g.user = user_info
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = get_token_from_request()
        if not token:
            return jsonify({'error': 'Authentication required'}), 401
        
        user_info = verify_firebase_token(token)
        if not user_info:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        if not is_admin(user_info):
            return jsonify({'error': 'Admin privileges required'}), 403
        
        # Store the user info in Flask's g object for access in the route
        g.user = user_info
        return f(*args, **kwargs)
    return decorated_function


# Helper functions
def user_to_dict(firebase_user):
    """Convert Firebase user object to dictionary"""
    if not firebase_user:
        return None
        
    user_dict = {
        'uid': firebase_user.uid,
        'display_name': firebase_user.display_name,
        'email': firebase_user.email,
        'phone_number': firebase_user.phone_number,
        'photo_url': firebase_user.photo_url,
        'disabled': firebase_user.disabled,
        'email_verified': firebase_user.email_verified,
        'custom_claims': firebase_user.custom_claims or {},
        'provider_data': [p._data for p in firebase_user.provider_data] if firebase_user.provider_data else [],
        'user_metadata': {
            'creation_timestamp': firebase_user.user_metadata.creation_timestamp,
            'last_sign_in_timestamp': firebase_user.user_metadata.last_sign_in_timestamp
        } if firebase_user.user_metadata else {}
    }
    
    return user_dict