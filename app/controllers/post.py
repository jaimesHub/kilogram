from flask import Blueprint, request
from app import db
from app.utils import api_response, token_required
from app.models.post import Post

post_bp = Blueprint('post', __name__)

@post_bp.route('', methods=['POST'])
@token_required
def create_post(current_user):
    """UC07: API to create a new post."""

    data = request.get_json() or {}
    caption = data.get('caption')
    image_url = data.get('image_url')
    
    if image_url is None:
        return api_response(message="Image is required", status=400)
    
    try:
        post = Post(
            image_url=image_url,
            caption=caption,
            user_id=current_user.id
        )
        
        db.session.add(post)
        db.session.commit()
        
        return api_response(
            message="Create post successfully",
            data=post.to_dict(),
            status=201
        )
    except Exception as e:
        db.session.rollback()
        return api_response(message=f"Error creating post: {str(e)}", status=500)

@post_bp.route('/<int:post_id>', methods=['GET'])
@token_required
def get_post(current_user, post_id):
    """UC08: Get detail post by id"""
    post = Post.query.get(post_id)
    
    if not post or post.deleted:
        return api_response(message="Post not found", status=404)
    
    post_data = post.to_dict()
    
    return api_response(data=post_data)

@post_bp.route('/<int:post_id>', methods=['DELETE'])
@token_required
def delete_post(current_user, post_id):
    """UC09: Delete Own Post"""
    post = Post.query.get(post_id)
    
    if not post or post.deleted:
        return api_response(message="Post not found", status=404)
        
    if post.user_id != current_user.id:
        return api_response(message="Unauthorized to delete this post", status=403)
    
    try:
        post.deleted = True
        db.session.commit()
        return api_response(message="Post deleted successfully")
    except Exception as e:
        db.session.rollback()
        return api_response(message=f"Error deleting post: {str(e)}", status=500)
        
