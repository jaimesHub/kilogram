import os
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy

# Initialize extensions
jwt = JWTManager()
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "your-very-secure-secret-key"
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    jwt.init_app(app)
    db.init_app(app)

    from app.controllers.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    from app.controllers.user import user_bp
    app.register_blueprint(user_bp, url_prefix='/api/users')

    return app