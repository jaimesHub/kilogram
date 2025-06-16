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
    password_hash = db.Column('password_hash', db.String(255), nullable=True) # Made nullable for social users
    fullname = db.Column('fullname', db.String(100))
    bio = db.Column('bio', db.Text)
    profile_picture = db.Column('profile_picture', db.String(255), default='default.jpg')
    created_at = db.Column('created_at', db.Integer, default=lambda: int(datetime.now().timestamp()))
    updated_at = db.Column('updated_at', db.Integer, default=lambda: int(datetime.now().timestamp()), onupdate=lambda: int(datetime.now().timestamp()))

    # New field for social authentication
    signup_method = db.Column('signup_method', db.String(20), default='username')

    def __repr__(self):
        """Return a string representation of the user.
        """
        return f'<User {self.username} :: Email {self.email}>'
    
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
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    # Social authentication helper methods
    def has_social_account(self, provider=None):
        """Check if user has social account(s)"""
        if provider:
            return any(acc.provider == provider for acc in self.social_accounts)
        return len(self.social_accounts) > 0
    
    def get_social_account(self, provider):
        """Get specific social account by provider"""
        return next((acc for acc in self.social_accounts if acc.provider == provider), None)
    
    def can_login_without_password(self):
        """Check if user can login without password (has social accounts)"""
        return self.has_social_account() and not self.password_hash
    
    def get_linked_providers(self):
        """Get list of linked social providers"""
        return [acc.provider for acc in self.social_accounts]
    
    def has_password(self):
        """Check if user has a password set"""
        return bool(self.password_hash)
    
    # Serialization methods
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

    def to_dict_with_social(self):
        """Extended user dict with social account info"""
        base_dict = self.to_dict()
        
        # Add social account info
        base_dict.update({
            'social_accounts': [acc.to_dict() for acc in self.social_accounts],
            'has_password': self.has_password(),
            'linked_providers': self.get_linked_providers(),
            'can_login_without_password': self.can_login_without_password()
        })
        
        return base_dict

    @staticmethod
    def find_by_username(username):
        """Find user by username"""
        return User.query.filter_by(username=username).first()
    
    @staticmethod
    def find_by_email(email):
        """Find user by email"""
        return User.query.filter_by(email=email).first()
    
    @staticmethod
    def find_by_username_or_email(identifier):
        """Find user by username or email"""
        return User.query.filter(
            (User.username == identifier) | (User.email == identifier)
        ).first()