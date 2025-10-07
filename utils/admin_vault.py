from cryptography.fernet import Fernet
from .vault import derive_vault_key

# this is admin_vault.py

class AdminVault:
    def __init__(self):
        self.layer_keys = {}

    def unlock_layer(self, tier: int, passphrase: str, salt: str = ""):
        key = derive_vault_key(passphrase, salt)
        self.layer_keys[tier] = Fernet(key)
        return True

    def decrypt_layer(self, tier: int, encrypted_data: str) -> str:
        if tier not in self.layer_keys:
            raise PermissionError(f"Layer {tier} is locked.")
        return self.layer_keys[tier].decrypt(encrypted_data.encode()).decode()

    def encrypt_layer(self, tier: int, data: str) -> str:
        if tier not in self.layer_keys:
            raise PermissionError(f"Layer {tier} is locked.")
        return self.layer_keys[tier].encrypt(data.encode()).decode()
