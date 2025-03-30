import sqlite3
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class Database:
    def __init__(self, db_name="blockchain.db"):
        """Initialize database connection, enable WAL mode, and create tables."""
        self.db_name = db_name
        self.enable_wal()
        self.create_tables()

    def enable_wal(self):
        """Enable SQLite Write-Ahead Logging (WAL) to prevent database locking."""
        try:
            with sqlite3.connect(self.db_name, timeout=15, isolation_level=None) as conn:
                conn.execute("PRAGMA journal_mode=WAL;")
                logging.info("WAL mode enabled.")
        except sqlite3.Error as e:
            logging.error(f"Failed to enable WAL mode: {e}")

    def create_tables(self):
        """Create necessary tables for the blockchain."""
        try:
            with sqlite3.connect(self.db_name, timeout=15, isolation_level=None) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS wallets (
                        public_key TEXT PRIMARY KEY
                    )
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS balances (
                        public_key TEXT PRIMARY KEY,
                        balance REAL DEFAULT 0
                    )
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        sender TEXT NOT NULL,
                        recipient TEXT NOT NULL,
                        amount REAL NOT NULL CHECK (amount > 0),
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                logging.info("Database tables created successfully.")

        except sqlite3.Error as e:
            logging.error(f"Database error: {e}")

    def register_wallet(self, public_key):
        """Register a new wallet with an initial balance of 0."""
        try:
            with sqlite3.connect(self.db_name, timeout=15, isolation_level=None) as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT OR IGNORE INTO wallets (public_key) VALUES (?)", (public_key,))
                cursor.execute("INSERT OR IGNORE INTO balances (public_key, balance) VALUES (?, 0)", (public_key,))
                logging.info(f"Wallet registered: {public_key}")

        except sqlite3.Error as e:
            logging.error(f"Failed to register wallet: {e}")

    def update_balance(self, public_key, amount):
        """Update or insert balance for a given public key."""
        try:
            with sqlite3.connect(self.db_name, timeout=15, isolation_level=None) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT balance FROM balances WHERE public_key = ?", (public_key,))
                result = cursor.fetchone()

                if result:
                    new_balance = result[0] + amount
                    if new_balance < 0:
                        logging.warning(f"Insufficient funds for {public_key}")
                        return False  # Prevent overdrafts
                    cursor.execute("UPDATE balances SET balance = ? WHERE public_key = ?", (new_balance, public_key))
                else:
                    if amount < 0:
                        logging.warning(f"Cannot create a wallet with negative balance: {public_key}")
                        return False
                    new_balance = amount  # Ensure new_balance is always defined
                    cursor.execute("INSERT INTO balances (public_key, balance) VALUES (?, ?)", (public_key, new_balance))

                logging.info(f"Balance updated: {public_key} => {new_balance}")
                return True

        except sqlite3.Error as e:
            logging.error(f"Failed to update balance: {e}")
        return False

    def get_balance(self, public_key):
        """Get the balance of a given public key."""
        try:
            with sqlite3.connect(self.db_name, timeout=15, isolation_level=None) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT balance FROM balances WHERE public_key = ?", (public_key,))
                result = cursor.fetchone()
                return float(result[0]) if result else 0.0  # Ensure float return

        except sqlite3.Error as e:
            logging.error(f"Failed to retrieve balance: {e}")
            return 0.0

    def add_transaction(self, sender, recipient, amount):
        """Add a transaction to the database and update balances atomically."""
        if amount <= 0:
            logging.warning("Invalid transaction amount.")
            return False

        sender_balance = self.get_balance(sender)
        if sender_balance < amount:
            logging.warning(f"Insufficient funds. Sender has only {sender_balance}.")
            return False

        try:
            with sqlite3.connect(self.db_name, timeout=15, isolation_level=None) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT INTO transactions (sender, recipient, amount) VALUES (?, ?, ?)
                """, (sender, recipient, amount))

                # Deduct from sender
                cursor.execute("UPDATE balances SET balance = balance - ? WHERE public_key = ?", (amount, sender))

                # Add to recipient
                cursor.execute("""
                    INSERT INTO balances (public_key, balance) VALUES (?, ?)
                    ON CONFLICT(public_key) DO UPDATE SET balance = balance + ?
                """, (recipient, amount, amount))

                logging.info(f"Transaction successful: {sender} -> {recipient} ({amount})")
                return True

        except sqlite3.Error as e:
            logging.error(f"Failed to add transaction: {e}")
        return False

    def get_transactions(self):
        """Retrieve all transactions."""
        try:
            with sqlite3.connect(self.db_name, timeout=15, isolation_level=None) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT sender, recipient, amount, timestamp FROM transactions")
                transactions = cursor.fetchall()
                return [{"sender": t[0], "recipient": t[1], "amount": t[2], "timestamp": t[3]} for t in transactions]

        except sqlite3.Error as e:
            logging.error(f"Failed to fetch transactions: {e}")
            return []

    def list_wallets(self):
        """List all registered wallets."""
        try:
            with sqlite3.connect(self.db_name, timeout=15, isolation_level=None) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT public_key FROM wallets")
                wallets = cursor.fetchall()
                return [wallet[0] for wallet in wallets]

        except sqlite3.Error as e:
            logging.error(f"Failed to list wallets: {e}")
            return []

# Ensure the database is created when this script runs
if __name__ == "__main__":
    db = Database()
    print("Database initialized successfully!")