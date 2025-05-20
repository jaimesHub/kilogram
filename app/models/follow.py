from datetime import datetime
from app import db

class Follow(db.Model):
    """Model for following feature between users and users"""
    __tablename__ = 'follows'

    # composite primary key
    follower_id = db.Column('follower_id', db.Integer, primary_key=True)
    following_id = db.Column('following_id', db.Integer, primary_key=True) # ID of the user being followed
    #

    created_at = db.Column('created_at', db.Integer, default=lambda: int(datetime.now().timestamp()))

    def __repr__(self):
        return f' {self.following_id}>'