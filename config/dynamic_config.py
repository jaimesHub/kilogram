import os
from urllib.parse import urlparse

def get_dynamic_oauth_config():
    """Get OAuth configuration based on environment"""
    
    # Try to detect environment
    if os.environ.get('GOOGLE_CLOUD_PROJECT'):
        # Running on Google Cloud
        base_url = os.environ.get('OAUTH_REDIRECT_URI')
        if not base_url:
            # Auto-detect from Cloud Run or other Google Cloud services
            service_url = os.environ.get('K_SERVICE', '')
            if 'firebase' in service_url or 'cloudworkstations' in service_url:
                # This is Firebase Cloud Workstation
                base_url = os.environ.get('OAUTH_REDIRECT_URI')
    else:
        # Local development
        base_url = os.environ.get('OAUTH_REDIRECT_URI', 'http://localhost:5000')
    
    return {
        'base_url': base_url,
        'redirect_uri': f"{base_url}/api/auth/google/callback",
        'frontend_url': os.environ.get('FRONTEND_URL', base_url)
    }
