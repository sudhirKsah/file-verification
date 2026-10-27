"""
tests/test_rsa.py
RSA signing test
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from crypto.hash import hash_file
from crypto.rsa_sign import generate_key_pair, sign_hash, verify_signature

# 1. Create a key pair.
private_key, public_key = generate_key_pair()
print("✅ Key pair created successfully")

# 2. Hash the file.
h = hash_file("test_sample.txt")
print(f"✅ Hash: {h[:20]}...")

# 3. Sign the hash.
signature = sign_hash(private_key, h)
print(f"✅ Signature: {len(signature)} bytes")

# 4. Verify the valid signature.
result = verify_signature(public_key, h, signature)
print(f"✅ Valid verification: {result}  ← Should be True")

# 5. Change the hash and verify again.
fake_hash = "0000000000000000000000000000000000000000000000000000000000000000"
result2 = verify_signature(public_key, fake_hash, signature)
print(f"✅ Fake hash verification: {result2}  ← Should be False")
