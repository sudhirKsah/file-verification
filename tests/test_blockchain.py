"""
tests/test_blockchain.py
Blockchain test
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from blockchain.chain import Blockchain

# 1. Create a blockchain.
bc = Blockchain()
print("✅ Blockchain created successfully (Genesis block is ready)")

# 2. Add events.
bc.add_event("FILE_SIGNED", {
    "filename": "secret.txt",
    "hash": "e76561cf...",
    "signer": "Alice"
})
print("✅ FILE_SIGNED event added successfully")

bc.add_event("VERIFY_PASS", {
    "filename": "secret.txt",
    "verifier": "Bob",
    "result": "valid"
})
print("✅ VERIFY_PASS event added successfully")

bc.add_event("TAMPER_DETECTED", {
    "filename": "secret.txt",
    "expected_hash": "e76561cf...",
    "actual_hash": "000000ff..."
})
print("✅ TAMPER_DETECTED event added successfully")

# 3. Display the complete chain.
print("\n--- Complete Chain ---")
bc.print_chain()

# 4. Check chain integrity.
print(f"\n✅ Chain valid: {bc.is_valid()}  ← Should be True")

# 5. Simulate block modification (attack!).
bc.chain[1].data["signer"] = "HACKER"
print(f"✅ After modification: {bc.is_valid()}  ← Should be False")
