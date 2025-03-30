import os
import json
import sqlite3
import time
from ecdsa import SigningKey, SECP256k1

class Wallet:
    def __init__(self, filename=None, db_name="blockchain.db"):
        """ Generate or load a wallet. """
        self.db_name = db_name
        if filename and os.path.exists(filename):
            self.load_wallet(filename)
        else:
            self.create_wallet()

    def create_wallet(self):
        """ Create a new wallet and save it. """
        self.private_key = SigningKey.generate(curve=SECP256k1)
        self.public_key = self.private_key.get_verifying_key()
        
        filename = f"wallet_{int(time.time())}.json"  # Unique wallet file
        self.save_keys(filename)
        print(f"\nNew Wallet Created! File: {filename}")
        print(f"Public Key: {self.public_key.to_string().hex()}")

        self.register_wallet()

    def save_keys(self, filename):
        """ Save wallet keys to a JSON file. """
        keys = {
            "private_key": self.private_key.to_string().hex(),
            "public_key": self.public_key.to_string().hex()
        }
        with open(filename, "w") as f:
            json.dump(keys, f)

    def load_wallet(self, filename):
        """ Load an existing wallet from file. """
        with open(filename, "r") as f:
            keys = json.load(f)
            self.private_key = SigningKey.from_string(bytes.fromhex(keys["private_key"]), curve=SECP256k1)
            self.public_key = self.private_key.get_verifying_key()
        print(f"\nLoaded Wallet: {filename}")
        print(f"Public Key: {self.public_key.to_string().hex()}")

    @staticmethod
    def load_keys(filename):
        """ Load keys from a given wallet file. """
        if not os.path.exists(filename):
            print("Wallet file not found!")
            return None

        with open(filename, "r") as f:
            return json.load(f)

    def register_wallet(self):
        """ Store the wallet in the database. """
        public_key_hex = self.public_key.to_string().hex()
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO wallets (public_key) VALUES (?)", (public_key_hex,))
            conn.commit()

    @staticmethod
    def list_wallets(db_name="blockchain.db"):
        """ List all registered wallets. """
        with sqlite3.connect(db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT public_key FROM wallets")
            wallets = cursor.fetchall()
            return [wallet[0] for wallet in wallets]

if __name__ == "__main__":
    wallet = Wallet()