"""
verify/verifier.py
Combines cryptography and blockchain functionality with timestamps
"""

import os
import time
import base64
from crypto.hash import hash_file
from crypto.rsa_sign import sign_hash, verify_signature
from blockchain.chain import Blockchain

blockchain = Blockchain()


def sign_file(filepath: str, private_key, signer_name: str) -> dict:
    """
    Sign a file and record the event in the blockchain.
    Returns: A dictionary containing the hash and signature.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    file_hash    = hash_file(filepath)
    signature    = sign_hash(private_key, file_hash)
    sig_b64      = base64.b64encode(signature).decode("utf-8")

    blockchain.add_event("FILE_SIGNED", {
        "filename":  os.path.basename(filepath),
        "hash":      file_hash,
        "signer":    signer_name,
        "signature": sig_b64[:32] + "...",
        "time":      time.strftime("%Y-%m-%d %H:%M:%S")
    })

    print(f"✅ File signed successfully: {os.path.basename(filepath)}")
    print(f"   Hash   : {file_hash[:20]}...")
    print(f"   Signer : {signer_name}")

    return {
        "filename":  filepath,
        "hash":      file_hash,
        "signature": signature,
        "signer":    signer_name
    }


def verify_file(filepath: str, original_hash: str,
                signature: bytes, public_key, verifier_name: str) -> bool:
    """
    Verify a file and record the result in the blockchain.
    Returns: True if the file is safe; False if modification is detected.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    current_hash = hash_file(filepath)
    sig_valid    = verify_signature(public_key, current_hash, signature)
    hash_match   = current_hash == original_hash

    if sig_valid and hash_match:
        blockchain.add_event("VERIFY_PASS", {
            "filename": os.path.basename(filepath),
            "hash":     current_hash,
            "verifier": verifier_name,
            "result":   "valid",
            "time":     time.strftime("%Y-%m-%d %H:%M:%S")
        })
        print(f"✅ VERIFY PASS: {os.path.basename(filepath)} is safe")
        return True
    else:
        blockchain.add_event("TAMPER_DETECTED", {
            "filename":      os.path.basename(filepath),
            "expected_hash": original_hash[:20] + "...",
            "actual_hash":   current_hash[:20] + "...",
            "hash_match":    hash_match,
            "sig_valid":     sig_valid,
            "time":          time.strftime("%Y-%m-%d %H:%M:%S")
        })
        print(f"❌ TAMPER DETECTED: {os.path.basename(filepath)} was modified!")
        return False


def get_audit_log() -> list:
    return blockchain.get_all_events()


def is_blockchain_valid() -> bool:
    return blockchain.is_valid()
