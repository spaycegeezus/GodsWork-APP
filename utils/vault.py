import hashlib
from Crypto.Hash import keccak
from base64 import urlsafe_b64encode
from cryptography.fernet import Fernet

# this is vault.py

def keccak256(data: str) -> bytes:
    k = keccak.new(digest_bits=256)
    k.update(data.encode())
    return k.digest()

def derive_vault_key(passphrase: str, salt: str = "") -> bytes:
    key_material = keccak256(passphrase + salt)
    return urlsafe_b64encode(key_material[:32])
