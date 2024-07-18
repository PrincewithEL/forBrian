from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend
import os

def generate_key(otp: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return kdf.derive(otp.encode())

def encrypt_message(message: str, key: bytes) -> (bytes, bytes):
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    encrypted_message = aesgcm.encrypt(nonce, message.encode(), None)
    return nonce, encrypted_message

def decrypt_message(encrypted_message: bytes, key: bytes, nonce: bytes) -> str:
    aesgcm = AESGCM(key)
    decrypted_message = aesgcm.decrypt(nonce, encrypted_message, None)
    return decrypted_message.decode()