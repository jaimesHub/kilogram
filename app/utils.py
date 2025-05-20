from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from functools import wraps
from google.cloud import storage
import uuid
from datetime import timedelta

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
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS and filename.rsplit('.', 1)[0].lower() != ''

def upload_file_to_gcs(file_obj, destination_folder):
    """Upload file to Google Cloud Storage
    """
    filename = f"{destination_folder}/{uuid.uuid4().hex}_{file_obj.filename}"
    blob = bucket.blob(filename)
    blob.upload_from_file(file_obj, content_type=file_obj.content_type)
    return blob.public_url

def generate_signed_url(filename, bucket_name, expiration_minutes=15):
    """
    Giả sử bucket đã được thiết lập không công khai, chúng ta có thể tạo signed URL
    Khi nào cần ?
        - Ảnh đại diện chỉ hiển thị sau khi người dùng đăng nhập.
        - File video riêng tư, ví dụ video nháp chưa đăng.
        - Tăng bảo mật cho ảnh tải từ mobile app.
        - Giới hạn thời gian xem file, giảm nguy cơ bị phát tán URL.
    Nếu không có yêu cầu riêng tư, việc dùng public URL vẫn là lựa chọn đơn giản và tiết kiệm chi phí hơn.
    """
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(filename)

    url = blob.generate_signed_url(
        version="v4",
        expiration=timedelta(minutes=expiration_minutes),
        method="GET"
    )

    return url

def delete_file_from_gcs(filename, bucket_name):
    """UC09 – người dùng xóa bài viết, chúng ta cũng cần xóa ảnh/video khỏi bucket tương ứng.
    """
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(filename)
    blob.delete()