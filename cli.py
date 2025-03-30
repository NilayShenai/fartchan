import requests
import wallet
import time
import os
import json

API_URL = "http://127.0.0.1:5000"  # Blockchain Node Address

def main():
    while True:
        print("\n1. Create New Wallet")
        print("2. List Existing Wallets")
        print("3. View Balance")
        print("4. View Transactions")
        print("5. Send Transaction")
        print("6. Mine Block")
        print("7. Exit")
        choice = input("Choose an option: ")

        if choice == "1":
            filename = f"wallet_{int(time.time())}.json"
            new_wallet = wallet.Wallet()
            new_wallet.save_keys(filename)
            print(f"\nNew wallet created! File: {filename}")
            print(f"Public Key: {new_wallet.public_key}")

        elif choice == "2":
            wallets = os.listdir(".")  # List files in current directory
            wallet_files = [w for w in wallets if w.startswith("wallet_") and w.endswith(".json")]
            
            if not wallet_files:
                print("No wallets found.")
            else:
                print("\nAvailable Wallets:")
                for w in wallet_files:
                    print(f"- {w}")

        elif choice == "3":
            wallet_file = input("Enter your wallet filename: ")
            if not os.path.exists(wallet_file):
                print("Wallet file not found!")
                continue
            
            try:
                keys = wallet.Wallet.load_keys(wallet_file)
                response = requests.get(f"{API_URL}/get_balance?address={keys['public_key']}")
                if response.status_code == 200:
                    print("\nBalance:", response.json().get("balance", "Error fetching balance"))
                else:
                    print("Error fetching balance.")
            except (requests.exceptions.RequestException, json.JSONDecodeError):
                print("Error: Unable to connect to the blockchain node.")

        elif choice == "4":
            try:
                response = requests.get(f"{API_URL}/get_transactions")
                if response.status_code == 200:
                    transactions = response.json()

                    if isinstance(transactions, list) and all(isinstance(tx, dict) for tx in transactions):
                        print("\nTransaction History:")
                        for tx in transactions:
                            print(f"{tx.get('timestamp', 'Unknown')} | {tx.get('sender', 'N/A')} -> {tx.get('recipient', 'N/A')} | Amount: {tx.get('amount', 0)}")
                    else:
                        print("No valid transactions found.")
                else:
                    print("Failed to fetch transactions.")
            except (requests.exceptions.RequestException, ValueError):
                print("Error: Unable to connect to the blockchain node.")

        elif choice == "5":
            sender_wallet = input("Enter your wallet filename: ")
            if not os.path.exists(sender_wallet):
                print("Wallet file not found!")
                continue
            
            try:
                keys = wallet.Wallet.load_keys(sender_wallet)
                sender = keys["public_key"]
                recipient = input("Recipient (Public Key): ")
                amount = input("Amount: ")

                try:
                    amount = float(amount)
                    if amount <= 0:
                        print("Amount must be greater than zero.")
                        continue
                except ValueError:
                    print("Invalid amount. Must be a number.")
                    continue

                data = {"sender": sender, "recipient": recipient, "amount": amount}
                response = requests.post(f"{API_URL}/add_transaction", json=data)
                if response.status_code == 200:
                    print(response.json().get("message", "Transaction sent successfully!"))
                else:
                    print("Error processing transaction.")

            except (requests.exceptions.RequestException, json.JSONDecodeError):
                print("Error: Unable to connect to the blockchain node.")

        elif choice == "6":
            miner_wallet = input("Enter your wallet filename: ")
            if not os.path.exists(miner_wallet):
                print("Wallet file not found!")
                continue

            try:
                keys = wallet.Wallet.load_keys(miner_wallet)
                response = requests.get(f"{API_URL}/mine?miner={keys['public_key']}")
                if response.status_code == 200:
                    print(response.json().get("message", "Block mined successfully!"))
                else:
                    print("Error mining block.")

            except (requests.exceptions.RequestException, json.JSONDecodeError):
                print("Error: Unable to connect to the blockchain node.")

        elif choice == "7":
            print("Exiting CLI...")
            break

        else:
            print("Invalid option. Please select a number between 1-7.")

if __name__ == "__main__":
    main()