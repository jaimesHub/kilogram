from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

from app.utils import api_response
from app import users

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """UC01: Register a new user account."""

@auth_bp.route('/login', methods=['POST'])
def login():
    """UC02: Log in to an existing user account."""

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """UC03: Log out of the current user account."""