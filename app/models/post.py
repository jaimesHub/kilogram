from datetime import datetime
from app import db

class Post(db.Model):
    """Model Post"""
    __tablename__ = 'posts'
    
    id = db.Column('id', db.Integer, primary_key=True)
    user_id =  db.Column('user_id', db.Integer, db.ForeignKey('users.id'), nullable=False) # [Complete this]
    image_url = db.Column('image_url', db.String(255), nullable=False) # [Complete this]
    caption = db.Column('caption', db.Text) # [Complete this]    
    deleted = db.Column('deleted', db.Boolean, default=False) # [Complete this]
    created_at = db.Column('created_at', db.Integer, default=lambda: int(datetime.now().timestamp())) # [Complete this]
    updated_at = db.Column('updated_at', db.Integer, default=lambda: int(datetime.now().timestamp()), onupdate=lambda: int(datetime.now().timestamp())) # [Complete this]
    
    def __repr__(self):
        return f'Post: {self.id}, User: {self.user_id}'
    
    def to_dict(self):
        """Converting post to dictionary for API response.
        Returns:
            dict: Dictionary representation of the post.
        """
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'image_url': self.image_url,
            'caption': self.caption,
            'deleted': self.deleted,
            'created_at': datetime.utcfromtimestamp(self.created_at).isoformat() if self.created_at else None
        }
         
        return data