"""
crypto/hash.py
SHA-256 hashing for file integrity verification
"""

import hashlib
import os


def hash_file(filepath: str) -> str:
    """
    Calculate the SHA-256 hash of a file.
    Read the file in chunks to support large files.

    Returns: Hexadecimal hash string.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def hash_bytes(data: bytes) -> str:
    """Calculate a SHA-256 hash directly from bytes."""
    return hashlib.sha256(data).hexdigest()


def hash_string(text: str) -> str:
    """Calculate a SHA-256 hash from a string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def verify_file_hash(filepath: str, expected_hash: str) -> bool:
    """
    Check whether a file hash matches the expected value.
    Returns: True if it matches; False if the file was modified.
    """
    actual_hash = hash_file(filepath)
    return actual_hash == expected_hash
