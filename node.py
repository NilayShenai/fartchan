from flask import Flask, request, jsonify
from blockchain import Blockchain
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = Flask(__name__)
blockchain = Blockchain()

MINING_REWARD = 50  # Reward for mining a new block

@app.route('/mine', methods=['GET'])
def mine():
    miner_address = request.args.get("miner")
    if not miner_address:
        logging.error("No miner address provided.")
        return jsonify({"error": "No miner address provided"}), 400

    try:
        last_block = blockchain.chain[-1]
        last_proof = last_block["proof"]
        proof = blockchain.proof_of_work(last_proof)
        previous_hash = blockchain.hash(last_block)

        # Ensure miner has a registered wallet
        blockchain.db.register_wallet(miner_address)

        # Reward the miner
        success = blockchain.db.update_balance(miner_address, MINING_REWARD)
        if not success:
            logging.error("Failed to update miner balance.")
            return jsonify({"error": "Failed to update miner balance"}), 500

        # Create a new block including pending transactions
        block = blockchain.create_block(proof, previous_hash)

        response = {
            "message": "New block mined!",
            "block": block,
            "reward": MINING_REWARD,
            "miner": miner_address
        }
        logging.info(f"Block mined successfully: {block}")
        return jsonify(response), 200

    except Exception as e:
        logging.error(f"Mining failed: {e}")
        return jsonify({"error": "Mining failed"}), 500

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    data = request.get_json()
    required_fields = ["sender", "recipient", "amount"]

    if not data or not all(field in data for field in required_fields):
        logging.error(f"Missing transaction fields: {data}")
        return jsonify({"error": "Missing transaction fields"}), 400

    sender = data["sender"]
    recipient = data["recipient"]
    amount = data["amount"]

    if not isinstance(amount, (int, float)) or amount <= 0:
        logging.error(f"Invalid transaction amount: {amount}")
        return jsonify({"error": "Invalid transaction amount"}), 400

    # Ensure sender has enough balance
    sender_balance = blockchain.db.get_balance(sender)
    if sender_balance < amount:
        logging.warning(f"Insufficient funds: {sender} has {sender_balance}, tried to send {amount}")
        return jsonify({"error": "Insufficient balance"}), 400

    # Process transaction
    success = blockchain.db.add_transaction(sender, recipient, amount)
    if success:
        logging.info(f"Transaction added: {sender} -> {recipient} ({amount})")
        return jsonify({"message": "Transaction added"}), 200
    else:
        logging.error(f"Transaction failed for {sender} -> {recipient} ({amount})")
        return jsonify({"error": "Transaction failed"}), 500

@app.route('/get_balance', methods=['GET'])
def get_balance():
    address = request.args.get("address")
    if not address:
        logging.error("No address provided.")
        return jsonify({"error": "No address provided"}), 400

    try:
        balance = blockchain.db.get_balance(address)
        logging.info(f"Balance retrieved: {address} => {balance}")
        return jsonify({"balance": balance}), 200
    except Exception as e:
        logging.error(f"Failed to retrieve balance: {e}")
        return jsonify({"error": "Failed to retrieve balance"}), 500

@app.route('/get_transactions', methods=['GET'])
def get_transactions():
    try:
        transactions = blockchain.db.get_transactions()
        return jsonify(transactions), 200  # Ensure it returns a list of dictionaries
    except Exception as e:
        logging.error(f"Failed to fetch transactions: {e}")
        return jsonify({"error": "Failed to fetch transactions"}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)