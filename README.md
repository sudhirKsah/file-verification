# Secure File Verification

Secure File Verification is an academic cryptography project that verifies a file's integrity and authenticity using **SHA-256** and **RSA-2048 digital signatures with RSA-PSS padding**. The Flask application lets users generate keys, sign files, verify received files, view a tamper-evident audit trail, and demonstrate common attacks.

## Problem Statement

When a file is sent over a network, the receiver needs to know:

1. Was the file changed after it was signed?
2. Was it signed by the owner of the expected private key?

The sender signs a SHA-256 hash of the file with an RSA private key. The receiver recalculates the hash and verifies the signature with the corresponding public key.

> This project provides integrity and authenticity. It does **not** encrypt files, so it does not provide confidentiality.

## Features

- RSA-2048 private/public key-pair generation
- RSA-PSS signatures over SHA-256 file hashes
- Private and public key export/import in PEM format
- File verification and tamper detection
- Persistent, cryptographically linked audit hash chain in `blockchain.json`
- Visual audit-chain explorer
- CSV and JSON audit-log export
- Interactive file-tampering, MITM, and replay-attack demonstrations
- Flask web interface

## Cryptographic Design

```text
                 Sender                                      Receiver

File ──> SHA-256 hash ──> RSA-PSS sign                 Received file
                         (private key)                     │
                              │                             ▼
                              └──── signature ─────> SHA-256 hash
                                                            │
                                      sender public key ────┤
                                                            ▼
                                                Verify RSA-PSS signature
                                                            │
                                            Valid / Tamper detected
```

| Purpose | Algorithm |
|---|---|
| File digest | SHA-256 |
| Key algorithm | RSA, 2048-bit modulus |
| Signature scheme | RSA-PSS with MGF1/SHA-256 |
| Audit-block linking | SHA-256 |
| Key-file format | PEM |

The application signs the file hash rather than the full file. A SHA-256 hash is always a fixed-size 256-bit digest, which makes signing practical even for large files.

## Architecture

```text
┌──────────────┐      ┌──────────────┐      ┌──────────────────────┐
│ Crypto Core  │ ───> │   Verifier   │ ───> │ Audit Hash Chain     │
│ SHA-256/RSA  │      │ Sign/Verify  │      │ blockchain.json      │
└──────────────┘      └──────────────┘      └──────────────────────┘
       ▲                      ▲                         ▲
       └──────────────────────┴─────────────────────────┘
                              │
                       ┌─────────────┐
                       │ Flask UI    │
                       │ Dashboard   │
                       └─────────────┘
```

## Project Structure

```text
security-file-verification/
├── crypto/
│   ├── hash.py             # SHA-256 file, byte, and string hashing
│   └── rsa_sign.py         # RSA keys, signing, and verification
├── blockchain/
│   └── chain.py            # Local tamper-evident audit hash chain
├── verify/
│   └── verifier.py         # Connects crypto operations and audit events
├── ui/
│   └── app.py              # Flask server, dashboard, and attack simulations
├── attack/
│   └── mitm_sim.py         # Command-line tampering and MITM simulation
├── tests/
│   ├── test_hash.py        # Hash-integrity demonstration
│   ├── test_rsa.py         # RSA-signature demonstration
│   ├── test_verifier.py    # End-to-end sign/verify demonstration
│   └── test_blockchain.py  # Audit-chain integrity demonstration
├── blockchain.json         # Persistent audit events
├── test_sample.txt         # Sample file for test scripts
├── important.txt           # Sample file for verifier tests
└── README.md
```

## Installation

### Requirements

- Python 3.10 or later
- `pip`

### Install dependencies

From this project directory:

```bash
python -m venv .venv
```

Activate the environment:

```bash
# Linux/macOS
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

Then install dependencies:

```bash
pip install flask cryptography
```

## Run the Web Application

```bash
python ui/app.py
```

Open the displayed local address in a browser, normally:

```text
http://127.0.0.1:5000
```

Keep the terminal running while using the application.

## Test the UI Step by Step

### 1. Generate keys

1. Open the **Dashboard** tab.
2. Click **Generate RSA keys**.
3. The key status changes to **Ready**.
4. Optionally download the private and public PEM files.

Never share the private key. The public key is shared with the receiver.

### 2. Sign a file

1. Create a local file named `demo.txt`.
2. Enter `Alice` as the signer name.
3. Upload `demo.txt` in the **Sign file** section.
4. Click **Sign file**.

The system calculates the SHA-256 hash, signs it with Alice's private key, and adds a `FILE_SIGNED` audit event.

### 3. Verify the unchanged file

1. Enter `Bob` as the verifier name.
2. Upload the exact same unchanged `demo.txt`.
3. Click **Verify file**.

Expected result: **integrity verified, file is authentic**. A `VERIFY_PASS` event is added to the audit log.

### 4. Demonstrate tamper detection

1. Edit the contents of `demo.txt` locally.
2. Save it with the same filename: `demo.txt`.
3. Upload the changed file in **Verify file**.
4. Click **Verify file**.

Expected result: **tamper detected**. The changed file has a different SHA-256 hash, so the original signature is no longer valid for it. A `TAMPER_DETECTED` event is recorded.

> The current UI keeps signatures in memory and identifies them by filename. Verify within the same running server session and retain the original filename. Restarting the server clears the currently loaded keys and signed-file records.

### 5. View and export the audit trail

- Open the **Blockchain** tab to view the linked audit blocks.
- Click a block to inspect its full hash and previous hash.
- Return to **Dashboard** and use **CSV** or **JSON** to export the audit log.

## Attack Demonstrations

Open the **Attack Sim** tab and run each simulation.

| Attack | What happens | Why it is detected |
|---|---|---|
| File tampering | An attacker changes a signed file. | The recalculated SHA-256 hash differs from the signed hash. |
| Man-in-the-middle | An attacker replaces a message and signs it with the attacker's own private key. | The attacker's signature cannot be verified with the genuine sender's public key. |
| Replay attack | An attacker attaches an old valid signature to a new malicious file. | A signature is tied to the old file hash, not the new file hash. |

## Run the Command-Line Demonstrations

Run these commands from the project root:

```bash
python attack/mitm_sim.py
python tests/test_hash.py
python tests/test_rsa.py
python tests/test_blockchain.py
python tests/test_verifier.py
```

| Script | Expected result |
|---|---|
| `test_hash.py` | Verification is `True` before modification and `False` after modification. |
| `test_rsa.py` | A correct hash verifies as `True`; a fake hash verifies as `False`. |
| `test_blockchain.py` | Chain validity is `True` before modification and `False` after a block is changed in memory. |
| `test_verifier.py` | The original file passes verification; the modified file is rejected. |
| `mitm_sim.py` | File-tampering and MITM scenarios are detected. |

> Some demonstration scripts modify `test_sample.txt`, `important.txt`, and add audit events to `blockchain.json`. Use copies or reset the demo data before recording final screenshots.

## Audit Hash Chain

Every block includes the previous block's hash. Altering stored block data changes its calculated hash and breaks the link to the next block, which `is_valid()` detects.

This is a **local tamper-evident audit hash chain**, not a decentralized public blockchain. It has no peer network, consensus mechanism, or externally anchored immutable history. It demonstrates audit logging and hash-linked integrity for this academic project.

## Security Properties and Limitations

### Provided

- **Integrity:** Changes to the signed file are detected.
- **Authenticity:** A valid signature proves possession of the matching private key.
- **Auditability:** Sign and verification events are persisted and hash-linked.

### Not provided / future work

- **Confidentiality:** Files are not encrypted.
- **Trusted public-key distribution:** The receiver must obtain the genuine public key through a trusted channel.
- **Long-term key protection:** Private keys are exported without password encryption in this demonstration.
- **Persistent signatures:** The browser-session signature store is not a production signature-distribution format.
- **Distributed audit consensus:** The audit chain is local only.

Possible extensions include hybrid RSA-AES encryption, password-protected private keys, X.509 certificates, digital-signature sidecar files, trusted timestamping, and an ECDSA/Ed25519 option.

## Viva Summary

> Our project is a secure file verification system using SHA-256 and RSA digital signatures. The sender hashes the file and signs that hash with an RSA private key using RSA-PSS padding. The receiver recalculates the received file's hash and verifies the signature with the sender's public key. If the file is modified, even by one character, the hash changes and verification fails. The application records sign and verification events in a local cryptographically linked audit hash chain.

## Technology Stack

- Python
- Flask
- PyCA `cryptography`
- HTML, CSS, and JavaScript
- JSON for persistent audit data

## Academic Use

This project is intended for educational use in an asymmetric-cryptography course. It is not production-ready without stronger key management, trusted identity infrastructure, secure file handling, and additional security hardening.
