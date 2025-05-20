from datetime import datetime
from app import db
from app.models.like import Like
from app.models.user import User

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
    
    def to_dict(self, include_author=False, include_likes=False, current_user=None):
        """Converting post to dictionary for API response.
        Returns:
            dict: Dictionary representation of the post.
        """
        data = {
            'id': self.id,
            'author_id': self.user_id,
            'image_url': self.image_url,
            'caption': self.caption,
            'deleted': self.deleted,
            'created_at': datetime.utcfromtimestamp(self.created_at).isoformat() if self.created_at else None
        }

        if include_author:
            user = User.query.get(self.user_id)
            data['author'] = user.to_dict()

        if include_likes:
            data['like_count'] = Like.query.filter_by(post_id=self.id).count()
            if current_user:
                data['liked_by_current_user'] = Like.query.filter_by(post_id=self.id, user_id=current_user.id).first() is not None
            else:
                data['liked_by_current_user'] = False
         
        return data