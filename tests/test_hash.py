"""
tests/test_hash.py
SHA-256 hashing test
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from crypto.hash import hash_file, verify_file_hash

# Create a test file.
with open("test_sample.txt", "w", encoding="utf-8") as f:
    f.write("Hello from Bikini Bottom!")

# Hash the original file.
h = hash_file("test_sample.txt")
print(f"Original hash : {h}")
print(f"Verification  : {verify_file_hash('test_sample.txt', h)}  ← Should be True")

# Modify the file.
with open("test_sample.txt", "a", encoding="utf-8") as f:
    f.write(" TAMPERED!")

print(f"After modification: {verify_file_hash('test_sample.txt', h)}  ← Should be False")
