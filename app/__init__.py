from flask import Flask
from flask_jwt_extended import JWTManager

users = {}  # { username: { password: hashed_password, profile: {...} } }

# Initialize extensions
jwt = JWTManager(app)

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "your-very-secure-secret-key"
    jwt.init_app(app)

    from app.controllers.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    from app.controllers.user import user_bp
    app.register_blueprint(user_bp, url_prefix='/api/users')

    return app