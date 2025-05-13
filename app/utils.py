from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from functools import wraps

from app.models.user import User

def api_response(data=None, message=None, status=200):
    """Formating JSON response for API"""
    response = {
        'success': 200 <= status < 300,
        'status': status
    }

    if message:
        response['message'] = message

    if data is not None:
        response['data'] = data

    return jsonify(response), status

def token_required(fn):
    """Decorator for authenticate API Using JWT token."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            # Check if the JWT token is valid or not
            verify_jwt_in_request()

            # Get the user_id (identity) from the JWT token
            user_id = get_jwt_identity()

            # Get the user profile from the database
            current_user = User.query.get(user_id)

            # Check if the user exists in the database
            if not current_user:
                return api_response(message="User does not exist", status=404)

            # Calling the original endpoint with the authenticated user profile
            return fn(current_user, *args, **kwargs)
        except Exception as e:
            return api_response(message=f"Token is invalid: {str(e)}", status=401)
    return wrapper