from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from functools import wraps
from google.cloud import storage
import uuid

from app.models.user import User

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

BUCKET_NAME = "kilogram-media"
client = storage.Client()
bucket = client.bucket(BUCKET_NAME)

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

def allowed_file(filename):
    """Check if the file extension is allowed
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_file_to_gcs(file_obj, destination_folder):
    """Upload file to Google Cloud Storage
    """
    filename = f"{destination_folder}/{uuid.uuid4().hex}_{file_obj.filename}"
    blob = bucket.blob(filename)
    blob.upload_from_file(file_obj, content_type=file_obj.content_type)
    return blob.public_url
