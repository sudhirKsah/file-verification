"""
blockchain/chain.py
Blockchain audit trail with JSON persistence
"""

import hashlib
import json
import time
import os


CHAIN_FILE = os.path.join(os.path.dirname(__file__), "..", "blockchain.json")


class Block:
    def __init__(self, index, event_type, data, prev_hash, timestamp=None):
        self.index      = index
        self.timestamp  = timestamp or time.time()
        self.event_type = event_type
        self.data       = data
        self.prev_hash  = prev_hash
        self.hash       = self._calculate_hash()

    def _calculate_hash(self) -> str:
        content = json.dumps({
            "index":      self.index,
            "timestamp":  self.timestamp,
            "event_type": self.event_type,
            "data":       self.data,
            "prev_hash":  self.prev_hash
        }, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()

    def to_dict(self) -> dict:
        return {
            "index":      self.index,
            "timestamp":  self.timestamp,
            "event_type": self.event_type,
            "data":       self.data,
            "prev_hash":  self.prev_hash,
            "hash":       self.hash
        }

    @classmethod
    def from_dict(cls, d: dict):
        """Create a Block from a dictionary loaded from JSON."""
        block = cls(
            index      = d["index"],
            event_type = d["event_type"],
            data       = d["data"],
            prev_hash  = d["prev_hash"],
            timestamp  = d["timestamp"]
        )
        block.hash = d["hash"]
        return block


class Blockchain:
    def __init__(self):
        self.chain = []
        self._load_or_create()

    def _load_or_create(self):
        """Load the chain from a file if it exists; otherwise create one."""
        if os.path.exists(CHAIN_FILE):
            try:
                with open(CHAIN_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.chain = [Block.from_dict(b) for b in data]
                print(f"✅ Loaded blockchain: {len(self.chain)} blocks from {CHAIN_FILE}")
                return
            except Exception as e:
                print(f"⚠️  Could not load blockchain file: {e} — starting fresh")

        self._create_genesis_block()
        self._save()

    def _create_genesis_block(self):
        genesis = Block(
            index      = 0,
            event_type = "GENESIS",
            data       = {"message": "Blockchain initialized"},
            prev_hash  = "0000"
        )
        self.chain.append(genesis)

    def _save(self):
        """Save the complete chain to JSON."""
        try:
            with open(CHAIN_FILE, "w", encoding="utf-8") as f:
                json.dump([b.to_dict() for b in self.chain], f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️  Could not save blockchain: {e}")

    def add_event(self, event_type: str, data: dict) -> Block:
        prev_block = self.chain[-1]
        new_block  = Block(
            index      = len(self.chain),
            event_type = event_type,
            data       = data,
            prev_hash  = prev_block.hash
        )
        self.chain.append(new_block)
        self._save()  # Save immediately after every event.
        return new_block

    def is_valid(self) -> bool:
        for i in range(1, len(self.chain)):
            cur  = self.chain[i]
            prev = self.chain[i - 1]
            if cur.hash != cur._calculate_hash():
                return False
            if cur.prev_hash != prev.hash:
                return False
        return True

    def get_all_events(self) -> list:
        return [b.to_dict() for b in self.chain[1:]]

    def print_chain(self):
        for b in self.chain:
            print(f"\n Block #{b.index} [{b.event_type}]")
            print(f"   prev : {b.prev_hash[:16]}...")
            print(f"   hash : {b.hash[:16]}...")
            print(f"   data : {b.data}")
