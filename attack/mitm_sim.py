"""
attack/mitm_sim.py
Simulates two attack types:
1. File Tampering — modifies a file in transit
2. Man-in-the-Middle (MITM) — replaces both the file and signature
"""

import sys
import os
import tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from crypto.rsa_sign import generate_key_pair
from verify.verifier import sign_file, verify_file

# Use the system temporary directory on Windows, macOS, or Linux.
TMP = tempfile.gettempdir()


def print_banner(title: str):
    print("\n" + "=" * 55)
    print(f"  {title}")
    print("=" * 55)


def print_step(step: str):
    print(f"\n  🔹 {step}")


# -------------------------------------------------------
# Attack 1: File Tampering
# -------------------------------------------------------
def attack_file_tampering(private_key, public_key):
    print_banner("ATTACK 1 — File Tampering")

    filepath = os.path.join(TMP, "secret.txt")

    # 1. Create the original file.
    print_step("Alice creates the original file...")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("Confidential project plan: timeline, budget, and milestones.")
    print("     📄 secret.txt created")

    # 2. Sign the file.
    print_step("Alice signs the file...")
    result = sign_file(filepath, private_key, "Alice")

    # 3. Eve modifies the file.
    print_step("💀 Eve tampers with the file during transfer!")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("Confidential project plan: changed by an unauthorized user!")
    print("     ⚠️  File content has been modified!")

    # 4. Bob verifies the file.
    print_step("Bob verifies the file...")
    valid = verify_file(
        filepath,
        result["hash"],
        result["signature"],
        public_key,
        "Bob"
    )

    print_step(f"Result: {'✅ SAFE' if valid else '❌ TAMPER DETECTED — Attack caught!'}")
    return not valid


# -------------------------------------------------------
# Attack 2: Man-in-the-Middle (MITM)
# -------------------------------------------------------
def attack_mitm(private_key, public_key):
    print_banner("ATTACK 2 — Man-in-the-Middle (MITM)")

    original_path = os.path.join(TMP, "original.txt")
    fake_path = os.path.join(TMP, "fake.txt")

    # 1. Create the original file.
    print_step("Alice creates the original file...")
    with open(original_path, "w", encoding="utf-8") as f:
        f.write("Private message: Meet at the office at noon.")
    print("     📄 original.txt created")

    # 2. Sign the file with Alice's key.
    print_step("Alice signs the file with her private key...")
    result = sign_file(original_path, private_key, "Alice")

    # 3. Eve creates her own key and replaces everything.
    print_step("💀 Eve intercepts! Creates a fake file and signs it with her own key...")
    eve_private, eve_public = generate_key_pair()

    with open(fake_path, "w", encoding="utf-8") as f:
        f.write("Private message: Transfer the payment to Eve.")

    fake_result = sign_file(fake_path, eve_private, "Eve")
    print("     ⚠️  Eve replaced both the file and signature!")

    # 4. Bob verifies using Alice's public key.
    print_step("Bob verifies using Alice's public key...")
    valid = verify_file(
        fake_path,
        fake_result["hash"],
        fake_result["signature"],
        public_key,
        "Bob"
    )

    print_step(f"Result: {'✅ SAFE' if valid else '❌ MITM DETECTED — Attack caught!'}")
    return not valid


# -------------------------------------------------------
# Run All Attacks
# -------------------------------------------------------
if __name__ == "__main__":
    print("\n🛡️ Attack simulation starting...")
    print("   Testing if our system can catch every attack!\n")

    private_key, public_key = generate_key_pair()
    print("✅ RSA key pair generated for Alice")

    caught1 = attack_file_tampering(private_key, public_key)
    caught2 = attack_mitm(private_key, public_key)

    print_banner("SIMULATION SUMMARY")
    print(f"  Attack 1 - File Tampering : {'✅ CAUGHT' if caught1 else '❌ NOT caught'}")
    print(f"  Attack 2 - MITM           : {'✅ CAUGHT' if caught2 else '❌ NOT caught'}")

    if caught1 and caught2:
        print("\n  🎉 All attacks detected! The system is secure.\n")
    else:
        print("\n  ⚠️  Some attacks were not detected. Review the system.\n")
