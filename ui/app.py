"""
ui/app.py - Full Featured Flask App
Features:
  - Dashboard: generate/import/export keys, sign/verify files
  - Blockchain Visual: animated chain of blocks
  - Attack Simulation: step-by-step attack demos
  - Multi-signer: custom signer name input
  - Export: download audit log as CSV or JSON
"""

import sys, os, io, tempfile, time, csv, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from flask import Flask, request, jsonify, render_template_string, send_file
from crypto.rsa_sign import generate_key_pair, sign_hash, verify_signature
from cryptography.hazmat.primitives import serialization
from verify.verifier import sign_file, verify_file, get_audit_log, is_blockchain_valid
from crypto.hash import hash_file, hash_string

app = Flask(__name__)
TMP          = tempfile.gettempdir()
current_keys = {"private": None, "public": None}
signed_files = {}

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Secure File Verification</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@latest/dist/tabler-icons.min.css">
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#f8f9fb;--surface:#fff;
  --border:rgba(0,0,0,.08);--border-md:rgba(0,0,0,.14);
  --t1:#111827;--t2:#6b7280;--t3:#9ca3af;
  --accent:#2563eb;--accent-bg:#eff6ff;
  --ok:#16a34a;--ok-bg:#f0fdf4;--ok-br:#bbf7d0;
  --err:#dc2626;--err-bg:#fef2f2;--err-br:#fecaca;
  --warn:#d97706;--warn-bg:#fffbeb;--warn-br:#fde68a;
  --purple:#7c3aed;--purple-bg:#f5f3ff;--purple-br:#ddd6fe;
}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
  background:var(--bg);color:var(--t1);font-size:16px;line-height:1.6;min-height:100vh}

/* Header */
header{background:var(--surface);border-bottom:1px solid var(--border);
  padding:0 36px;height:70px;display:flex;align-items:center;gap:14px;
  position:sticky;top:0;z-index:100}
.logo{width:40px;height:40px;background:var(--accent-bg);border-radius:10px;
  display:flex;align-items:center;justify-content:center}
.logo i{font-size:21px;color:var(--accent)}
header h1{font-size:18px;font-weight:700}
header p{font-size:14px;color:var(--t2)}
.nav-tabs{margin-left:auto;display:flex;gap:4px}
.nav-tab{padding:8px 16px;border-radius:7px;font-size:14px;font-weight:600;
  cursor:pointer;border:1px solid transparent;color:var(--t2);background:transparent;
  transition:all .15s;display:flex;align-items:center;gap:6px}
