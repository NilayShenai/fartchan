import hashlib
import json
import time
from database import Database

class Blockchain:
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.difficulty = 4  # Adjustable difficulty
        self.block_time_target = 10  # Target time per block in seconds
        self.db = Database()
        self.create_genesis_block()

    def create_genesis_block(self):
        """Creates the genesis block."""
        genesis_block = {
            "index": 1,
            "timestamp": str(time.time()),
            "transactions": [],
            "proof": 100,
            "previous_hash": "0"
        }
        self.chain.append(genesis_block)

    def add_transaction(self, sender, recipient, amount):
        """
        Adds a transaction to the list of pending transactions.
        Does NOT require a signature in this version.
        """
        # Prevent spending more than available (unless sender is "Network")
        if sender != "Network" and self.db.get_balance(sender) < int(amount):
            return False
        self.transactions.append({
            "sender": sender,
            "recipient": recipient,
            "amount": amount
        })
        self.db.add_transaction(sender, recipient, amount)
        return True

    def proof_of_work(self, last_proof):
        """Performs Proof-of-Work mining."""
        proof = 0
        while not self.is_valid_proof(last_proof, proof):
            proof += 1
        return proof

    def is_valid_proof(self, last_proof, proof):
        guess = f"{last_proof}{proof}".encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:self.difficulty] == "0" * self.difficulty

    def adjust_difficulty(self):
        """Adjusts the mining difficulty based on the time taken to mine the last block."""
        if len(self.chain) < 2:
            return
        last_time = float(self.chain[-1]['timestamp'])
        prev_time = float(self.chain[-2]['timestamp'])
        actual_time = last_time - prev_time
        if actual_time < self.block_time_target:
            self.difficulty += 1
        elif actual_time > self.block_time_target:
            self.difficulty = max(1, self.difficulty - 1)

    def hash(self, block):
        """Creates a SHA-256 hash of a block."""
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def create_block(self, proof, previous_hash):
        """Creates a new block and adds it to the chain."""
        block = {
            "index": len(self.chain) + 1,
            "timestamp": str(time.time()),
            "transactions": self.transactions,
            "proof": proof,
            "previous_hash": previous_hash
        }
        self.chain.append(block)
        self.transactions = []  # Reset pending transactions
        self.adjust_difficulty()
        return block
