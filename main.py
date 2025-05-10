import os
from flask import Flask, request, jsonify
from functools import wraps
from datetime import datetime
from flask_jwt_extended import create_access_token, create_refresh_token, JWTManager
from werkzeug.security import generate_password_hash, check_password_hash

from utils import api_response

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev_secret_key")

jwt = JWTManager(app)

users = {}  # { username: { password: hashed_password, profile: {...} } }

@app.route("/")
def hello_world():
  """Example Hello World route."""
  name = os.environ.get("NAME", "World")
  return f"Hello {name}!"

@app.route('/register', methods=['POST'])
def register():
    """UC01: Register a new account"""
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    full_name = data.get('full_name')
    email = data.get('email')

    # Validate username, password and email
    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400
    if username in users:
        return jsonify({'error': 'Username already exists'}), 400
    if '@' not in email:
        return jsonify({'error': 'Invalid email format'}), 400
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters long'}), 400
    if not full_name:
        return jsonify({'error': 'Missing full name'}), 400

    # Hashing password before creating a new account
    pw_hash = generate_password_hash(password)

    # A new account will be created with the following profile
    profile = {
        'username': username,
        'email': email,
        'full_name': full_name,
        'profile_picture': 'default.png',
        'bio': '',
        'created_at': int(datetime.now().timestamp())
    }

    users[username] = {'password': pw_hash, 'profile': profile}

    return api_response(data=profile, message='User registered successfully')

@app.route('/login', methods=['POST'])
def login():
    """UC02: Login to an existing user account."""
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')

    # Check whether the username exists in the system or not
    if username not in users:
        return jsonify({'error': 'Invalid username or password'}), 401

    # Verify the password which is input from user is correct or incorrect
    if not check_password_hash(users[username]['password'], password):
        return jsonify({'error': 'Invalid username or password'}), 401

    # If ok, create access token and refresh token
    access_token = create_access_token(identity=username)
    refresh_token = create_refresh_token(identity=username)

    # Return response with token and user profile
    return api_response(
        message='Login successful',
        data={
            'access_token': access_token,
            'refresh_token': refresh_token,
            "user": users[username]['profile'],
        })


if __name__ == "__main__":
  app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))