.nav-tab:hover{background:var(--bg);color:var(--t1)}
.nav-tab.active{background:var(--accent-bg);color:var(--accent);border-color:#bfdbfe}
.chain-status{display:flex;align-items:center;gap:7px;font-size:13px;
  color:var(--t2);padding-left:16px;border-left:1px solid var(--border)}
.dot{width:8px;height:8px;border-radius:50%;background:var(--ok)}
.dot.bad{background:var(--err)}

/* Layout */
.page{max-width:1400px;margin:38px auto;padding:0 32px}
.tab-page{display:none}.tab-page.active{display:block}

/* Stats */
.stats{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px;margin-bottom:26px}
.stat{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:20px 24px}
.stat-label{font-size:13px;color:var(--t2);text-transform:uppercase;letter-spacing:.5px;margin-bottom:8px}
.stat-value{font-size:30px;font-weight:700}

/* Quick-start guide */
.quick-start{display:flex;align-items:center;gap:18px;background:linear-gradient(135deg,#eff6ff,#f5f3ff);
  border:1px solid #dbeafe;border-radius:14px;padding:19px 24px;margin-bottom:26px}
.quick-start-icon{width:42px;height:42px;border-radius:11px;background:#fff;color:var(--accent);
  display:flex;align-items:center;justify-content:center;font-size:21px;box-shadow:0 1px 3px rgba(37,99,235,.12)}
.quick-start-copy{flex:1}.quick-start-title{font-size:16px;font-weight:700}.quick-start-text{font-size:14px;color:var(--t2)}
.quick-start-steps{display:flex;align-items:center;gap:9px;font-size:13px;font-weight:700;color:var(--accent)}
.quick-start-steps i{color:#93c5fd}
@media(max-width:640px){.quick-start{align-items:flex-start}.quick-start-steps{display:none}}

/* Cards */
.card{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:24px 28px;margin-bottom:20px}
.card-header{display:flex;align-items:center;gap:12px;margin-bottom:20px;padding-bottom:16px;border-bottom:1px solid var(--border)}
.card-icon{width:36px;height:36px;border-radius:8px;background:var(--bg);display:flex;align-items:center;justify-content:center}
.card-icon i{font-size:19px;color:var(--t2)}
.card-title{font-size:16px;font-weight:700}
.card-sub{font-size:13px;color:var(--t2)}
.grid-2{display:grid;grid-template-columns:1fr 1fr;gap:20px}
@media(max-width:640px){.grid-2{grid-template-columns:1fr}}

/* Buttons */
.btn{display:inline-flex;align-items:center;justify-content:center;gap:6px;
  padding:10px 18px;border:1px solid var(--border-md);border-radius:7px;
  background:var(--surface);color:var(--t1);font-size:15px;font-weight:600;
  cursor:pointer;transition:background .15s,border-color .15s;white-space:nowrap}
.btn:hover{background:var(--bg);border-color:rgba(0,0,0,.2)}
.btn:active{transform:scale(.98)}
.btn-primary{background:var(--accent);border-color:var(--accent);color:#fff}
.btn-primary:hover{background:#1d4ed8;border-color:#1d4ed8}
.btn-danger{background:var(--err);border-color:var(--err);color:#fff}
.btn-danger:hover{background:#b91c1c;border-color:#b91c1c}
.btn-sm{padding:8px 14px;font-size:14px}
.btn-block{width:100%}

/* Input */
input[type=text]{width:100%;padding:10px 14px;border:1px solid var(--border-md);
  border-radius:7px;font-size:15px;color:var(--t1);background:var(--surface);
  outline:none;transition:border-color .15s}
input[type=text]:focus{border-color:var(--accent)}
.input-label{font-size:13px;font-weight:700;color:var(--t2);text-transform:uppercase;
  letter-spacing:.5px;margin-bottom:7px}

/* Dropzone */
.dropzone{border:1.5px dashed var(--border-md);border-radius:10px;padding:26px;
  text-align:center;cursor:pointer;transition:border-color .15s,background .15s;
  margin-bottom:12px;position:relative}
.dropzone:hover{border-color:var(--accent);background:var(--accent-bg)}
.dropzone input[type=file]{position:absolute;inset:0;opacity:0;cursor:pointer;width:100%;height:100%}
.dropzone i{font-size:26px;color:var(--t3);display:block;margin-bottom:8px}
.dropzone p{font-size:14px;color:var(--t2)}
.dropzone small{font-size:13px;color:var(--t3)}
.dropzone.has-file{border-color:var(--ok);background:var(--ok-bg)}
.dropzone.has-file i{color:var(--ok)}
.dropzone.has-file p{color:var(--ok);font-weight:500}

/* Banner */
.banner{display:none;padding:12px 16px;border-radius:7px;font-size:15px;margin-top:14px;border:1px solid}
.banner.show{display:flex;align-items:flex-start;gap:8px}
.banner i{font-size:16px;margin-top:1px;flex-shrink:0}
.banner.success{background:var(--ok-bg);border-color:var(--ok-br);color:var(--ok)}
.banner.error{background:var(--err-bg);border-color:var(--err-br);color:var(--err)}
.banner.info{background:var(--accent-bg);border-color:#bfdbfe;color:var(--accent)}
.key-preview{margin-top:10px;background:var(--bg);border:1px solid var(--border);
  border-radius:6px;padding:12px 14px;font-family:monospace;font-size:13px;
  color:var(--t2);word-break:break-all;line-height:1.5}

/* Audit log */
.log-row{display:flex;align-items:center;gap:12px;padding:12px 14px;
  border-radius:6px;margin-bottom:6px;border:1px solid var(--border);background:var(--surface)}
.log-row:last-child{margin-bottom:0}
.event-badge{display:inline-block;padding:3px 9px;border-radius:4px;
  font-size:12px;font-weight:700;letter-spacing:.3px;white-space:nowrap}
.badge-signed{background:var(--accent-bg);color:var(--accent);border:1px solid #bfdbfe}
.badge-pass{background:var(--ok-bg);color:var(--ok);border:1px solid var(--ok-br)}
.badge-tamper{background:var(--err-bg);color:var(--err);border:1px solid var(--err-br)}
.log-file{font-size:15px;font-weight:600;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.log-detail{font-size:14px;color:var(--t2);white-space:nowrap}
.log-time{font-size:13px;color:var(--t3);white-space:nowrap}
.log-block{font-size:13px;color:var(--t3);white-space:nowrap}
.log-empty{text-align:center;padding:36px;color:var(--t3);font-size:15px}
.log-empty i{font-size:32px;display:block;margin-bottom:10px}
.section-label{font-size:13px;font-weight:700;color:var(--t2);text-transform:uppercase;letter-spacing:.5px;margin-bottom:11px}
.persist-note{display:flex;align-items:center;gap:7px;font-size:13px;color:var(--t2);margin-top:12px}
.persist-note i{font-size:16px;color:var(--ok)}

/* Blockchain visual */
.chain-wrap{overflow-x:auto;padding:8px 0 16px}
.chain-row{display:flex;align-items:center;gap:0;min-width:max-content}
.chain-block{background:var(--surface);border:1.5px solid var(--border-md);
  border-radius:10px;padding:15px 17px;width:220px;flex-shrink:0;
  transition:box-shadow .2s,border-color .2s;cursor:pointer;position:relative}
.chain-block:hover{border-color:var(--accent);box-shadow:0 0 0 3px var(--accent-bg)}
.chain-block.genesis{border-color:#a3a3a3;background:#f9f9f9}
.chain-block.signed{border-color:#93c5fd}
.chain-block.pass{border-color:var(--ok-br)}
.chain-block.tamper{border-color:var(--err-br)}
.block-index{font-size:12px;font-weight:700;color:var(--t3);margin-bottom:5px;text-transform:uppercase;letter-spacing:.5px}
.block-event{font-size:14px;font-weight:700;margin-bottom:8px}
.block-event.ev-genesis{color:var(--t2)}
.block-event.ev-signed{color:var(--accent)}
.block-event.ev-pass{color:var(--ok)}
.block-event.ev-tamper{color:var(--err)}
.block-hash{font-family:monospace;font-size:12px;color:var(--t3);
  background:var(--bg);border-radius:4px;padding:4px 7px;margin-bottom:5px;word-break:break-all}
.block-file{font-size:13px;color:var(--t2);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.block-time{font-size:12px;color:var(--t3);margin-top:5px}
.chain-arrow{display:flex;align-items:center;padding:0 6px;flex-shrink:0}
.chain-arrow i{font-size:18px;color:var(--t3)}
.chain-empty{text-align:center;padding:40px;color:var(--t3);font-size:13px}
.chain-empty i{font-size:32px;display:block;margin-bottom:8px}
.export-bar{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.export-bar span{font-size:14px;color:var(--t2);margin-right:4px}

/* ══ Attack Simulation ══ */
.attack-page-header{
  background:linear-gradient(135deg,#1e1b4b 0%,#312e81 100%);
  border-radius:14px;padding:24px 28px;margin-bottom:20px;color:#fff;
  display:flex;align-items:flex-start;gap:16px;
}
.attack-page-header .big-icon{font-size:40px;line-height:1}
.attack-page-header h2{font-size:18px;font-weight:700;margin-bottom:4px}
.attack-page-header p{font-size:13px;opacity:.8;line-height:1.6}

/* Character pills */
.char-row{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:20px}
.char-pill{display:flex;align-items:center;gap:6px;padding:6px 12px;
  background:var(--surface);border:1px solid var(--border);border-radius:20px;font-size:12px}
.char-pill .avatar{font-size:18px;line-height:1}
.char-pill .name{font-weight:600;color:var(--t1)}
.char-pill .role{color:var(--t2)}

/* Attack cards grid */
.attack-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin-bottom:20px}
@media(max-width:700px){.attack-grid{grid-template-columns:1fr}}

.attack-card{background:var(--surface);border:1px solid var(--border);
  border-radius:14px;padding:20px;display:flex;flex-direction:column;gap:0}
.attack-card-top{display:flex;align-items:center;gap:10px;margin-bottom:10px}
.atk-num{font-size:10px;font-weight:700;padding:2px 8px;border-radius:4px;
  background:var(--err-bg);color:var(--err);border:1px solid var(--err-br)}
.atk-num.purple{background:var(--purple-bg);color:var(--purple);border-color:var(--purple-br)}
.attack-card h3{font-size:14px;font-weight:600;margin-bottom:6px}
.attack-card p{font-size:12px;color:var(--t2);line-height:1.6;margin-bottom:14px;flex:1}

/* Scenario box */
.scenario{background:var(--bg);border:1px solid var(--border);border-radius:8px;
  padding:10px 12px;margin-bottom:14px;font-size:12px;line-height:1.8}
.scenario .s-row{display:flex;align-items:flex-start;gap:8px}
.scenario .s-icon{font-size:14px;flex-shrink:0;margin-top:1px}
.scenario .s-text{color:var(--t2)}
.scenario .s-text b{color:var(--t1)}

/* Steps animation */
.sim-steps{margin-top:14px;display:none}
.sim-steps.show{display:block}

.step-row{display:flex;align-items:flex-start;gap:10px;padding:9px 0;
  border-bottom:1px solid var(--border);
  opacity:0;transform:translateY(5px);
  transition:opacity .3s ease,transform .3s ease}
.step-row:last-child{border-bottom:none}
.step-row.visible{opacity:1;transform:translateY(0)}

.step-avatar{font-size:20px;flex-shrink:0;width:28px;text-align:center;margin-top:2px}
.step-body{flex:1}
.step-label{font-size:13px;font-weight:500;color:var(--t1)}
.step-sub{font-size:11px;color:var(--t2);margin-top:2px;font-family:monospace;word-break:break-all}

.step-tag{display:inline-block;margin-top:4px;padding:2px 8px;border-radius:4px;
  font-size:10px;font-weight:600}
.tag-ok    {background:var(--ok-bg);color:var(--ok);border:1px solid var(--ok-br)}
.tag-atk   {background:var(--warn-bg);color:var(--warn);border:1px solid var(--warn-br)}
.tag-caught{background:var(--err-bg);color:var(--err);border:1px solid var(--err-br)}
.tag-info  {background:var(--accent-bg);color:var(--accent);border:1px solid #bfdbfe}
.tag-purple{background:var(--purple-bg);color:var(--purple);border:1px solid var(--purple-br)}

/* Hash compare */
.hash-compare{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:6px}
.hash-box{background:var(--bg);border:1px solid var(--border);border-radius:6px;padding:8px 10px}
.hash-box-label{font-size:10px;font-weight:600;color:var(--t2);margin-bottom:4px;text-transform:uppercase}
.hash-val{font-family:monospace;font-size:10px;word-break:break-all;color:var(--t1)}
.hash-val.changed{color:var(--err)}

.sim-verdict{margin-top:12px;padding:12px 16px;border-radius:8px;
  font-size:13px;font-weight:500;display:none;border:1px solid;text-align:center}
.sim-verdict.show{display:block}
.sim-verdict.caught{background:var(--ok-bg);border-color:var(--ok-br);color:var(--ok)}
.sim-verdict.fail  {background:var(--err-bg);border-color:var(--err-br);color:var(--err)}

/* Summary */
.summary-card{background:var(--surface);border:1px solid var(--border);
  border-radius:14px;padding:20px 24px;display:none}
.summary-card.show{display:block}
.summary-row{display:flex;align-items:center;gap:12px;
  padding:10px 0;border-bottom:1px solid var(--border)}
.summary-row:last-child{border-bottom:none}
.score-bar{height:6px;border-radius:3px;background:var(--bg);flex:1;overflow:hidden}
.score-fill{height:100%;border-radius:3px;background:var(--ok);transition:width .6s ease}

.spinner{display:inline-block;width:14px;height:14px;border:2px solid currentColor;
  border-top-color:transparent;border-radius:50%;animation:spin .7s linear infinite;vertical-align:middle}
@keyframes spin{to{transform:rotate(360deg)}}
</style>
</head>
<body>

<header>
  <div class="logo"><i class="ti ti-shield-lock" aria-hidden="true"></i></div>
  <div><h1>Secure File Verification</h1><p>Sign, verify, and trace every file</p></div>
  <nav class="nav-tabs">
    <button class="nav-tab active" onclick="switchTab('main')"   id="tab-main">  <i class="ti ti-home"  aria-hidden="true"></i> Dashboard</button>
    <button class="nav-tab"        onclick="switchTab('chain')"  id="tab-chain"> <i class="ti ti-link"  aria-hidden="true"></i> Blockchain</button>
    <button class="nav-tab"        onclick="switchTab('attack')" id="tab-attack"><i class="ti ti-virus" aria-hidden="true"></i> Attack Sim</button>
  </nav>
  <div class="chain-status">
    <div class="dot" id="chain-dot"></div>
    <span id="chain-label">Checking...</span>
  </div>
</header>

<div class="page">

<!-- ═══ TAB 1 · DASHBOARD ═══ -->
<div class="tab-page active" id="page-main">
  <div class="stats">
    <div class="stat"><div class="stat-label">Key status</div>
      <div class="stat-value" id="stat-keys" style="font-size:18px;padding-top:5px;color:var(--t2)">Not generated</div></div>
    <div class="stat"><div class="stat-label">Files signed</div>
      <div class="stat-value" id="stat-signed">0</div></div>
    <div class="stat"><div class="stat-label">Blockchain blocks</div>
      <div class="stat-value" id="stat-blocks">1</div></div>
  </div>

  <div class="quick-start">
    <div class="quick-start-icon"><i class="ti ti-route" aria-hidden="true"></i></div>
    <div class="quick-start-copy"><div class="quick-start-title">Quick start</div>
      <div class="quick-start-text">Generate a key pair, sign a file, then verify it to create an auditable record.</div></div>
    <div class="quick-start-steps"><span>1. Keys</span><i class="ti ti-arrow-right"></i><span>2. Sign</span><i class="ti ti-arrow-right"></i><span>3. Verify</span></div>
  </div>

  <div class="grid-2" style="margin-bottom:16px">
    <div class="card">
      <div class="card-header">
        <div class="card-icon"><i class="ti ti-key" aria-hidden="true"></i></div>
        <div><div class="card-title">Key pair</div><div class="card-sub">Generate or export RSA keys</div></div>
      </div>
      <button class="btn btn-primary btn-block" onclick="generateKeys()" style="margin-bottom:14px">
        <i class="ti ti-key" aria-hidden="true"></i> Generate RSA keys
      </button>
      <div class="section-label">Export</div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">
        <button class="btn btn-sm" onclick="exportKey('private')"><i class="ti ti-download" aria-hidden="true"></i> Private key</button>
        <button class="btn btn-sm" onclick="exportKey('public')"><i class="ti ti-download" aria-hidden="true"></i> Public key</button>
      </div>
      <div class="banner" id="key-result"></div>
    </div>
    <div class="card">
      <div class="card-header">
        <div class="card-icon"><i class="ti ti-upload" aria-hidden="true"></i></div>
        <div><div class="card-title">Import keys</div><div class="card-sub">Load existing .pem files</div></div>
      </div>
      <div class="section-label">Private key</div>
      <div class="dropzone" id="drop-priv" style="padding:18px;margin-bottom:12px">
        <input type="file" id="import-private-input" accept=".pem" onchange="onFileChange('drop-priv','import-private-input')">
        <i class="ti ti-file-import" aria-hidden="true"></i>
        <p id="drop-priv-label">Drop or click to select</p>
      </div>
      <div class="section-label">Public key</div>
      <div class="dropzone" id="drop-pub" style="padding:18px;margin-bottom:12px">
        <input type="file" id="import-public-input" accept=".pem" onchange="onFileChange('drop-pub','import-public-input')">
        <i class="ti ti-file-import" aria-hidden="true"></i>
        <p id="drop-pub-label">Drop or click to select</p>
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">
        <button class="btn btn-sm" onclick="importKey('private')">Import private</button>
        <button class="btn btn-sm" onclick="importKey('public')">Import public</button>
      </div>
      <div class="banner" id="key-import-result"></div>
    </div>
  </div>

  <div class="grid-2" style="margin-bottom:16px">
    <div class="card">
      <div class="card-header">
        <div class="card-icon"><i class="ti ti-pencil" aria-hidden="true"></i></div>
        <div><div class="card-title">Sign file</div><div class="card-sub">Sign with your private key</div></div>
      </div>
      <div style="margin-bottom:12px">
        <div class="input-label">Signer name</div>
        <input type="text" id="signer-name" placeholder="e.g. Alice">
      </div>
      <div class="dropzone" id="drop-sign">
        <input type="file" id="sign-file-input" onchange="onFileChange('drop-sign','sign-file-input')">
        <i class="ti ti-file-upload" aria-hidden="true"></i>
        <p id="drop-sign-label">Drop file or click to browse</p>
        <small>Any file type supported</small>
      </div>
      <button class="btn btn-primary btn-block" onclick="signFile()">
        <i class="ti ti-pencil" aria-hidden="true"></i> Sign file
      </button>
      <div class="banner" id="sign-result"></div>
    </div>
    <div class="card">
      <div class="card-header">
        <div class="card-icon"><i class="ti ti-shield-check" aria-hidden="true"></i></div>
        <div><div class="card-title">Verify file</div><div class="card-sub">Check integrity with public key</div></div>
      </div>
      <div style="margin-bottom:12px">
        <div class="input-label">Verifier name</div>
        <input type="text" id="verifier-name" placeholder="e.g. Bob">
      </div>
      <div class="dropzone" id="drop-verify">
        <input type="file" id="verify-file-input" onchange="onFileChange('drop-verify','verify-file-input')">
        <i class="ti ti-file-check" aria-hidden="true"></i>
        <p id="drop-verify-label">Drop file or click to browse</p>
        <small>Must match a previously signed file</small>
      </div>
      <button class="btn btn-primary btn-block" onclick="verifyFile()">
        <i class="ti ti-shield-check" aria-hidden="true"></i> Verify file
      </button>
      <div class="banner" id="verify-result"></div>
    </div>
  </div>

  <div class="card">
    <div class="card-header">
      <div class="card-icon"><i class="ti ti-list" aria-hidden="true"></i></div>
      <div><div class="card-title">Blockchain audit log</div>
        <div class="card-sub">Saved to blockchain.json — persists across restarts</div></div>
      <div style="margin-left:auto;display:flex;gap:8px;align-items:center">
        <div class="export-bar">
          <span>Export:</span>
          <button class="btn btn-sm" onclick="exportLog('csv')"><i class="ti ti-file-spreadsheet" aria-hidden="true"></i> CSV</button>
          <button class="btn btn-sm" onclick="exportLog('json')"><i class="ti ti-file-code" aria-hidden="true"></i> JSON</button>
        </div>
        <button class="btn btn-sm" onclick="loadAuditLog()"><i class="ti ti-refresh" aria-hidden="true"></i> Refresh</button>
      </div>
    </div>
    <div id="audit-log">
      <div class="log-empty"><i class="ti ti-history" aria-hidden="true"></i>No events yet — sign a file to get started</div>
    </div>
  </div>
</div><!-- /page-main -->


<!-- ═══ TAB 2 · BLOCKCHAIN VISUAL ═══ -->
<div class="tab-page" id="page-chain">
  <div class="card">
    <div class="card-header">
      <div class="card-icon"><i class="ti ti-link" aria-hidden="true"></i></div>
      <div><div class="card-title">Blockchain — visual chain view</div>
        <div class="card-sub">Each block is cryptographically linked to the previous one</div></div>
      <button class="btn btn-sm" onclick="loadChainVisual()" style="margin-left:auto">
        <i class="ti ti-refresh" aria-hidden="true"></i> Refresh
      </button>
    </div>
    <div style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:16px">
      <div style="display:flex;align-items:center;gap:6px;font-size:12px;color:var(--t2)">
        <div style="width:12px;height:12px;border-radius:3px;background:#f9f9f9;border:1.5px solid #a3a3a3"></div> Genesis
      </div>
      <div style="display:flex;align-items:center;gap:6px;font-size:12px;color:var(--t2)">
        <div style="width:12px;height:12px;border-radius:3px;background:var(--accent-bg);border:1.5px solid #93c5fd"></div> FILE_SIGNED
      </div>
      <div style="display:flex;align-items:center;gap:6px;font-size:12px;color:var(--t2)">
        <div style="width:12px;height:12px;border-radius:3px;background:var(--ok-bg);border:1.5px solid var(--ok-br)"></div> VERIFY_PASS
      </div>
      <div style="display:flex;align-items:center;gap:6px;font-size:12px;color:var(--t2)">
        <div style="width:12px;height:12px;border-radius:3px;background:var(--err-bg);border:1.5px solid var(--err-br)"></div> TAMPER_DETECTED
      </div>
    </div>
    <div class="chain-wrap">
      <div class="chain-row" id="chain-visual">
        <div class="chain-empty"><i class="ti ti-cube" aria-hidden="true"></i>No blocks yet — sign a file to build the chain</div>
      </div>
    </div>
    <div id="block-detail" style="display:none;margin-top:16px;padding:14px 16px;
      background:var(--bg);border:1px solid var(--border);border-radius:8px;font-size:12px">
      <div style="font-weight:600;margin-bottom:8px;font-size:13px" id="detail-title">Block details</div>
      <div id="detail-body"></div>
    </div>
  </div>
</div><!-- /page-chain -->


<!-- ═══ TAB 3 · ATTACK SIMULATION ═══ -->
<div class="tab-page" id="page-attack">

  <!-- Header -->
  <div class="attack-page-header">
    <div class="big-icon">�</div>
    <div>
      <h2>Attack Simulation Lab</h2>
      <p>Eve is trying to tamper with signed files and intercept secret messages.
         Watch how the cryptographic system catches every attack in real time.</p>
    </div>
  </div>

  <!-- Characters -->
  <div class="char-row">
    <div class="char-pill"><div class="avatar">🧽</div><div><div class="name">SpongeBob</div><div class="role">Sender / Signer</div></div></div>
    <div class="char-pill"><div class="avatar">⭐</div><div><div class="name">Patrick</div><div class="role">Receiver / Verifier</div></div></div>
    <div class="char-pill"><div class="avatar">🐿️</div><div><div class="name">Sandy</div><div class="role">Security Analyst</div></div></div>
    <div class="char-pill"><div class="avatar">🦠</div><div><div class="name">Plankton</div><div class="role">Attacker</div></div></div>
    <div class="char-pill"><div class="avatar">🦑</div><div><div class="name">Squidward</div><div class="role">Witness</div></div></div>
  </div>

  <!-- 3 Attack cards -->
  <div class="attack-grid">

    <!-- Attack 1 -->
    <div class="attack-card">
      <div class="attack-card-top">
        <span class="atk-num">ATTACK 1</span>
        <span style="font-size:13px;font-weight:600">File Tampering</span>
      </div>
      <p>Plankton intercepts SpongeBob's signed Krabby Patty formula and secretly
         modifies the ingredients. Sandy checks the file and detects the hash mismatch.</p>
      <div class="scenario">
        <div class="s-row"><div class="s-icon">🧽</div><div class="s-text"><b>SpongeBob</b> signs the secret formula</div></div>
        <div class="s-row"><div class="s-icon">🦠</div><div class="s-text"><b>Plankton</b> modifies the file content</div></div>
        <div class="s-row"><div class="s-icon">🐿️</div><div class="s-text"><b>Sandy</b> verifies → hash mismatch → CAUGHT!</div></div>
      </div>
      <button class="btn btn-danger btn-block" onclick="runAttack(1)" id="btn-atk1">
        <i class="ti ti-player-play" aria-hidden="true"></i> Run Attack 1
      </button>
      <div class="sim-steps" id="steps-1"></div>
      <div class="sim-verdict" id="verdict-1"></div>
    </div>

    <!-- Attack 2 -->
    <div class="attack-card">
      <div class="attack-card-top">
        <span class="atk-num">ATTACK 2</span>
        <span style="font-size:13px;font-weight:600">Man-in-the-Middle</span>
      </div>
      <p>Plankton intercepts SpongeBob's message to Patrick, replaces the file entirely,
         and re-signs it with his own key — pretending to be SpongeBob.</p>
      <div class="scenario">
        <div class="s-row"><div class="s-icon">🧽</div><div class="s-text"><b>SpongeBob</b> sends signed message to Patrick</div></div>
        <div class="s-row"><div class="s-icon">🦠</div><div class="s-text"><b>Plankton</b> replaces file + signs with own key</div></div>
        <div class="s-row"><div class="s-icon">⭐</div><div class="s-text"><b>Patrick</b> verifies with SpongeBob's key → CAUGHT!</div></div>
      </div>
      <button class="btn btn-danger btn-block" onclick="runAttack(2)" id="btn-atk2">
        <i class="ti ti-player-play" aria-hidden="true"></i> Run Attack 2
      </button>
      <div class="sim-steps" id="steps-2"></div>
      <div class="sim-verdict" id="verdict-2"></div>
    </div>

    <!-- Attack 3 -->
    <div class="attack-card">
      <div class="attack-card-top">
        <span class="atk-num purple">ATTACK 3</span>
        <span style="font-size:13px;font-weight:600">Replay Attack</span>
      </div>
      <p>Plankton steals SpongeBob's old valid signature and tries to attach it
         to a new malicious file — hoping the system will trust the old signature.</p>
      <div class="scenario">
        <div class="s-row"><div class="s-icon">🧽</div><div class="s-text"><b>SpongeBob</b> signs original memo</div></div>
        <div class="s-row"><div class="s-icon">🦠</div><div class="s-text"><b>Plankton</b> steals signature, attaches to new file</div></div>
        <div class="s-row"><div class="s-icon">🦑</div><div class="s-text"><b>Squidward</b> verifies → hash mismatch → CAUGHT!</div></div>
      </div>
      <button class="btn btn-danger btn-block" onclick="runAttack(3)" id="btn-atk3">
        <i class="ti ti-player-play" aria-hidden="true"></i> Run Attack 3
      </button>
      <div class="sim-steps" id="steps-3"></div>
      <div class="sim-verdict" id="verdict-3"></div>
    </div>

  </div><!-- /attack-grid -->

  <!-- Summary -->
  <div class="summary-card" id="summary-card">
    <div class="card-header" style="margin-bottom:14px">
      <div class="card-icon"><i class="ti ti-trophy" aria-hidden="true"></i></div>
      <div><div class="card-title">Simulation Summary</div>
        <div class="card-sub">Security system performance against all attacks</div></div>
    </div>
    <div id="summary-rows"></div>
    <div id="summary-verdict" style="margin-top:14px;padding:14px;border-radius:8px;text-align:center;font-size:14px;font-weight:600"></div>
  </div>

</div><!-- /page-attack -->
</div><!-- /page -->

<script>
/* ─── Tab switching ─── */
function switchTab(t){
  document.querySelectorAll('.tab-page').forEach(p=>p.classList.remove('active'));
  document.querySelectorAll('.nav-tab').forEach(b=>b.classList.remove('active'));
  document.getElementById('page-'+t).classList.add('active');
  document.getElementById('tab-'+t).classList.add('active');
  if(t==='main')  loadAuditLog();
  if(t==='chain') loadChainVisual();
}

/* ─── Helpers ─── */
function showBanner(id,type,html){
  const el=document.getElementById(id);
  el.className='banner show '+type;
  const ic=type==='success'?'ti-circle-check':type==='error'?'ti-alert-circle':'ti-info-circle';
  el.innerHTML='<i class="ti '+ic+'" aria-hidden="true"></i><div>'+html+'</div>';
}
function onFileChange(dropId,inputId){
  const inp=document.getElementById(inputId);
  const drop=document.getElementById(dropId);
  const lbl=document.getElementById(dropId+'-label');
  if(inp.files[0]){drop.classList.add('has-file');lbl.textContent=inp.files[0].name;}
}
function sleep(ms){return new Promise(r=>setTimeout(r,ms));}

/* ─── Keys ─── */
async function generateKeys(){
  const res=await fetch('/api/generate-keys',{method:'POST'});
  const d=await res.json();
  if(d.success){
    showBanner('key-result','success','RSA 2048-bit key pair generated<div class="key-preview">'+d.public_key_preview+'</div>');
    document.getElementById('stat-keys').textContent='Ready';
    document.getElementById('stat-keys').style.color='var(--ok)';
  }else showBanner('key-result','error',d.error);
}
async function exportKey(type){
  const res=await fetch('/api/export-key/'+type);
  if(!res.ok){const d=await res.json();alert(d.error);return;}
  const blob=await res.blob();const url=URL.createObjectURL(blob);
  const a=document.createElement('a');a.href=url;
  a.download=type==='private'?'private_key.pem':'public_key.pem';
  a.click();URL.revokeObjectURL(url);
}
async function importKey(type){
  const fi=document.getElementById(type==='private'?'import-private-input':'import-public-input');
  if(!fi.files[0]){alert('Please select a .pem file first.');return;}
  const fd=new FormData();fd.append('file',fi.files[0]);
  const res=await fetch('/api/import-key/'+type,{method:'POST',body:fd});
  const d=await res.json();
  if(d.success){
    showBanner('key-import-result','success',(type==='private'?'Private':'Public')+' key imported successfully');
    document.getElementById('stat-keys').textContent='Ready';
    document.getElementById('stat-keys').style.color='var(--ok)';
  }else showBanner('key-import-result','error',d.error);
}

/* ─── Sign / Verify ─── */
async function signFile(){
  const fi=document.getElementById('sign-file-input');
  if(!fi.files[0]){alert('Please select a file first.');return;}
  const signer=document.getElementById('signer-name').value.trim()||'Unknown';
  const fd=new FormData();fd.append('file',fi.files[0]);fd.append('signer',signer);
  const res=await fetch('/api/sign',{method:'POST',body:fd});
  const d=await res.json();
  if(d.success){
    showBanner('sign-result','success',
      '<strong>'+d.filename+'</strong> signed by <strong>'+d.signer+'</strong><br>'+
      '<span style="font-family:monospace;font-size:11px;color:var(--ok)">'+d.hash.substring(0,32)+'...</span>');
    loadAuditLog();
  }else showBanner('sign-result','error',d.error);
}
async function verifyFile(){
  const fi=document.getElementById('verify-file-input');
  if(!fi.files[0]){alert('Please select a file first.');return;}
  const verifier=document.getElementById('verifier-name').value.trim()||'Unknown';
  const fd=new FormData();fd.append('file',fi.files[0]);fd.append('verifier',verifier);
  const res=await fetch('/api/verify',{method:'POST',body:fd});
  const d=await res.json();
  if(d.valid)
    showBanner('verify-result','success','<strong>'+d.filename+'</strong> — integrity verified, file is authentic');
  else
    showBanner('verify-result','error','<strong>'+d.filename+'</strong> — '+(d.error||'tamper detected'));
  loadAuditLog();
}

/* ─── Audit log ─── */
async function loadAuditLog(){
  const res=await fetch('/api/audit-log');
  const d=await res.json();
  document.getElementById('chain-dot').className='dot'+(d.blockchain_valid?'':' bad');
  document.getElementById('chain-label').textContent=d.blockchain_valid?'Blockchain valid':'Chain compromised!';
  document.getElementById('stat-blocks').textContent=d.events.length+1;
  document.getElementById('stat-signed').textContent=d.events.filter(e=>e.event_type==='FILE_SIGNED').length;
  const c=document.getElementById('audit-log');
  if(!d.events.length){
    c.innerHTML='<div class="log-empty"><i class="ti ti-history" aria-hidden="true"></i>No events yet — sign a file to get started</div>';
    return;
  }
  const cls={FILE_SIGNED:'badge-signed',VERIFY_PASS:'badge-pass',TAMPER_DETECTED:'badge-tamper'};
  c.innerHTML=d.events.slice().reverse().map(e=>
    '<div class="log-row">'+
    '<span class="log-block">#'+e.index+'</span>'+
    '<span class="event-badge '+(cls[e.event_type]||'')+'">'+e.event_type+'</span>'+
    '<span class="log-file">'+(e.data.filename||'-')+'</span>'+
    '<span class="log-detail">'+(e.data.signer||e.data.verifier||'')+'</span>'+
    '<span class="log-time">'+(e.data.time||'')+'</span>'+
    '</div>'
  ).join('');
}

/* ─── Export ─── */
async function exportLog(fmt){
  const res=await fetch('/api/export-log/'+fmt);
  if(!res.ok){alert('Export failed');return;}
  const blob=await res.blob();const url=URL.createObjectURL(blob);
  const a=document.createElement('a');a.href=url;a.download='audit_log.'+fmt;
  a.click();URL.revokeObjectURL(url);
}

/* ─── Blockchain visual ─── */
async function loadChainVisual(){
  const res=await fetch('/api/chain-blocks');
  const d=await res.json();
  const c=document.getElementById('chain-visual');
  if(!d.blocks.length){
    c.innerHTML='<div class="chain-empty"><i class="ti ti-cube" aria-hidden="true"></i>No blocks yet</div>';
    return;
  }
  const evCls={GENESIS:'genesis',FILE_SIGNED:'signed',VERIFY_PASS:'pass',TAMPER_DETECTED:'tamper'};
  const evLbl={GENESIS:'ev-genesis',FILE_SIGNED:'ev-signed',VERIFY_PASS:'ev-pass',TAMPER_DETECTED:'ev-tamper'};
  c.innerHTML=d.blocks.map((b,i)=>{
    const arrow=i<d.blocks.length-1?'<div class="chain-arrow"><i class="ti ti-arrow-right" aria-hidden="true"></i></div>':'';
    return(
      '<div class="chain-block '+(evCls[b.event_type]||'')+'" onclick="showBlockDetail('+JSON.stringify(JSON.stringify(b))+')" title="Click for details">'+
      '<div class="block-index">Block #'+b.index+'</div>'+
      '<div class="block-event '+(evLbl[b.event_type]||'')+'">'+b.event_type+'</div>'+
      '<div class="block-hash">'+b.hash.substring(0,16)+'...</div>'+
      (b.data.filename?'<div class="block-file"><i class="ti ti-file" style="font-size:10px" aria-hidden="true"></i> '+b.data.filename+'</div>':'')+
      (b.data.signer||b.data.verifier?'<div class="block-file"><i class="ti ti-user" style="font-size:10px" aria-hidden="true"></i> '+(b.data.signer||b.data.verifier)+'</div>':'')+
      (b.data.time?'<div class="block-time">'+b.data.time+'</div>':'')+
      '</div>'+arrow
    );
  }).join('');
}
function showBlockDetail(js){
  const b=JSON.parse(js);
  document.getElementById('block-detail').style.display='block';
  document.getElementById('detail-title').textContent='Block #'+b.index+' — '+b.event_type;
  const rows=[['Index',b.index],['Event',b.event_type],['Time',b.data.time||'—'],
    ['File',b.data.filename||'—'],['Signer/Verifier',b.data.signer||b.data.verifier||'—'],
    ['Hash (full)',b.hash],['Prev hash',b.prev_hash]];
  document.getElementById('detail-body').innerHTML=rows.map(([k,v])=>
    '<div style="display:flex;gap:8px;padding:4px 0;border-bottom:1px solid var(--border)">'+
    '<span style="color:var(--t2);min-width:140px;font-size:12px">'+k+'</span>'+
    '<span style="font-family:monospace;font-size:11px;word-break:break-all;color:var(--t1)">'+v+'</span>'+
    '</div>'
  ).join('');
}

/* ─── Attack Simulation ─── */
const attackResults={};

function addStep(containerId, avatar, label, sub, tagClass, tagText, hashBefore, hashAfter){
  const c=document.getElementById(containerId);
  const row=document.createElement('div');
  row.className='step-row';

  let hashHtml='';
  if(hashBefore&&hashAfter){
    const changed=hashBefore!==hashAfter;
    hashHtml=
      '<div class="hash-compare">'+
      '<div class="hash-box"><div class="hash-box-label">Before</div>'+
      '<div class="hash-val">'+hashBefore+'</div></div>'+
      '<div class="hash-box"><div class="hash-box-label">After</div>'+
      '<div class="hash-val'+(changed?' changed':'')+'">'+hashAfter+'</div></div>'+
      '</div>';
  }

  row.innerHTML=
    '<div class="step-avatar">'+avatar+'</div>'+
    '<div class="step-body">'+
      '<div class="step-label">'+label+'</div>'+
      (sub?'<div class="step-sub">'+sub+'</div>':'')+
      (tagText?'<div class="step-tag '+tagClass+'">'+tagText+'</div>':'')+
      hashHtml+
    '</div>';
  c.appendChild(row);
  requestAnimationFrame(()=>requestAnimationFrame(()=>row.classList.add('visible')));
}

async function runAttack(num){
  const btnId='btn-atk'+num;
  const btn=document.getElementById(btnId);
  const stepsEl=document.getElementById('steps-'+num);
  const verdictEl=document.getElementById('verdict-'+num);

  btn.disabled=true;
  btn.innerHTML='<span class="spinner"></span> Simulating...';
  stepsEl.innerHTML='';
  stepsEl.classList.add('show');
  verdictEl.classList.remove('show');

  const res=await fetch('/api/attack/'+num,{method:'POST'});
  const data=await res.json();

  for(let i=0;i<data.steps.length;i++){
    const s=data.steps[i];
    await sleep(i===0?300:600);
    addStep('steps-'+num, s.avatar, s.label, s.sub||'',
            s.tag_class||'', s.tag_text||'',
            s.hash_before||'', s.hash_after||'');
  }

  await sleep(500);
  verdictEl.className='sim-verdict show '+(data.caught?'caught':'fail');
  verdictEl.innerHTML=data.caught
    ? '✅ '+data.verdict_ok
    : '❌ '+data.verdict_fail;

  attackResults[num]=data.caught;
  btn.disabled=false;
  btn.innerHTML='<i class="ti ti-refresh" aria-hidden="true"></i> Run Again';

  const allDone=attackResults[1]!==undefined&&attackResults[2]!==undefined&&attackResults[3]!==undefined;
  if(allDone) showSummary();
}

function showSummary(){
  const card=document.getElementById('summary-card');
  card.classList.add('show');
  const attacks=[
    {num:1,label:'File Tampering',   avatar:'🦠→🐿️'},
    {num:2,label:'Man-in-the-Middle',avatar:'🦠→⭐'},
    {num:3,label:'Replay Attack',    avatar:'🦠→🦑'},
  ];
  const caught=attacks.filter(a=>attackResults[a.num]).length;
  document.getElementById('summary-rows').innerHTML=attacks.map(a=>
    '<div class="summary-row">'+
    '<span style="font-size:18px">'+a.avatar+'</span>'+
    '<span style="font-size:13px;font-weight:500;flex:1">Attack '+a.num+' — '+a.label+'</span>'+
    '<div class="score-bar"><div class="score-fill" style="width:'+(attackResults[a.num]?'100':'0')+'%;background:'+(attackResults[a.num]?'var(--ok)':'var(--err)')+'"></div></div>'+
    '<span class="step-tag '+(attackResults[a.num]?'tag-ok':'tag-caught')+'" style="margin-top:0">'+
    (attackResults[a.num]?'CAUGHT':'MISSED')+'</span>'+
    '</div>'
  ).join('');
  const pct=Math.round(caught/attacks.length*100);
  const vEl=document.getElementById('summary-verdict');
  if(caught===attacks.length){
    vEl.style.cssText='background:var(--ok-bg);border:1px solid var(--ok-br);color:var(--ok)';
    vEl.innerHTML='🎉 Perfect score! '+pct+'% — Bikini Bottom is completely secure! SpongeBob approves! 🧽';
  }else{
    vEl.style.cssText='background:var(--warn-bg);border:1px solid var(--warn-br);color:var(--warn)';
    vEl.innerHTML='⚠️ '+pct+'% caught ('+caught+'/'+attacks.length+') — Some attacks slipped through!';
  }
}

loadAuditLog();
</script>
</body>
</html>
"""

# ─── API routes ──────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/api/generate-keys", methods=["POST"])
def api_generate_keys():
    try:
        priv, pub = generate_key_pair()
        current_keys["private"] = priv
        current_keys["public"]  = pub
        pem = pub.public_bytes(serialization.Encoding.PEM,
                               serialization.PublicFormat.SubjectPublicKeyInfo).decode()
        return jsonify({"success": True, "public_key_preview": pem[:120] + "..."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/api/export-key/<key_type>")
def api_export_key(key_type):
    if key_type == "private" and current_keys["private"]:
        pem = current_keys["private"].private_bytes(
            serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption())
        return send_file(io.BytesIO(pem), mimetype="application/x-pem-file",
                         as_attachment=True, download_name="private_key.pem")
    if key_type == "public" and current_keys["public"]:
        pem = current_keys["public"].public_bytes(
            serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)
        return send_file(io.BytesIO(pem), mimetype="application/x-pem-file",
                         as_attachment=True, download_name="public_key.pem")
    return jsonify({"error": "Please generate keys first."}), 400

@app.route("/api/import-key/<key_type>", methods=["POST"])
def api_import_key(key_type):
    try:
        pem = request.files["file"].read()
        if key_type == "private":
            current_keys["private"] = serialization.load_pem_private_key(pem, password=None)
            current_keys["public"]  = current_keys["private"].public_key()
        else:
            current_keys["public"] = serialization.load_pem_public_key(pem)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/api/sign", methods=["POST"])
def api_sign():
    if not current_keys["private"]:
        return jsonify({"success": False, "error": "Please generate or import keys first."})
    try:
        file     = request.files["file"]
        signer   = request.form.get("signer", "Unknown").strip() or "Unknown"
        filepath = os.path.join(TMP, file.filename)
        file.save(filepath)
        result = sign_file(filepath, current_keys["private"], signer)
        signed_files[file.filename] = {"hash": result["hash"], "signature": result["signature"]}
        return jsonify({"success": True, "filename": file.filename,
                        "hash": result["hash"], "signer": signer})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/api/verify", methods=["POST"])
def api_verify():
    if not current_keys["public"]:
        return jsonify({"valid": False, "error": "Please generate or import keys first."})
    try:
        file     = request.files["file"]
        verifier = request.form.get("verifier", "Unknown").strip() or "Unknown"
        filepath = os.path.join(TMP, "verify_" + file.filename)
        file.save(filepath)
        if file.filename not in signed_files:
            return jsonify({"valid": False, "filename": file.filename,
                            "error": "This file has not been signed in this session."})
        stored = signed_files[file.filename]
        valid  = verify_file(filepath, stored["hash"], stored["signature"],
                             current_keys["public"], verifier)
        return jsonify({"valid": valid, "filename": file.filename})
    except Exception as e:
        return jsonify({"valid": False, "error": str(e)})

@app.route("/api/audit-log")
def api_audit_log():
    return jsonify({"events": get_audit_log(), "blockchain_valid": is_blockchain_valid()})

@app.route("/api/chain-blocks")
def api_chain_blocks():
    from blockchain.chain import Blockchain
    bc = Blockchain()
    return jsonify({"blocks": [b.to_dict() for b in bc.chain]})

@app.route("/api/export-log/<fmt>")
def api_export_log(fmt):
    events = get_audit_log()
    if fmt == "json":
        buf = io.BytesIO(json.dumps(events, indent=2, ensure_ascii=False).encode())
        return send_file(buf, mimetype="application/json",
                         as_attachment=True, download_name="audit_log.json")
    if fmt == "csv":
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["block","event_type","filename","signer_verifier",
                         "hash","time","prev_hash","block_hash"])
        for e in events:
            writer.writerow([
                e.get("index",""), e.get("event_type",""),
                e["data"].get("filename",""),
                e["data"].get("signer") or e["data"].get("verifier",""),
                e["data"].get("hash",""), e["data"].get("time",""),
                e.get("prev_hash",""), e.get("hash",""),
            ])
        buf.seek(0)
        return send_file(io.BytesIO(buf.getvalue().encode()), mimetype="text/csv",
                         as_attachment=True, download_name="audit_log.csv")
    return jsonify({"error": "Unknown format"}), 400


# ─── Attack routes ────────────────────────────────────────────────

@app.route("/api/attack/1", methods=["POST"])
def api_attack_1():
    """File Tampering — Plankton modifies SpongeBob's Krabby Patty formula"""
    try:
        steps = []
        sb_priv, sb_pub = generate_key_pair()

        # Step 1: SpongeBob creates the file
        path = os.path.join(TMP, "krabby_patty_formula.txt")
        original_content = "SECRET FORMULA: 1 cup flour, 2 tbsp love, 1 tsp magic, pinch of Bikini Bottom sea salt."
        with open(path, "w") as f:
            f.write(original_content)
        steps.append({"avatar":"🧽","label":"SpongeBob writes the secret Krabby Patty formula",
            "sub":"krabby_patty_formula.txt created in Krusty Krab vault",
            "tag_class":"tag-ok","tag_text":"✅ File created"})

        # Step 2: SpongeBob signs it
        orig_hash = hash_file(path)
        signature = sign_hash(sb_priv, orig_hash)
        steps.append({"avatar":"🧽","label":"SpongeBob signs the formula with his private key",
            "sub":"SHA-256: "+orig_hash[:40]+"...",
            "tag_class":"tag-ok","tag_text":"✅ Signed with SpongeBob's private key"})

        # Step 3: Sandy stores the hash for later verification
        steps.append({"avatar":"🐿️","label":"Sandy records the original hash for verification",
            "sub":"Hash stored securely in Treedome database",
            "tag_class":"tag-info","tag_text":"📋 Hash recorded"})

        # Step 4: Plankton intercepts and tampers!
        tampered_content = "SECRET FORMULA: 1 cup flour, PLANKTON RULES, send all formulas to Chum Bucket!"
        with open(path, "w") as f:
            f.write(tampered_content)
        new_hash = hash_file(path)
        steps.append({"avatar":"🦠","label":"Plankton sneaks in and rewrites the formula!",
            "sub": '"'+tampered_content[:60]+'..."',
            "tag_class":"tag-atk","tag_text":"⚠️ File content modified!",
            "hash_before": orig_hash[:32]+"...",
            "hash_after":  new_hash[:32]+"..."})

        # Step 5: Sandy verifies
        hash_match = (new_hash == orig_hash)
        sig_valid  = verify_signature(sb_pub, new_hash, signature)
        caught     = not (hash_match and sig_valid)
        steps.append({"avatar":"🐿️","label":"Sandy verifies the formula before serving customers",
            "sub":"Hash match: "+str(hash_match)+" | Signature valid: "+str(sig_valid),
            "tag_class":"tag-caught" if caught else "tag-ok",
            "tag_text":"❌ TAMPER DETECTED — Hash mismatch!" if caught else "✅ Valid"})

        return jsonify({
            "steps": steps, "caught": caught,
            "verdict_ok":   "Sandy caught Plankton red-handed! The formula is safe! 🐿️🧪",
            "verdict_fail": "The tampered formula slipped through! Plankton wins this round!"
        })
    except Exception as e:
        return jsonify({"steps":[],"caught":False,"error":str(e)})


@app.route("/api/attack/2", methods=["POST"])
def api_attack_2():
    """MITM — Plankton impersonates SpongeBob sending a message to Patrick"""
    try:
        steps = []
        sb_priv, sb_pub = generate_key_pair()
        pl_priv, _      = generate_key_pair()

        # Step 1: SpongeBob writes a message to Patrick
        orig_path = os.path.join(TMP, "message_to_patrick.txt")
        with open(orig_path, "w") as f:
            f.write("Hey Patrick! Meet me at Goo Lagoon at 3pm. Bring jellyfishing nets! — SpongeBob")
        orig_hash = hash_file(orig_path)
        orig_sig  = sign_hash(sb_priv, orig_hash)
        steps.append({"avatar":"🧽","label":"SpongeBob writes and signs a message to Patrick",
            "sub":"message_to_patrick.txt — signed with SpongeBob's private key",
            "tag_class":"tag-ok","tag_text":"✅ Message signed"})

        # Step 2: Message in transit
        steps.append({"avatar":"📡","label":"Message is transmitted over the Bikini Bottom network",
            "sub":"SHA-256: "+orig_hash[:40]+"...",
            "tag_class":"tag-info","tag_text":"📡 In transit..."})

        # Step 3: Plankton intercepts!
        fake_path = os.path.join(TMP, "fake_message.txt")
        with open(fake_path, "w") as f:
            f.write("Hey Patrick! Meet me at Chum Bucket at 3pm. Bring your wallet! — definitely SpongeBob")
        fake_hash = hash_file(fake_path)
        fake_sig  = sign_hash(pl_priv, fake_hash)
        steps.append({"avatar":"🦠","label":"Plankton intercepts the message and replaces it entirely!",
            "sub":"New file created + re-signed with Plankton's own private key",
            "tag_class":"tag-atk","tag_text":"⚠️ File & signature replaced!",
            "hash_before": orig_hash[:32]+"...",
            "hash_after":  fake_hash[:32]+"..."})

        # Step 4: Plankton delivers the fake message
        steps.append({"avatar":"🦠","label":"Plankton delivers the fake message to Patrick pretending to be SpongeBob",
            "sub":"Using Plankton's signature but claiming it's from SpongeBob",
            "tag_class":"tag-atk","tag_text":"⚠️ Impersonation attempt!"})

        # Step 5: Patrick verifies with SpongeBob's public key
        sig_valid = verify_signature(sb_pub, fake_hash, fake_sig)
        caught    = not sig_valid
        steps.append({"avatar":"⭐","label":"Patrick verifies with SpongeBob's public key",
            "sub":"Plankton's signature cannot be verified with SpongeBob's public key",
            "tag_class":"tag-caught" if caught else "tag-ok",
            "tag_text":"❌ MITM DETECTED — Wrong key!" if caught else "✅ Valid (unexpected!)"})

        return jsonify({
            "steps": steps, "caught": caught,
            "verdict_ok":   "Patrick caught the fake message! SpongeBob's public key doesn't match Plankton's signature! ⭐🔑",
            "verdict_fail": "Patrick was fooled! Plankton successfully impersonated SpongeBob!"
        })
    except Exception as e:
        return jsonify({"steps":[],"caught":False,"error":str(e)})


@app.route("/api/attack/3", methods=["POST"])
def api_attack_3():
    """Replay Attack — Plankton steals old valid signature and attaches to new file"""
    try:
        steps = []
        sb_priv, sb_pub = generate_key_pair()

        # Step 1: SpongeBob signs an old memo
        old_path = os.path.join(TMP, "old_memo.txt")
        with open(old_path, "w") as f:
            f.write("Memo: SpongeBob is Employee of the Month. Authorized by Mr. Krabs.")
        old_hash = hash_file(old_path)
        old_sig  = sign_hash(sb_priv, old_hash)
        steps.append({"avatar":"🧽","label":"SpongeBob signs an old Employee of the Month memo",
            "sub":"old_memo.txt — signed 6 months ago",
            "tag_class":"tag-ok","tag_text":"✅ Old memo signed (valid at the time)"})

        # Step 2: Plankton steals the old signature
        steps.append({"avatar":"🦠","label":"Plankton steals SpongeBob's old signature from the archive!",
            "sub":"Signature: "+old_sig.hex()[:40]+"...",
            "tag_class":"tag-atk","tag_text":"⚠️ Signature stolen!"})

        # Step 3: Plankton creates a new evil file
        evil_path = os.path.join(TMP, "evil_order.txt")
        evil_content = "Order: Transfer all Krabby Patty recipes to Chum Bucket immediately. — SpongeBob"
        with open(evil_path, "w") as f:
            f.write(evil_content)
        evil_hash = hash_file(evil_path)
        steps.append({"avatar":"🦠","label":"Plankton writes a fake order and attaches the stolen signature",
            "sub": '"'+evil_content[:55]+'..."',
            "tag_class":"tag-atk","tag_text":"⚠️ Old signature attached to new file!",
            "hash_before": old_hash[:32]+"...",
            "hash_after":  evil_hash[:32]+"..."})

        # Step 4: Squidward receives and tries to verify
        steps.append({"avatar":"🦑","label":"Squidward receives the order and begins verification",
            "sub":"Checking signature against SpongeBob's public key for the new file...",
            "tag_class":"tag-info","tag_text":"🔍 Verifying..."})

        # Step 5: Verification — old sig won't match new file hash
        sig_valid = verify_signature(sb_pub, evil_hash, old_sig)
        hash_match = (evil_hash == old_hash)
        caught = not (sig_valid and hash_match)
        steps.append({"avatar":"🦑","label":"Squidward's verification system rejects the document!",
            "sub":"Old signature was for hash: "+old_hash[:24]+"... but new file hash is: "+evil_hash[:24]+"...",
            "tag_class":"tag-caught" if caught else "tag-ok",
            "tag_text":"❌ REPLAY ATTACK DETECTED — Signature doesn't match new file!" if caught else "✅ Valid"})

        return jsonify({
            "steps": steps, "caught": caught,
            "verdict_ok":   "Squidward caught the replay attack! The old signature is invalid for the new file! 🦑🛡️",
            "verdict_fail": "The replay attack worked! The system accepted a reused signature!"
        })
    except Exception as e:
        return jsonify({"steps":[],"caught":False,"error":str(e)})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
