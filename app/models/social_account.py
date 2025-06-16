from app import db
from datetime import datetime
import json

class SocialAccount(db.Model):
    """Model for social authentication accounts"""
    __tablename__ = 'social_accounts'
    
    id = db.Column('id', db.Integer, primary_key=True)
    user_id = db.Column('user_id', db.Integer, db.ForeignKey('users.id'), nullable=False)
    provider = db.Column('provider', db.String(50), nullable=False)  # 'google', 'facebook'
    provider_id = db.Column('provider_id', db.String(255), nullable=False)  # ID from provider
    provider_email = db.Column('provider_email', db.String(100))  # Email from provider
    access_token = db.Column('access_token', db.Text)  # Encrypted OAuth token
    refresh_token = db.Column('refresh_token', db.Text)  # Encrypted refresh token
    expires_at = db.Column('expires_at', db.Integer)  # Token expiration timestamp
    profile_data = db.Column('profile_data', db.JSON)  # Additional profile info
    created_at = db.Column('created_at', db.Integer, nullable=False, default=lambda: int(datetime.now().timestamp()))
    updated_at = db.Column('updated_at', db.Integer, nullable=False, default=lambda: int(datetime.now().timestamp()), onupdate=lambda: int(datetime.now().timestamp()))
    
    # Relationships
    user = db.relationship('User', backref=db.backref('social_accounts', lazy=True, cascade="all, delete-orphan"))
    
    # Table constraints
    __table_args__ = (
        db.UniqueConstraint('provider', 'provider_id', name='unique_provider_account'),
        db.Index('idx_user_provider', 'user_id', 'provider'),
        db.Index('idx_provider_lookup', 'provider', 'provider_id'),
    )
    
    def __repr__(self):
        return f'<SocialAccount {self.provider}:{self.provider_id}::UserID {self.user_id}>'
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'provider': self.provider,
            'provider_email': self.provider_email,
            'linked_at': datetime.fromtimestamp(self.created_at).isoformat() + 'Z',
            'has_valid_token': bool(self.access_token)
        }
    
    @staticmethod
    def find_by_provider_id(provider, provider_id):
        """Find social account by provider and provider_id"""
        return SocialAccount.query.filter_by(
            provider=provider, 
            provider_id=str(provider_id)
        ).first()
    
    @staticmethod
    def find_by_user_and_provider(user_id, provider):
        """Find social account by user and provider"""
        return SocialAccount.query.filter_by(
            user_id=user_id,
            provider=provider
        ).first()
    
    def update_token(self, access_token, refresh_token=None, expires_at=None):
        """Update OAuth tokens"""
        from app.utils.crypto_utils import encrypt_token
        
        self.access_token = encrypt_token(access_token)
        if refresh_token:
            self.refresh_token = encrypt_token(refresh_token)
        if expires_at:
            self.expires_at = expires_at
        self.updated_at = int(datetime.now().timestamp())
    
    def get_decrypted_token(self):
        """Get decrypted access token"""
        if not self.access_token:
            return None
        
        from app.utils.crypto_utils import decrypt_token
        return decrypt_token(self.access_token)