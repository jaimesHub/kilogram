from flask import Blueprint

from app.utils import api_response, token_required

user_bp = Blueprint('user', __name__)

@user_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    """UC04: Get the profile of the current user."""
    # Get the username from the JWT token
    return api_response(data=current_user['profile'])