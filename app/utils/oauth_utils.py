# OAUTH UTILITIES

import requests
from flask import current_app
from app.models.user import User
from app.models.social_account import SocialAccount
from app import db
from datetime import datetime

def get_google_user_info(access_token):
    """Fetch user info from Google OAuth API"""
    try:
        response = requests.get(
            'https://www.googleapis.com/oauth2/v2/userinfo',
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            current_app.logger.error(f"Google API error: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Google API request failed: {str(e)}")
        return None

def get_facebook_user_info(access_token):
    """Fetch user info from Facebook Graph API"""
    try:
        response = requests.get(
            'https://graph.facebook.com/me',
            params={
                'fields': 'id,name,email,picture.type(large)',
                'access_token': access_token
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            # Normalize Facebook response to match Google format
            normalized = {
                'id': data.get('id'),
                'name': data.get('name'),
                'email': data.get('email'),
                'picture': data.get('picture', {}).get('data', {}).get('url')
            }
            return normalized
        else:
            current_app.logger.error(f"Facebook API error: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Facebook API request failed: {str(e)}")
        return None

def generate_unique_username(base_username):
    """Generate unique username from base"""
    username = base_username.lower().replace(' ', '_')
    
    # Remove special characters
    import re
    username = re.sub(r'[^a-zA-Z0-9_]', '', username)
    
    # Ensure minimum length
    if len(username) < 3:
        username = 'user_' + username
    
    # Make unique
    original_username = username
    counter = 1
    
    while User.find_by_username(username):
        username = f"{original_username}{counter}"
        counter += 1
    
    return username

def find_or_create_user_from_social(provider, user_info, access_token):
    """
    Find existing user or create new one from social provider data
    Returns: (user, is_new_user, social_account)
    """
    provider_id = str(user_info.get('id'))
    email = user_info.get('email')
    name = user_info.get('name', '')
    
    # Check if social account already exists
    social_account = SocialAccount.find_by_provider_id(provider, provider_id)
    
    if social_account:
        # Update token and return existing user
        social_account.update_token(access_token)
        social_account.provider_email = email
        db.session.commit()
        return social_account.user, False, social_account
    
    # Check if user exists with same email
    existing_user = User.find_by_email(email) if email else None
    
    if existing_user:
        # Link social account to existing user
        social_account = SocialAccount(
            user_id=existing_user.id,
            provider=provider,
            provider_id=provider_id,
            provider_email=email,
            profile_data={'name': name, 'picture': user_info.get('picture')}
        )
        social_account.update_token(access_token)
        
        db.session.add(social_account)
        db.session.commit()
        
        return existing_user, False, social_account
    
    # Create new user
    if email:
        username = generate_unique_username(email.split('@')[0])
    else:
        username = generate_unique_username(name or 'user')
    
    new_user = User(
        username=username,
        email=email or f"{username}@{provider}.local",
        fullname=name or username,
        signup_method=provider,
        password_hash=None  # No password for social-only users
    )
    
    db.session.add(new_user)
    db.session.flush()  # Get user ID
    
    # Create social account
    social_account = SocialAccount(
        user_id=new_user.id,
        provider=provider,
        provider_id=provider_id,
        provider_email=email,
        profile_data={'name': name, 'picture': user_info.get('picture')}
    )
    social_account.update_token(access_token)
    
    db.session.add(social_account)
    db.session.commit()
    
    return new_user, True, social_account