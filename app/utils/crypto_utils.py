# CRYPTO UTILITIES
import os
from cryptography.fernet import Fernet
from flask import current_app

def get_encryption_key():
    """Get encryption key from environment"""
    key = current_app.config.get('ENCRYPTION_KEY')
    if not key:
        # Generate a key for development (not recommended for production)
        key = Fernet.generate_key().decode()
        current_app.logger.warning("Using generated encryption key. Set ENCRYPTION_KEY in production!")
    
    if isinstance(key, str):
        key = key.encode()
    
    return key

def encrypt_token(token):
    """Encrypt token before storing in database"""
    if not token:
        return None
    
    try:
        key = get_encryption_key()
        f = Fernet(key)
        encrypted = f.encrypt(token.encode())
        return encrypted.decode()
    except Exception as e:
        current_app.logger.error(f"Token encryption failed: {str(e)}")
        raise

def decrypt_token(encrypted_token):
    """Decrypt stored token"""
    if not encrypted_token:
        return None
    
    try:
        key = get_encryption_key()
        f = Fernet(key)
        decrypted = f.decrypt(encrypted_token.encode())
        return decrypted.decode()
    except Exception as e:
        current_app.logger.error(f"Token decryption failed: {str(e)}")
        raise