import datetime
from flask import Blueprint, request, jsonify, current_app
from functools import wraps
from base64 import b64decode

from models import Admin
from schemas import AdminLogin, AdminLoginResponse

auth_bp = Blueprint("auth", __name__)

# Route: Admin Login
@auth_bp.route('/api/admin/login', methods=['POST'])
def admin_login():
    try:
        data = request.get_json()
        login_data = AdminLogin(**data)

        admin = Admin.query.filter_by(username=login_data.username).first()
        if admin and admin.check_password(login_data.password):
            response = AdminLoginResponse(
                success=True
            )
            return jsonify(response.dict())
        else:
            response = AdminLoginResponse(
                success=False,
                error='Invalid credentials'
            )
            return jsonify(response.dict()), 401
    except ValueError as e:
        # Handle validation errors
        response = AdminLoginResponse(
            success=False,
            error=str(e)
        )
        return jsonify(response.dict()), 400
    except Exception as e:
        response = AdminLoginResponse(
            success=False,
            error=str(e)
        )
        return jsonify(response.dict()), 400

# Admin logout route - no longer needed but kept for API compatibility
@auth_bp.route('/api/admin/logout', methods=['POST'])
def admin_logout():
    return jsonify({'success': True, 'message': 'Logged out successfully'})

# Admin required decorator that checks for basic auth
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Basic '):
            return jsonify({'error': 'Admin authentication required'}), 401

        try:
            # Extract and decode the base64 credentials
            encoded_credentials = auth_header.split(' ')[1]
            decoded_credentials = b64decode(encoded_credentials).decode('utf-8')
            username, password = decoded_credentials.split(':')

            # Check if credentials are valid
            admin = Admin.query.filter_by(username=username).first()
            if not admin or not admin.check_password(password):
                return jsonify({'error': 'Invalid credentials'}), 401

            return f(*args, **kwargs)
        except Exception:
            return jsonify({'error': 'Invalid authentication format'}), 401
    return decorated
