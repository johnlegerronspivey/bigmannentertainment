"""
Encryption utilities for securing sensitive data
Uses Fernet symmetric encryption for OAuth tokens
"""
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

# Get encryption key from environment or generate one
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')

if not ENCRYPTION_KEY:
    # Generate a key from SECRET_KEY for consistency
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key-change-in-production')
    
    # Derive a Fernet key from SECRET_KEY
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b'social_media_encryption_salt',  # Static salt for deterministic key
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(SECRET_KEY.encode()))
    ENCRYPTION_KEY = key.decode()

fernet = Fernet(ENCRYPTION_KEY.encode())

def encrypt_token(token: str) -> str:
    """Encrypt a token for secure storage"""
    if not token:
        return None
    encrypted = fernet.encrypt(token.encode())
    return encrypted.decode()

def decrypt_token(encrypted_token: str) -> str:
    """Decrypt a token from storage"""
    if not encrypted_token:
        return None
    try:
        decrypted = fernet.decrypt(encrypted_token.encode())
        return decrypted.decode()
    except Exception as e:
        print(f"⚠️ Failed to decrypt token: {e}")
        return None

def verify_encryption():
    """Verify encryption/decryption is working"""
    test_token = "test_access_token_12345"
    encrypted = encrypt_token(test_token)
    decrypted = decrypt_token(encrypted)
    return decrypted == test_token

# Test on import
if __name__ == "__main__":
    if verify_encryption():
        print("✅ Encryption utilities working correctly")
    else:
        print("❌ Encryption verification failed")
