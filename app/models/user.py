from app import db
from app.models.follow import Follow

from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model):
    """Model users"""
    __tablename__ = 'users'
    
    id = db.Column('id', db.Integer, primary_key=True)
    username = db.Column('username', db.String(50), unique=True, nullable=False)
    email = db.Column('email', db.String(100), unique=True, nullable=False)
    password_hash = db.Column('password_hash', db.String(255), nullable=False)
    fullname = db.Column('fullname', db.String(100))
    bio = db.Column('bio', db.Text)
    profile_picture = db.Column('profile_picture', db.String(255), default='default.jpg')
    created_at = db.Column('created_at', db.Integer, default=lambda: int(datetime.now().timestamp()))
    updated_at = db.Column('updated_at', db.Integer, default=lambda: int(datetime.now().timestamp()), onupdate=lambda: int(datetime.now().timestamp()))

    def __repr__(self):
        """Return a string representation of the user.
        """
        return f''
    
    def set_password(self, password):
        """Set hasing password
        Args:
            password (str): Raw password will be hashed
        """
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Comparing password with hashed password
        Args:
            password (str): Raw password will be hashed
        Returns:
            bool: True if password is correct, False otherwise
        """
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self, viewer=None):
        """Converting user to dictionary for API response.
        Returns:
            dict: Dictionary representation of the user.
        """
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'fullname': self.fullname,
            'bio': self.bio,
            'profile_picture': self.profile_picture,
            'created_at': datetime.utcfromtimestamp(self.created_at).isoformat() if self.created_at else None,
        }

        # viewer ở đây là người muốn xem profile
        # "is_following" để kiểm tra xem viewer có đang follow user này không.
        if viewer:
            data['follower_count'] = Follow.query.filter_by(following_id=self.id).count()
            data['following_count'] = Follow.query.filter_by(follower_id=self.id).count()
            data['is_following'] = Follow.query.filter_by(follower_id=viewer.id, following_id=self.id).first() is not None

        return data