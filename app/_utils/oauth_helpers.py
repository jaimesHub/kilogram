# ENHANCED OAUTH UTILITIES (oauth_utils.py)

import requests
import secrets
import hashlib
import time
from urllib.parse import urlencode, parse_qs, urlparse
from flask import current_app, session, request, url_for
from app.models.user import User
from app.models.social_account import SocialAccount
from app._utils.crypto_utils import encrypt_token
from app import db
from datetime import datetime

class OAuthError(Exception):
    """Custom OAuth error for better error handling"""
    pass

class GoogleOAuthService:
    """Service class for Google OAuth operations"""

    @staticmethod
    def get_current_base_url():
        """Get current base URL dynamically"""
        # Get the actual URL user is accessing from
        if request.headers.get('X-Forwarded-Host'):
            # For proxied environments like Firebase Cloud Workstation
            scheme = request.headers.get('X-Forwarded-Proto', 'https')
            host = request.headers.get('X-Forwarded-Host')
            return f"{scheme}://{host}"
        elif request.headers.get('Host'):
            # Standard host header
            scheme = 'https' if request.is_secure else 'http'
            host = request.headers.get('Host')
            return f"{scheme}://{host}"
        else:
            # Fallback to config
            return current_app.config.get('OAUTH_REDIRECT_URI', 'http://localhost:5000')
    
    @staticmethod
    def generate_state():
        """Generate secure state parameter for CSRF protection"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def verify_state(received_state):
        """Verify state parameter against session"""
        stored_state = session.get('oauth_state')
        if not stored_state or stored_state != received_state:
            raise OAuthError("Invalid state parameter - CSRF protection failed")
        
        # Clear state from session after verification
        session.pop('oauth_state', None)
        return True

    @staticmethod
    def get_authorization_url():
        """Generate Google OAuth authorization URL with dynamic redirect_uri"""
        try:
            google = current_app.oauth_clients['google']
            
            # Generate and store state for CSRF protection
            state = GoogleOAuthService.generate_state()
            session['oauth_state'] = state
            
            # Get dynamic base URL
            base_url = GoogleOAuthService.get_current_base_url()
            redirect_uri = f"{base_url}/api/auth/google/callback"
            
            current_app.logger.info(f"OAuth redirect_uri: {redirect_uri}")
            
            # Generate authorization URL with dynamic redirect_uri
            authorization_url = google.create_authorization_url(
                redirect_uri=redirect_uri,
                state=state,
                access_type='offline',  # Get refresh token
                prompt='select_account'  # Force account selection
            )
            
            return authorization_url['url']
            
        except Exception as e:
            current_app.logger.error(f"Failed to generate Google auth URL: {str(e)}")
            raise OAuthError("Failed to initialize Google OAuth")

    @staticmethod
    def exchange_code_for_token(authorization_code, state):
        """Exchange authorization code for access token with dynamic redirect_uri"""
        try:
            # Verify state parameter
            GoogleOAuthService.verify_state(state)
            
            google = current_app.oauth_clients['google']
            
            # Use same dynamic redirect_uri as in authorization
            base_url = GoogleOAuthService.get_current_base_url()
            redirect_uri = f"{base_url}/api/auth/google/callback"
            
            current_app.logger.info(f"Token exchange redirect_uri: {redirect_uri}")
            
            # Exchange code for token
            token = google.fetch_access_token(
                code=authorization_code,
                redirect_uri=redirect_uri
            )
            
            if not token or 'access_token' not in token:
                raise OAuthError("Failed to obtain access token from Google")
            
            return token
            
        except OAuthError:
            raise
        except Exception as e:
            current_app.logger.error(f"Token exchange failed: {str(e)}")
            raise OAuthError("Failed to exchange authorization code for token")
    
    @staticmethod
    def get_user_info(access_token):
        """Fetch user information from Google"""
        try:
            headers = {'Authorization': f'Bearer {access_token}'}
            
            # Get user info from Google userinfo endpoint
            response = requests.get(
                'https://www.googleapis.com/oauth2/v2/userinfo',
                headers=headers,
                timeout=10
            )
            
            if response.status_code != 200:
                current_app.logger.error(f"Google userinfo API error: {response.status_code} - {response.text}")
                raise OAuthError("Failed to fetch user information from Google")
            
            user_data = response.json()
            
            # Validate required fields
            if not user_data.get('id') or not user_data.get('email'):
                raise OAuthError("Incomplete user data from Google")
            
            # Normalize user data
            normalized_data = {
                'id': str(user_data['id']),
                'email': user_data.get('email'),
                'name': user_data.get('name', ''),
                'given_name': user_data.get('given_name', ''),
                'family_name': user_data.get('family_name', ''),
                'picture': user_data.get('picture'),
                'verified_email': user_data.get('verified_email', False)
            }
            
            return normalized_data
            
        except OAuthError:
            raise
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Network error fetching Google user info: {str(e)}")
            raise OAuthError("Network error while fetching user information")
        except Exception as e:
            current_app.logger.error(f"Unexpected error fetching Google user info: {str(e)}")
            raise OAuthError("Failed to process user information from Google")

def find_or_create_user_from_google(user_info, token_data):
    """
    Find existing user or create new one from Google OAuth data
    Returns: (user, is_new_user, social_account)
    """
    provider_id = user_info['id']
    email = user_info['email']
    name = user_info['name']
    
    try:
        # Check if social account already exists
        social_account = SocialAccount.find_by_provider_id('google', provider_id)
        
        if social_account:
            # Update existing social account with new token
            social_account.update_token(
                access_token=token_data['access_token'],
                refresh_token=token_data.get('refresh_token'),
                expires_at=int(time.time()) + token_data.get('expires_in', 3600)
            )
            social_account.provider_email = email
            social_account.profile_data = user_info
            db.session.commit()
            
            current_app.logger.info(f"Updated existing Google account for user {social_account.user.username}")
            return social_account.user, False, social_account
        
        # Check if user exists with same email
        existing_user = User.find_by_email(email)
        
        if existing_user:
            # Link Google account to existing user
            social_account = SocialAccount(
                user_id=existing_user.id,
                provider='google',
                provider_id=provider_id,
                provider_email=email,
                profile_data=user_info
            )
            
            social_account.update_token(
                access_token=token_data['access_token'],
                refresh_token=token_data.get('refresh_token'),
                expires_at=int(time.time()) + token_data.get('expires_in', 3600)
            )
            
            db.session.add(social_account)
            db.session.commit()
            
            current_app.logger.info(f"Linked Google account to existing user {existing_user.username}")
            return existing_user, False, social_account
        
        # Create new user from Google data
        username = generate_username_from_google_data(user_info)
        
        new_user = User(
            username=username,
            email=email,
            fullname=name or username,
            signup_method='google',
            password_hash=None,  # No password for Google-only users
            profile_picture=user_info.get('picture', 'default.jpg')
        )
        
        db.session.add(new_user)
        db.session.flush()  # Get user ID
        
        # Create social account
        social_account = SocialAccount(
            user_id=new_user.id,
            provider='google',
            provider_id=provider_id,
            provider_email=email,
            profile_data=user_info
        )
        
        social_account.update_token(
            access_token=token_data['access_token'],
            refresh_token=token_data.get('refresh_token'),
            expires_at=int(time.time()) + token_data.get('expires_in', 3600)
        )
        
        db.session.add(social_account)
        db.session.commit()
        
        current_app.logger.info(f"Created new user {username} from Google OAuth")
        return new_user, True, social_account
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating/finding user from Google data: {str(e)}")
        raise OAuthError("Failed to create or link user account")

def generate_username_from_google_data(user_info):
    """Generate unique username from Google user data"""
    email = user_info.get('email', '')
    name = user_info.get('name', '')
    given_name = user_info.get('given_name', '')
    
    # Try different strategies for username generation
    candidates = []
    
    if email:
        candidates.append(email.split('@')[0])
    
    if given_name:
        candidates.append(given_name.lower())
    
    if name:
        # Clean name for username
        clean_name = ''.join(c for c in name.lower() if c.isalnum() or c in '_')
        candidates.append(clean_name)
    
    # Fallback
    candidates.append('google_user')
    
    # Find unique username
    for base_username in candidates:
        username = base_username[:30]  # Limit length
        if len(username) < 3:
            username = f"user_{username}"
        
        # Make unique
        final_username = username
        counter = 1
        
        while User.find_by_username(final_username):
            final_username = f"{username}{counter}"
            counter += 1
            
            # Prevent infinite loop
            if counter > 9999:
                final_username = f"user_{int(time.time())}"
                break
        
        return final_username
    
    # Final fallback
    return f"user_{int(time.time())}"