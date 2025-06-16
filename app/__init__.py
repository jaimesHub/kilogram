import os
from flask import Flask, send_from_directory, request, Response, make_response
from prometheus_client import Counter, Gauge, Histogram, Summary, make_wsgi_app, REGISTRY
from werkzeug.middleware.dispatcher import DispatcherMiddleware
import time
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy

from flask_migrate import Migrate
from dotenv import load_dotenv
from datetime import timedelta

# Load environment variables
load_dotenv()

# --- Prometheus Metrics ---
# Example: Counting the number of request by METHOD and ENDPOINT
REQUEST_COUNT = Counter(
    'kilogram_http_requests_total_test',
    'Total number of HTTP requests',
    ['method', 'endpoint']
)

# Example: Counting the number of posts created
POSTS_CREATED = Counter(
    'kilogram_posts_created_total_test',
    'Number of posts created'
)

# Example: Measuring the latency of HTTP requests
REQUEST_LATENCY = Histogram(
    'kilogram_http_request_duration_seconds_test',
    'HTTP Request latency',
    ['method', 'endpoint']
)

# Example: Monitoring the number of active users
# ACTIVE_USERS = Gauge(
#     'sydegram_active_users',
#     'Number of active users'
# ) # Gauge phức tạp hơn, cần cơ chế cập nhật

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

UPLOAD_FOLDER = 'uploads'
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(APP_ROOT)
ABSOLUTE_UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, UPLOAD_FOLDER)

def create_app():
    app = Flask(__name__)

    # Configuration
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "your-very-secure-secret-key")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # JWT Configuration
    app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "jwt-secret-string")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=60)

    # OAuth Configuration
    app.config["GOOGLE_CLIENT_ID"] = os.environ.get("GOOGLE_CLIENT_ID")
    app.config["GOOGLE_CLIENT_SECRET"] = os.environ.get("GOOGLE_CLIENT_SECRET")
    app.config["FACEBOOK_CLIENT_ID"] = os.environ.get("FACEBOOK_CLIENT_ID")
    app.config["FACEBOOK_CLIENT_SECRET"] = os.environ.get("FACEBOOK_CLIENT_SECRET")
    app.config["OAUTH_REDIRECT_URI"] = os.environ.get("OAUTH_REDIRECT_URI", "http://localhost:5000")

    # Security
    app.config["ENCRYPTION_KEY"] = os.environ.get("ENCRYPTION_KEY")

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Import models to ensure they're registered with SQLAlchemy
    from app.models import user, post, like, follow, social_account

    # --- Middleware để thu thập metrics request cơ bản ---
    @app.before_request
    def before_request():
        # Ghi lại thời điểm bắt đầu request để tính latency
        request.start_time = time.time()

    @app.after_request
    def after_request(response):
        if hasattr(request, 'endpoint') and request.endpoint != 'static' and request.endpoint != 'prometheus':
             # Tính latency
            latency = time.time() - request.start_time
            # Ghi nhận latency vào Histogram
            REQUEST_LATENCY.labels(method=request.method, endpoint=request.endpoint).observe(latency)
            # Đếm request
            REQUEST_COUNT.labels(method=request.method, endpoint=request.endpoint).inc()
        return response

    # --- Import và register blueprints ---
    from app.controllers.auth import auth_bp
    from app.controllers.user import user_bp
    from app.controllers.post import post_bp
    from app.controllers.upload import upload_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(post_bp, url_prefix='/api/posts')
    app.register_blueprint(upload_bp, url_prefix='/api/upload')

    # --- Tạo endpoint /metrics ---
    # Sử dụng DispatcherMiddleware để phục vụ endpoint /metrics riêng biệt
    # mà không ảnh hưởng bởi các middleware hoặc blueprint khác của Flask app chính
    app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
        '/metrics': make_wsgi_app(REGISTRY)
    })

    # Ví dụ cách increment counter POSTS_CREATED trong controller
    # Bạn cần truyền metric này vào blueprint hoặc import trực tiếp
    # Ví dụ trong app/controllers/post.py:
    # from app import POSTS_CREATED # Giả sử bạn đặt metric ở __init__
    #
    # @post_bp.route('', methods=['POST'])
    # @token_required
    # def create_post(current_user):
    #     # ... (logic tạo post)
    #     if post_created_successfully:
    #          POSTS_CREATED.inc() # Increment counter
    #     # ... (trả về response)

    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        return send_from_directory(ABSOLUTE_UPLOAD_FOLDER, filename)

    if not os.path.exists(ABSOLUTE_UPLOAD_FOLDER):
        os.makedirs(ABSOLUTE_UPLOAD_FOLDER)

    return app