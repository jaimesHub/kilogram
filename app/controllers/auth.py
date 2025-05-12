from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

from app.utils import api_response
from app.models.user import User
from app import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """UC01: Register a new user account."""
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    fullname = data.get('fullname')
    email = data.get('email')

    # Validate username, password, and email
    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters long'}), 400
    if '@' not in email:
        return jsonify({'error': 'Invalid email format'}), 400
        
    # Check username & password already existed or not
    if User.query.filter_by(username=data['username']).first():
        return api_response(message="Username already exists", status=400)

    if User.query.filter_by(email=data['email']).first():
        return api_response(message="Email already exists", status=400)

    # Basic user profile
    try:
        user = User(
            username=data['username'],
            email=data['email'],
            fullname=data['fullname'],
        )

        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        return api_response(
            message="User registered successfully",
            data={"user_id": user.id, "username": user.username},
            status=201
        )
    except Exception as e:
        db.session.rollback()
        return api_response(message=f"Error registering user: {str(e)}", status=500)

@auth_bp.route('/login', methods=['POST'])
def login():
    """UC02: Log in to an existing user account."""
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=data['username']).first()
    if not user or not user.check_password(data['password']):
        return api_response(message="Username or password is incorrect", status=401)
        
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return api_response(
        message='Login successful',
        data={
            'access_token': access_token,
            'refresh_token': refresh_token,
            "user": user.to_dict()
        })

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """UC03: Log out of the current user account."""