import os
import time
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from app import ABSOLUTE_UPLOAD_FOLDER
from app.utils import allowed_file, api_response, upload_file_to_gcs

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return api_response(message="No file part", status=400)
    
    file = request.files['file']
    if file.filename == '':
        return api_response(message="No selected file", status=400)

    if not file or not allowed_file(file.filename):
        return api_response(message="Invalid file type", status=400)

    # Sanitize the original filename first
    sanitized_filename = secure_filename(file.filename)

    # Create a unique filename using timestamp prefix
    unique_filename = str(int(time.time())) + "_" + sanitized_filename

    # Construct the full path using the absolute upload folder path
    filepath = os.path.join(ABSOLUTE_UPLOAD_FOLDER, unique_filename)

    try:
        # file.save(filepath)
        url = upload_file_to_gcs(file, "test")

        # Return the generated unique filename
        return api_response(message="Upload successful", data={'filepath': url}, status=201)
    except Exception as e:
        # Log the error ideally
        print(f"Error saving file: {e}")
        return api_response(message="Error saving file", status=500)