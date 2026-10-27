"""
tests/test_verifier.py
Verification system test
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from crypto.rsa_sign import generate_key_pair
from verify.verifier import sign_file, verify_file, get_audit_log, is_blockchain_valid

# 1. Create a key pair.
private_key, public_key = generate_key_pair()
print("✅ Key pair created successfully")

# 2. Create a test file.
with open("important.txt", "w", encoding="utf-8") as f:
    f.write("Krabby Patty Secret Formula!")

# 3. Sign the file.
print("\n--- Sign File ---")
result = sign_file("important.txt", private_key, "Alice")

# 4. Verify the unmodified file.
print("\n--- Normal Verification ---")
verify_file("important.txt", result["hash"],
            result["signature"], public_key, "Bob")

# 5. Modify the file and verify it again.
print("\n--- Verification After Modification ---")
with open("important.txt", "a", encoding="utf-8") as f:
    f.write(" (Modified by Eve!)")

verify_file("important.txt", result["hash"],
            result["signature"], public_key, "Bob")

# 6. Display the audit log.
print("\n--- Audit Log ---")
for event in get_audit_log():
    print(f"  Block #{event['index']} [{event['event_type']}] → {event['data']['filename']}")

# 7. Verify the blockchain.
print(f"\n✅ Blockchain valid: {is_blockchain_valid()}")
