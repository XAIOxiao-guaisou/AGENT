from cryptography.fernet import Fernet

class VortexCrypto:
    """
    Vortex Core Encryption Utilities.
    
    Provides secure encryption and decryption for user data.
    """
    
    def __init__(self, key: bytes = None):
        """
        Initialize crypto engine.
        :param key: Fernet key (bytes). Generates new if None.
        """
        self.key = key or Fernet.generate_key()
        self.cipher = Fernet(self.key)
    
    def encrypt(self, data: str) -> bytes:
        """
        Encrypt string data.
        :param data: Plaintext string
        :return: Encrypted bytes
        """
        return self.cipher.encrypt(data.encode())
    
    def decrypt(self, token: bytes) -> str:
        """
        Decrypt data.
        :param token: Encrypted bytes
        :return: Decrypted string
        """
        return self.cipher.decrypt(token).decode()
