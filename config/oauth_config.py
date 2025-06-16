import os
from authlib.integrations.flask_client import OAuth
from flask import current_app

def init_oauth(app):
    """Initialize OAuth providers"""
    oauth = OAuth(app)
    
    # Google OAuth Configuration
    google = oauth.register(
        name='google',
        client_id=os.environ.get('GOOGLE_CLIENT_ID'),
        client_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile',
            'redirect_uri': None  # Will be set dynamically
        }
    )
    
    # Store OAuth clients in app for easy access
    app.oauth_clients = {
        'google': google
    }
    
    return oauth, google