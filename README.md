# Secure File Integrity Verification

> Secure file integrity verification system using RSA-2048 digital signatures and SHA-256 hashing, with a custom blockchain audit trail for tamper-evident logging. Built with Python and Flask. Detects file tampering, MITM, and replay attacks via an interactive simulation module.

![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1-black?logo=flask&logoColor=white)
![Cryptography](https://img.shields.io/badge/cryptography-43.x-green)
![License](https://img.shields.io/badge/license-MIT-lightgrey)
![Status](https://img.shields.io/badge/status-academic%20project-orange)

---

## Overview

This project implements a **two-layer security system** for verifying that a file has not been tampered with and genuinely came from its claimed sender:

- **Layer 1 — Digital Signatures:** RSA-2048 (PSS padding) + SHA-256 hashing
- **Layer 2 — Blockchain Audit Trail:** An append-only, cryptographically linked chain that permanently records every signing and verification event

A full **Attack Simulation** module (File Tampering, Man-in-the-Middle, and Replay Attack) demonstrates the system catching real-world attack patterns step-by-step, with a SpongeBob-themed interactive UI.

---

## Features

1. **RSA-2048 key generation** with export/import (`.pem`)
2. **File signing** with custom signer names
3. **File verification** with tamper detection
4. **Blockchain audit trail** — persists to `blockchain.json`, survives restarts
5. **Visual blockchain explorer** — see blocks linked as a chain, click for details
6. **Attack simulation** — File Tampering, MITM, and Replay Attack, animated step-by-step
7. **Export audit logs** as CSV or JSON
8. **Web UI** built with Flask — no frontend framework required

---

## Architecture

```
┌──────────────┐      ┌──────────────┐      ┌──────────────────┐
│  Crypto Core │ ───▶ │   Verifier   │ ───▶ │  Blockchain       │
│ SHA-256+RSA  │      │ Sign/Verify  │      │  Audit Trail      │
└──────────────┘      └──────────────┘      └──────────────────┘
                              │                       │
                              ▼                       ▼
                       ┌──────────────┐      ┌──────────────────┐
                       │   Flask UI   │      │  blockchain.json │
                       │  Dashboard   │      │   (persisted)    │
                       └──────────────┘      └──────────────────┘
```

| Layer | Responsibility |
|---|---|
| `crypto/` | SHA-256 hashing, RSA-2048 key generation, signing & verification |
| `blockchain/` | Block & Blockchain classes, chain integrity validation, JSON persistence |
| `verify/` | Orchestrates signing/verification and blockchain logging |
| `ui/` | Flask web app — dashboard, blockchain visual, attack simulation |
| `attack/` | Standalone CLI attack simulation script |

---

## Project Structure

```
secure_file_verify/
├── crypto/
│   ├── __init__.py
│   ├── hash.py          # SHA-256 file hashing
│   └── rsa_sign.py      # RSA key generation, signing, verification
├── blockchain/
│   ├── __init__.py
│   └── chain.py         # Blockchain audit trail with JSON persistence
├── verify/
│   ├── __init__.py
│   └── verifier.py      # Sign / verify orchestration
├── ui/
│   └── app.py           # Flask web application
├── attack/
│   ├── __init__.py
│   └── mitm_sim.py      # CLI attack simulation
├── tests/
│   ├── test_hash.py
│   ├── test_rsa.py
│   ├── test_blockchain.py
│   └── test_verifier.py
├── blockchain.json       # Auto-generated audit trail
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.10+ (developed and tested on **3.13**)
- pip

### Installation

```bash
git clone https://github.com/<your-username>/secure-file-verify.git
cd secure-file-verify

pip install cryptography flask
```

> **Note:** If installing inside a path containing spaces (e.g. on Windows), skip `venv` and install packages globally with the command above.

### Run the Web App

```bash
python ui/app.py
```

Then open your browser at **http://localhost:5000**

### Run the CLI Attack Simulation

```bash
python attack/mitm_sim.py
```

### Run Unit Tests

```bash
python tests/test_hash.py
python tests/test_rsa.py
python tests/test_blockchain.py
python tests/test_verifier.py
```

---

## Usage

| Step | Action |
|---|---|
| 1 | Click **Generate RSA Keys** on the Dashboard tab |
| 2 | Enter a signer name and upload a file → **Sign File** |
| 3 | Enter a verifier name and upload the same file → **Verify File** |
| 4 | Modify the file and verify again → see **TAMPER DETECTED** |
| 5 | Visit the **Blockchain** tab to see the chain visually |
| 6 | Visit the **Attack Sim** tab to run all 3 attack simulations |
| 7 | Export the audit log as **CSV** or **JSON** from the Dashboard |

---

## Attack Simulations

| Attack | Scenario | Detection Method |
|---|---|---|
| **File Tampering** | Plankton modifies a signed file's contents | SHA-256 hash mismatch |
| **Man-in-the-Middle** | Plankton replaces the file and signs it with his own key | Signature fails against sender's public key |
| **Replay Attack** | Plankton reuses an old valid signature on a new file | Signature is bound to original file hash, not reusable |

All three attacks are detected with **100% success rate** in testing.

---

## Security Notes

- Uses **RSA-2048** with **PSS padding** (resistant to existential forgery)
- **SHA-256** hashing provides a 256-bit digest (collision probability ≈ 1 in 2²⁵⁶)
- Blockchain blocks are cryptographically linked — modifying any block invalidates the chain from that point forward
- This is an **academic / educational project** — not intended for production use without additional hardening (PKI, HSM, distributed consensus, etc.)

---

## Roadmap / Future Improvements

- [ ] Distributed blockchain with consensus mechanism
- [ ] PKI / X.509 certificate integration
- [ ] Hardware Security Module (HSM) support for key storage
- [ ] ECDSA / Ed25519 signature algorithm option
- [ ] RFC 3161 trusted timestamping
- [ ] End-to-end file encryption

---

## Screenshots

> _Add screenshots here after running the app locally._

| Dashboard | Blockchain Visual | Attack Simulation |
|---|---|---|
| `screenshot-dashboard.png` | `screenshot-blockchain.png` | `screenshot-attack.png` |

---

## Contributing

Contributions, issues, and feature requests are welcome.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---


## 📄 License

This project was developed for academic purposes as part of a Fundamentals of Cyber Security Lab course. Licensed under the [MIT License](LICENSE).

---

## Acknowledgements

- [Python Cryptographic Authority (PyCA)](https://cryptography.io/) — cryptography library
- [Flask](https://flask.palletsprojects.com/) — web framework
- [Tabler Icons](https://tabler.io/icons) — UI iconography
