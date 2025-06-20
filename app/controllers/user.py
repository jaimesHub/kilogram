# import cProfile
# import pstats
# import io # Working with stream in memory

from flask import Blueprint, request

from app.utils import api_response, token_required
from app import db
from app.models.user import User
from app.models.post import Post
from app.models.follow import Follow

import cProfile
import pstats
import io

user_bp = Blueprint('user', __name__)

@user_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    """UC04: Get the profile of the current user."""

    # Get the username from the JWT token
    return api_response(data=current_user.to_dict())

    # # --- Start Profiling ---
    # profiler = cProfile.Profile()
    # profiler.enable()

    # response_data = current_user.to_dict(viewer=current_user)

    # # --- End Profiling ---
    # profiler.disable()

    # # --- Save and display the profiling's result ---
    # # Creating a stream in memory for saving the output of pstats
    # s = io.StringIO()
    
    # # Organizing by cumulative time
    # ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
    # ps.print_stats() # Print the stream

    # # Print profiling's result to the console of server Flask for observing
    # # Or we can save as a file:
    # # with open('profile_results.prof', 'w') as f:
    # #     f.write(s.getvalue())
    # print("---------------- PROFILING RESULTS FOR /api/user/profile ----------------")
    # print(s.getvalue())
    # print("-------------------------------------------------------------------------")
    
    # return api_response(data=response_data)

    # # Initializing the profiler
    # pr = cProfile.Profile()
    # pr.enable()  # Start collecting data

    # # --- Main Logic Of API ---
    # response = api_response(data=current_user.to_dict(viewer=current_user))
    # # --- End of main logic ---

    # pr.disable()  # Stop collecting data

    # # Saving profiling's result as a file .prof
    # s = io.StringIO()
    # sortby = 'cumulative' # Ordering by cumulative time (thời gian tích lũy)
    # ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    # ps.dump_stats(filename='profile_get_profile.prof') # Save file

    # # You can print the console for briefly checking, but SnakeViz will be more visualized
    # # print(s.getvalue()) 
    
    # return response


@user_bp.route('/profile', methods=['PUT'])
@token_required
def edit_profile(current_user):
    """UC05: Edit Own Profile."""
    data = request.get_json() or {}
    allowed_fields = ['fullname', 'email', 'username', 'bio']
    fields_to_update = {k: v for k, v in data.items() if k in allowed_fields and v}

    # If no fields to update, return error
    if not fields_to_update:
        return api_response(message="No fields to update", status=400)

    # Check if username or email already exists
    if 'username' in fields_to_update and fields_to_update['username'] != current_user.username:
        if User.query.filter_by(username=fields_to_update['username']).first():
            return api_response(message="Username already exists", status=400)

    if 'email' in fields_to_update and fields_to_update['email'] != current_user.email:
        if User.query.filter_by(email=fields_to_update['email']).first():
            return api_response(message="Email already exists", status=400)

    # Updating information
    for key, value in fields_to_update.items():
        setattr(current_user, key, value)

    try:
        db.session.commit()
        return api_response(message="Update profile successfully", data=current_user.to_dict())
    except Exception as e:
        db.session.rollback()
        return api_response(message=f"Error updating profile: {str(e)}", status=500)

@user_bp.route('/<int:user_id>/profile', methods=['GET'])
@token_required
def view_other_profile(current_user, user_id):
    """UC06: View Other User's Profile"""
    print(f'user_id: {user_id} - type: {type(user_id)}')
    user = User.query.get(user_id)
    
    if not user:
        return api_response(message="User not found", status=404)

    return api_response(data=user.to_dict(viewer=current_user))

@user_bp.route('/<int:user_id>/posts', methods=['GET'])
@token_required
def get_user_posts(current_user, user_id):
    """UC10: Get posts of the current user with pagination."""
    
    # Get pagination parameters from query string
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Get posts from database with pagination
    posts = Post.query.filter_by(user_id=user_id, deleted=False)\
        .order_by(Post.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    # Prepare response data
    response_data = {
        'items': [post.to_dict(include_author=True, include_likes=True, current_user=current_user) for post in posts.items],
        'pagination': {
            'page': posts.page,
            'per_page': posts.per_page,
            'total': posts.total,
            'pages': posts.pages
        }
    }
    
    return api_response(data=response_data)

@user_bp.route('/<int:user_id>/follow', methods=['POST'])
@token_required
def follow_user(current_user, user_id):
    """UC11: Follow another user."""
    # Cannot follow self
    if current_user.id == user_id:
        return api_response(message="Cannot follow yourself", status=400)

    # Check target exists
    target_user = User.query.get(user_id)
    if not target_user:
        return api_response(message="User does not exist", status=404)

    # Check existing follow
    existing = Follow.query.filter_by(follower_id=current_user.id, following_id=user_id).first()
    if existing:
        return api_response(message="Already following this user", status=400)

    # Create follow relationship
    try:
        follow = Follow(follower_id=current_user.id, following_id=user_id)
        db.session.add(follow)
        db.session.commit()
        return api_response(message="User followed successfully")
    except Exception as e:
        db.session.rollback()
        return api_response(message=f"Error following user: {str(e)}", status=500)

@user_bp.route('/<int:user_id>/follow', methods=['DELETE'])
@token_required
def unfollow_user(current_user, user_id):
    """UC12: Unfollow User."""
    # Cannot unfollow self
    if current_user.id == user_id:
        return api_response(message="Cannot unfollow yourself", status=400)
  
    # Check target exists
    target_user = User.query.get(user_id)
    if not target_user:
        return api_response(message="User does not exist", status=404)
  
    # Check existing follow relationship
    existing = Follow.query.filter_by(follower_id=current_user.id, following_id=user_id).first()
    if not existing:
        return api_response(message="Not following this user", status=400)
  
    # Remove follow relationship
    try:
        db.session.delete(existing)
        db.session.commit()
        return api_response(message="User unfollowed successfully")
    except Exception as e:
        db.session.rollback()
        return api_response(message=f"Error unfollowing user: {str(e)}", status=500)

@user_bp.route('/search', methods=['GET'])
@token_required
def search_users(current_user):
    """UC16: Search Users by Username"""
    username = request.args.get('username', '', type=str)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    if not username:
        return api_response(message="Username is required", status=400)

    # users = User.query.filter_by(username=username)\
    #     .order_by(User.created_at.desc())\
    #     .paginate(page=page, per_page=per_page, error_out=False)

    users = User.query.filter(User.username.ilike(f'%{username}%'))\
        .order_by(User.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)

    if not users.items:
        return api_response(message="No users found", status=404)

    response_data = {
        'items': [user.to_dict() for user in users.items],
        'pagination': {
            'page': users.page,
            'per_page': users.per_page,
            'total': users.total,
            'pages': users.pages
        }
    }

    return api_response(data=response_data, status=200)

# TODO: Text search:: https://develie.hashnode.dev/exploring-flask-sqlalchemy-queries 
  
