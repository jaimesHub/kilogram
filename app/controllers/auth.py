from flask import Blueprint, request, jsonify, url_for, redirect, session, current_app, render_template_string
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import traceback

from app.utils import api_response, token_required
from app.models.user import User
from app.models.social_account import SocialAccount
from app import db
from app._utils.oauth_helpers import GoogleOAuthService, find_or_create_user_from_google, OAuthError

auth_bp = Blueprint('auth', __name__)

#Success page template (inline for simplicity)
SUCCESS_PAGE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OAuth Success - Kilogram</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; justify-content: center; align-items: center; }
        .container { background: white; padding: 40px; border-radius: 12px; box-shadow: 0 8px 32px rgba(0,0,0,0.1); max-width: 600px; width: 100%; text-align: center; }
        .success-icon { font-size: 64px; color: #28a745; margin-bottom: 20px; }
        .title { font-size: 28px; font-weight: 600; color: #333; margin-bottom: 16px; }
        .user-info { background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; text-align: left; }
        .jwt-token { background: #f8f9fa; border: 1px solid #ddd; border-radius: 4px; padding: 15px; margin: 20px 0; font-family: 'Courier New', monospace; font-size: 14px; word-break: break-all; color: #333; }
        .copy-btn { background: #007bff; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; font-size: 14px; margin-top: 10px; }
        .info-item { margin: 8px 0; padding: 4px 0; border-bottom: 1px solid #eee; }
        .info-label { font-weight: 600; color: #555; display: inline-block; width: 120px; }
        .badge { display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 600; }
        .badge-new { background: #d4edda; color: #155724; }
        .badge-existing { background: #cce7ff; color: #004085; }
        .api-info { background: #e7f3ff; border-left: 4px solid #007bff; padding: 15px; margin: 20px 0; text-align: left; }
    </style>
</head>
<body>
    <div class="container">
        <div class="success-icon">✅</div>
        <h1 class="title">OAuth Authentication Successful!</h1>
        <p>
            {% if is_new_user %}
                Welcome to Kilogram! Your account has been created. 
                <span class="badge badge-new">NEW USER</span>
            {% else %}
                Welcome back! You've been logged in successfully.
                <span class="badge badge-existing">EXISTING USER</span>
            {% endif %}
        </p>

        <div class="user-info">
            <h3>👤 User Information</h3>
            <div class="info-item"><span class="info-label">ID:</span> {{ user.id }}</div>
            <div class="info-item"><span class="info-label">Username:</span> {{ user.username }}</div>
            <div class="info-item"><span class="info-label">Email:</span> {{ user.email }}</div>
            <div class="info-item"><span class="info-label">Name:</span> {{ user.fullname or 'Not provided' }}</div>
            <div class="info-item"><span class="info-label">Signup Method:</span> {{ user.signup_method }}</div>
            <div class="info-item"><span class="info-label">Provider:</span> {{ provider }}</div>
        </div>

        <div class="api-info">
            <h3>🔑 JWT Access Token</h3>
            <p>Use this token for API authentication:</p>
            <div class="jwt-token" id="jwtToken">{{ access_token }}</div>
            <button class="copy-btn" onclick="copyToken()">📋 Copy Token</button>
        </div>

        <div class="api-info">
            <h3>🧪 API Testing Examples</h3>
            <pre style="background: #f1f1f1; padding: 10px; border-radius: 4px; font-size: 12px; text-align: left;">
# Get user profile
curl -H "Authorization: Bearer YOUR_TOKEN" {{ base_url }}/api/users/profile

# Get social accounts  
curl -H "Authorization: Bearer YOUR_TOKEN" {{ base_url }}/api/auth/social/accounts

# Test protected endpoint
curl -H "Authorization: Bearer YOUR_TOKEN" {{ base_url }}/api/posts/newsfeed</pre>
        </div>
    </div>

    <script>
        function copyToken() {
            const tokenElement = document.getElementById('jwtToken');
            navigator.clipboard.writeText(tokenElement.textContent).then(() => {
                const button = document.querySelector('.copy-btn');
                button.textContent = '✅ Copied!';
                button.style.background = '#28a745';
                setTimeout(() => {
                    button.textContent = '📋 Copy Token';
                    button.style.background = '#007bff';
                }, 2000);
            });
        }
    </script>
</body>
</html>
"""

ERROR_PAGE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OAuth Error - Kilogram</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%); min-height: 100vh; display: flex; justify-content: center; align-items: center; }
        .container { background: white; padding: 40px; border-radius: 12px; box-shadow: 0 8px 32px rgba(0,0,0,0.1); max-width: 500px; width: 100%; text-align: center; }
        .error-icon { font-size: 64px; color: #dc3545; margin-bottom: 20px; }
        .title { font-size: 28px; font-weight: 600; color: #333; margin-bottom: 16px; }
        .error-message { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; padding: 15px; border-radius: 8px; margin: 20px 0; }
        .retry-btn { background: #007bff; color: white; border: none; padding: 12px 24px; border-radius: 6px; cursor: pointer; font-size: 16px; text-decoration: none; display: inline-block; margin: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="error-icon">❌</div>
        <h1 class="title">OAuth Authentication Failed</h1>
        <div class="error-message"><strong>Error:</strong> {{ error_message }}</div>
        <a href="{{ base_url }}/api/auth/google" class="retry-btn">🔄 Try Again</a>
    </div>
</body>
</html>
"""

@auth_bp.route('/register', methods=['POST'])
def register():
    """UC01: Register a new user account."""
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    fullname = data.get('fullname')
    email = data.get('email')

    # Validate username, password, and email
    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters long'}), 400
    if '@' not in email:
        return jsonify({'error': 'Invalid email format'}), 400
        
    # Check username & password already existed or not
    if User.query.filter_by(username=data['username']).first():
        return api_response(message="Username already exists", status=400)

    if User.query.filter_by(email=data['email']).first():
        return api_response(message="Email already exists", status=400)

    # Basic user profile
    try:
        user = User(
            username=data['username'],
            email=data['email'],
            fullname=data['fullname'],
        )

        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()

        # 🔧 FIX: Convert user.id to string
        access_token = create_access_token(
            identity=str(user.id),  # ✅ Convert to string
            additional_claims={
                'user_id': user.id,
                'username': user.username,
                'email': user.email
            }
        )
        
        return api_response(
            message="User registered successfully",
            data={"user_id": user.id, "username": user.username},
            status=201
        )
    except Exception as e:
        db.session.rollback()
        return api_response(message=f"Error registering user: {str(e)}", status=500)

@auth_bp.route('/login', methods=['POST'])
def login():
    """UC02: Log in to an existing user account."""
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=data['username']).first()
    if not user or not user.check_password(data['password']):
        return api_response(message="Username or password is incorrect", status=401)
        
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    # 🔧 FIX: Convert user.id to string
    access_token = create_access_token(
            identity=str(user.id),  # ✅ Convert to string
            additional_claims={
                'user_id': user.id,
                'username': user.username,
                'email': user.email
            }
        )

    return api_response(
        message='Login successful',
        data={
            'access_token': access_token,
            'refresh_token': refresh_token,
            "user": user.to_dict()
        })

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """UC03: Log out of the current user account."""

@auth_bp.route('/me', methods=['GET'])
@token_required
def view_own_profile(current_user):
    """UC04: View own profile"""
    return api_response(data=current_user.to_dict())

# ADD GOOGLE OAUTH ENDPOINTS
@auth_bp.route('/google', methods=['GET'])
def google_login():
    """Initiate Google OAuth flow"""
    try:
        # Generate authorization URL
        auth_url = GoogleOAuthService.get_authorization_url()
        
        current_app.logger.info("✅ Google OAuth flow initiated")
        
        # Return redirect URL for API clients or redirect directly
        if request.headers.get('Accept') == 'application/json':
            return jsonify({
                'authorization_url': auth_url,
                'message': 'Redirect to this URL to complete Google OAuth'
            }), 200
        else:
            # Direct redirect for browser clients
            return redirect(auth_url)
            
    except OAuthError as e:
        current_app.logger.error(f"❌ Google OAuth initiation failed: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"❌ Unexpected error in Google OAuth: {str(e)}")
        return jsonify({'error': 'OAuth service temporarily unavailable'}), 500

@auth_bp.route('/google/callback', methods=['GET'])
def google_callback():
    """Handle Google OAuth callback with success page for testing"""
    try:
        # Get authorization code and state from callback
        authorization_code = request.args.get('code')
        state = request.args.get('state')
        error = request.args.get('error')

        # Get base URL for templates
        base_url = GoogleOAuthService.get_current_base_url()
        
        # Handle OAuth errors
        if error:
            error_description = request.args.get('error_description', 'Unknown OAuth error')
            current_app.logger.warning(f"Google OAuth error: {error} - {error_description}")
            
            error_msg = 'Google OAuth access was denied by user' if error == 'access_denied' else f'Google OAuth error: {error_description}'
            
            # Return error page instead of JSON for better testing experience
            return render_template_string(ERROR_PAGE_TEMPLATE, 
                                        error_message=error_msg,
                                        base_url=base_url), 400
        
        if not authorization_code:
            return render_template_string(ERROR_PAGE_TEMPLATE, 
                                        error_message='Authorization code not received from Google',
                                        base_url=base_url), 400
        
        if not state:
            return render_template_string(ERROR_PAGE_TEMPLATE, 
                                        error_message='State parameter missing - security error',
                                        base_url=base_url), 400
        
        # Exchange code for token
        token_data = GoogleOAuthService.exchange_code_for_token(authorization_code, state)
        
        # Get user information
        user_info = GoogleOAuthService.get_user_info(token_data['access_token'])

        # Find or create user
        user, is_new_user, social_account = find_or_create_user_from_google(user_info, token_data)

        print(">>> user: ", user)
        
        # Generate JWT token for our application
        jwt_token = create_access_token(
            identity=str(user.id),  # ✅ Convert to string
            additional_claims={
                'user_id': user.id,     # Keep integer version for convenience
                'username': user.username,
                'email': user.email,
                'provider': 'google'
            }
        )

        # Log successful authentication
        action = "registered" if is_new_user else "logged in"
        current_app.logger.info(f"User {user.username} {action} via Google OAuth")
        
        # Check if request wants JSON response (for API testing)
        if request.headers.get('Accept') == 'application/json':
            response_data = {
                'access_token': jwt_token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'fullname': user.fullname,
                    'profile_picture': user.profile_picture,
                    'signup_method': user.signup_method,
                    'bio': user.bio
                },
                'is_new_user': is_new_user,
                'provider': 'google',
                'message': 'Google OAuth login successful'
            }
            return jsonify(response_data), 200
        
        # Return success page for browser-based testing
        return render_template_string(SUCCESS_PAGE_TEMPLATE, 
                                    access_token=jwt_token,
                                    user=user,
                                    is_new_user=is_new_user,
                                    provider='google',
                                    base_url=base_url), 200
        
    except OAuthError as e:
        current_app.logger.error(f"❌ Google OAuth callback error: {str(e)}")
        base_url = GoogleOAuthService.get_current_base_url()

        if request.headers.get('Accept') == 'application/json':
            return jsonify({'error': str(e)}), 400

        return render_template_string(ERROR_PAGE_TEMPLATE, 
                                    error_message=str(e),
                                    base_url=base_url), 400
    except Exception as e:
        current_app.logger.error(f"Unexpected error in Google OAuth callback: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        base_url = GoogleOAuthService.get_current_base_url()
        
        if request.headers.get('Accept') == 'application/json':
            return jsonify({'error': 'Authentication failed due to server error'}), 500
        
        return render_template_string(ERROR_PAGE_TEMPLATE, 
                                    error_message='Authentication failed due to server error',
                                    base_url=base_url), 500

@auth_bp.route('/test-page', methods=['GET'])
def test_page():
    """Simple test page to verify OAuth setup"""
    
    base_url = GoogleOAuthService.get_current_base_url()
    
    test_page_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Kilogram OAuth Test</title>
        <style>
            body {{ font-family: Arial, sans-serif; padding: 40px; text-align: center; }}
            .test-btn {{ background: #4285f4; color: white; padding: 15px 30px; border: none; border-radius: 8px; font-size: 16px; cursor: pointer; margin: 10px; text-decoration: none; display: inline-block; }}
            .test-btn:hover {{ background: #357ae8; }}
            .info {{ background: #f0f8ff; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <h1>🧪 Kilogram OAuth Testing</h1>
        <p>Test your Google OAuth integration</p>
        
        <div class="info">
            <h3>Current Environment</h3>
            <p><strong>Base URL:</strong> {base_url}</p>
            <p><strong>OAuth Callback:</strong> {base_url}/api/auth/google/callback</p>
        </div>
        
        <a href="{base_url}/api/auth/google" class="test-btn">
            🔐 Sign in with Google
        </a>
        
        <a href="{base_url}/api/auth/social/accounts" class="test-btn">
            📋 View Social Accounts (Requires Auth)
        </a>
        
        <div class="info">
            <h3>📖 Testing Notes</h3>
            <ul style="text-align: left; max-width: 500px; margin: 0 auto;">
                <li>Click "Sign in with Google" to test OAuth flow</li>
                <li>After success, you'll get a JWT token</li>
                <li>Copy the token to test protected API endpoints</li>
                <li>Use <code>curl</code> or Postman for API testing</li>
            </ul>
        </div>
    </body>
    </html>
    """
    
    return test_page_html

@auth_bp.route('/google/link', methods=['POST'])
@jwt_required()
def link_google_account():
    """Link Google account to existing authenticated user"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        google_access_token = data.get('access_token')
        
        if not google_access_token:
            return jsonify({'error': 'Google access token required'}), 400
        
        # Get user info from Google
        user_info = GoogleOAuthService.get_user_info(google_access_token)
        provider_id = user_info['id']
        
        # Check if this Google account is already linked to another user
        existing_social = SocialAccount.find_by_provider_id('google', provider_id)
        
        if existing_social:
            if existing_social.user_id == user_id:
                return jsonify({
                    'message': 'Google account is already linked to your account',
                    'provider': 'google'
                }), 200
            else:
                return jsonify({
                    'error': 'This Google account is already linked to another user'
                }), 400
        
        # Check if user already has a Google account linked
        user_google_account = SocialAccount.find_by_user_and_provider(user_id, 'google')
        
        if user_google_account:
            return jsonify({
                'error': 'Your account already has a Google account linked'
            }), 400
        
        # Create new social account link
        social_account = SocialAccount(
            user_id=user_id,
            provider='google',
            provider_id=provider_id,
            provider_email=user_info['email'],
            profile_data=user_info
        )
        
        social_account.update_token(google_access_token)
        
        db.session.add(social_account)
        db.session.commit()
        
        current_app.logger.info(f"✅ User {user.username} linked Google account")
        
        return jsonify({
            'message': 'Google account linked successfully',
            'provider': 'google',
            'provider_email': user_info['email']
        }), 200
        
    except OAuthError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"❌ Error linking Google account: {str(e)}")
        return jsonify({'error': 'Failed to link Google account'}), 500

@auth_bp.route('/google/unlink', methods=['DELETE'])
@jwt_required()
def unlink_google_account():
    """Unlink Google account from user"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Find Google social account
        google_account = SocialAccount.find_by_user_and_provider(user_id, 'google')
        
        if not google_account:
            return jsonify({'error': 'No Google account linked to your profile'}), 404
        
        # Check if user has password or other social accounts
        other_social_accounts = SocialAccount.query.filter(
            SocialAccount.user_id == user_id,
            SocialAccount.provider != 'google'
        ).count()
        
        if not user.has_password() and other_social_accounts == 0:
            return jsonify({
                'error': 'Cannot unlink your only authentication method. Please set a password first.',
                'action_required': 'set_password'
            }), 400
        
        # Remove social account
        db.session.delete(google_account)
        db.session.commit()
        
        current_app.logger.info(f"User {user.username} unlinked Google account")
        
        return jsonify({
            'message': 'Google account unlinked successfully',
            'provider': 'google'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error unlinking Google account: {str(e)}")
        return jsonify({'error': 'Failed to unlink Google account'}), 500

@auth_bp.route('/social/accounts', methods=['GET'])
@jwt_required()
def get_social_accounts():
    """Get user's linked social accounts"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        social_accounts = SocialAccount.query.filter_by(user_id=user_id).all()
        
        accounts_data = []
        for account in social_accounts:
            accounts_data.append({
                'provider': account.provider,
                'provider_email': account.provider_email,
                'linked_at': datetime.fromtimestamp(account.created_at).isoformat() + 'Z',
                'has_valid_token': bool(account.access_token)
            })
        
        return jsonify({
            'social_accounts': accounts_data,
            'has_password': user.has_password(),
            'signup_method': user.signup_method,
            'can_unlink_all': user.has_password()  # Can unlink all social accounts if has password
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching social accounts: {str(e)}")
        return jsonify({'error': 'Failed to fetch social accounts'}), 500