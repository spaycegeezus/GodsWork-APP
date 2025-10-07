# This is security.py

import bcrypt
import hashlib
from cryptography.fernet import Fernet
from base64 import urlsafe_b64encode
import os

APP_SECRET = os.environ.get("GODS_APP_SECRET", "my-ultimate-secret")  # stored in env

def hash_password(password: str) -> str:
    """Return a bcrypt hash (salted)."""
    salt = bcrypt.gensalt()
    bcrypt_hash = bcrypt.hashpw(password.encode(), salt)
    return bcrypt_hash.decode()

def derive_key(username: str, pepper: str) -> bytes:
    """
    Derive a Fernet key from app secret + username + pepper.
    """
    key_material = f"{APP_SECRET}:{username}:{pepper}".encode()
    sha = hashlib.sha256(key_material).digest()
    return urlsafe_b64encode(sha[:32])  # Fernet expects 32-byte urlsafe base64

def encrypt_hash(bcrypt_hash: str, username: str, pepper: str) -> str:
    key = derive_key(username, pepper)
    f = Fernet(key)
    return f.encrypt(bcrypt_hash.encode()).decode()

def decrypt_hash(encrypted_hash: str, username: str, pepper: str) -> str:
    key = derive_key(username, pepper)
    f = Fernet(key)
    return f.decrypt(encrypted_hash.encode()).decode()

def verify_password(input_password: str, stored_encrypted_hash: str, username: str, pepper: str) -> bool:
    """
    stored_encrypted_hash: what you saved during signup (Fernet(bcrypt_hash)).
    Steps:
      1) decrypt → bcrypt hash
      2) bcrypt.checkpw(input_password, decrypted_hash)
    """
    try:
        decrypted_bcrypt_hash = decrypt_hash(stored_encrypted_hash, username, pepper)
        return bcrypt.checkpw(input_password.encode(), decrypted_bcrypt_hash.encode())
    except Exception:
        return False
