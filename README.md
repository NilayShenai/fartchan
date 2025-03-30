# FARTCHAN

### Flask-Accelerated Replicated Transaction Chain and Hashing Algorithm Network

FARTCHAN is a blockchain implementation designed to demonstrate core concepts such as wallet management, transactions, mining, proof-of-work, and decentralized data storage. It features a Flask-based API, SQLite database integration, and a command-line interface (CLI) for user interactions.

## Features

- **Wallet System** – Secure ECDSA-based wallet generation and management
- **Transaction Processing** – Create, sign, and verify transactions between wallets
- **Proof-of-Work Mining** – Implemented with an adjustable difficulty algorithm
- **Blockchain Storage** – Full persistence with SQLite for blocks, transactions, and balances
- **REST API** – Flask-based interface for interacting with the blockchain network
- **CLI Interface** – Command-line utility for wallet operations, transactions, and mining
- **Dynamic Difficulty Adjustment** – Adapts mining difficulty based on block times

## Prerequisites

- Python 3.8+
- Required dependencies: `flask`, `ecdsa`, `sqlite3`

## Installation

### Clone the repository:

```bash
git clone https://github.com/NilayShenai/fartchan.git
cd fartchan
```

### Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Running the Blockchain Node

Start the node to enable API interactions:

```bash
python node.py
```

### Using the CLI Interface

Launch the command-line interface for blockchain operations:

```bash
python cli.py
```

## API Endpoints

| Method | Endpoint                       | Description                                |
| ------ | ------------------------------ | ------------------------------------------ |
| GET    | `/mine?miner=ADDRESS`          | Mines a new block and rewards the miner    |
| POST   | `/add_transaction`             | Adds a new transaction to the pending pool |
| GET    | `/get_balance?address=ADDRESS` | Retrieves the balance of a given wallet    |
| GET    | `/get_transactions`            | Fetches all confirmed transactions         |

## Project Structure

```
.
├── node.py            # Flask-based blockchain node
├── blockchain.py      # Core blockchain logic (mining, transactions, PoW)
├── database.py        # SQLite integration for storing blocks and balances
├── wallet.py          # Wallet creation and cryptographic key management
├── cli.py             # Command-line interface for user interactions
├── requirements.txt   # Dependencies
└── blockchain.db      # SQLite database file (auto-generated)
```

## How to Use

### Creating a Wallet

1. Run `python cli.py`
2. Select "Create New Wallet"
3. A wallet file will be generated and stored locally

### Sending Transactions

1. Run `python cli.py`
2. Select "Send Transaction"
3. Enter sender wallet, recipient address, and amount

### Mining Blocks

1. Run `python cli.py`
2. Select "Mine Block"
3. Enter your wallet file to receive mining rewards

## Future Improvements

- Implement additional security mechanisms for transaction validation
- Introduce Merkle trees for efficient transaction verification
- Improve block validation and consensus mechanisms

