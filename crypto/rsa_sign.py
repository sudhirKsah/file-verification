"""
crypto/rsa_sign.py
RSA key generation, signing, and verification
"""

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature


# ---- Key Generation ----

def generate_key_pair(key_size: int = 2048):
    """
    Create an RSA key pair (private and public).
    Returns: (private_key, public_key)
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    return private_key, public_key


def save_private_key(private_key, filepath: str):
    """Save a private key to a file in PEM format."""
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    with open(filepath, "wb") as f:
        f.write(pem)


def save_public_key(public_key, filepath: str):
    """Save a public key to a file in PEM format."""
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    with open(filepath, "wb") as f:
        f.write(pem)


def load_private_key(filepath: str):
    """Load a private key from a file."""
    with open(filepath, "rb") as f:
        return serialization.load_pem_private_key(
            f.read(), password=None, backend=default_backend()
        )


def load_public_key(filepath: str):
    """Load a public key from a file."""
    with open(filepath, "rb") as f:
        return serialization.load_pem_public_key(
            f.read(), backend=default_backend()
        )


# ---- Sign & Verify ----

def sign_hash(private_key, file_hash: str) -> bytes:
    """
    Sign a hash with a private key.
    Returns: Signature as bytes.
    """
    signature = private_key.sign(
        file_hash.encode("utf-8"),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature


def verify_signature(public_key, file_hash: str, signature: bytes) -> bool:
    """
    Verify a signature with a public key.
    Returns: True if valid; otherwise False.
    """
    try:
        public_key.verify(
            signature,
            file_hash.encode("utf-8"),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except InvalidSignature:
        return False
