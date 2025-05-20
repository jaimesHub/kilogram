from datetime import datetime
from app import db

class Like(db.Model):
    """Model user's like feature"""
    __tablename__ = 'likes'
    user_id = db.Column('user_id', db.Integer, primary_key=True, nullable=False)
    post_id = db.Column('post_id', db.Integer, primary_key=True, nullable=False)
    created_at = db.Column('created_at', db.Integer, nullable=False, default=lambda: int(datetime.now().timestamp()))

    def __repr__(self):
        return f'User {self.user_id} likes the post {self.post_id}'