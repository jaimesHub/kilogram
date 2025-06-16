# Google OAuth Setup Guide

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Project name: "Kilogram Social Auth" (or your preferred name)

## Step 2: Enable Google+ API

1. Go to "APIs & Services" > "Library"
2. Search for "Google+ API" 
3. Click "Enable"

## Step 3: Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. Application type: "Web application"
4. Name: "Kilogram Web Client"

### Authorized JavaScript origins:
- http://localhost:5000
- http://localhost:3000 (if you have frontend)
- https://your-domain.com (for production)

### Authorized redirect URIs:
- http://localhost:5000/api/auth/google/callback
- https://your-domain.com/api/auth/google/callback (for production)

## Step 4: Configure Environment Variables

Add to your .env file:
```
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
```

## Step 5: Test OAuth Flow

1. Start your Flask app: `python main.py`
2. Navigate to: http://localhost:5000/api/auth/google
3. Complete OAuth flow
4. Check logs for successful authentication

## Production Setup

For production, update:
- Authorized origins to your production domain
- Redirect URIs to production callback URLs
- Set production environment variables

## Security Notes

- Never commit CLIENT_SECRET to version control
- Use HTTPS in production
- Implement proper CSRF protection (handled by our implementation)
- Monitor OAuth usage in Google Cloud Console