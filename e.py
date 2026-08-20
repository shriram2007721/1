from datetime import datetime, timedelta
import threading


class DigitalWallet:
    def __init__(self, daily_limit=50000):
        self.accounts = {}
        self.daily_limit = daily_limit
        self.lock = threading.Lock()

    # Account Creation
    def create_account(self, account_id, name, pin):
        if account_id in self.accounts:
            return "Account already exists"

        self.accounts[account_id] = {
            "name": name,
            "pin": str(pin),
            "balance": 0.0,
            "daily_transactions": 0.0,
            "transactions": [],
            "failed_pins": 0,
            "last_transaction_time": None
        }

        return "Account created successfully"

    # PIN Verification
    def verify_pin(self, account_id, pin):
        if account_id not in self.accounts:
            return False

        account = self.accounts[account_id]

        if account["pin"] == str(pin):
            account["failed_pins"] = 0
            return True

        account["failed_pins"] += 1

        if account["failed_pins"] >= 3:
            print(f"FRAUD ALERT: Multiple failed PIN attempts for {account_id}")

        return False

    # Fraud Detection
    def fraud_detection(self, account_id, amount):
        account = self.accounts[account_id]
        suspicious = []

        # More than 5 transactions in 10 minutes
        ten_minutes_ago = datetime.now() - timedelta(minutes=10)

        recent_transactions = [
            t for t in account["transactions"]
            if t["time"] >= ten_minutes_ago
        ]

        if len(recent_transactions) >= 5:
            suspicious.append("More than 5 transactions in 10 minutes")

        # Large transaction
        if amount > 10000:
            suspicious.append("Large transaction")

        # Multiple failed PIN attempts
        if account["failed_pins"] >= 3:
            suspicious.append("Multiple failed PIN attempts")

        # Unusual transaction amount
        if amount > account["balance"] * 0.8 and account["balance"] > 0:
            suspicious.append("Unusual transaction amount")

        return suspicious

    # Record Transaction
    def record_transaction(self, transaction_type, amount, status, account_id):
        self.accounts[account_id]["transactions"].append({
            "type": transaction_type,
            "amount": amount,
            "status": status,
            "time": datetime.now()
        })

    # Deposit
    def deposit(self, account_id, amount, pin):
        if not self.verify_pin(account_id, pin):
            return "Invalid PIN"

        if amount <= 0:
            return "Invalid amount"

        fraud = self.fraud_detection(account_id, amount)

        self.accounts[account_id]["balance"] += amount
        self.accounts[account_id]["daily_transactions"] += amount

        self.record_transaction(
            "Deposit",
            amount,
            "SUSPICIOUS" if fraud else "SUCCESS",
            account_id
        )

        if fraud:
            return "Deposit successful - SUSPICIOUS: " + ", ".join(fraud)

        return "Deposit successful"

    # Withdrawal
    def withdraw(self, account_id, amount, pin):
        if not self.verify_pin(account_id, pin):
            return "Invalid PIN"

        if amount <= 0:
            return "Invalid amount"

        account = self.accounts[account_id]

        if account["balance"] < amount:
            self.record_transaction(
                "Withdrawal",
                amount,
                "FAILED - Insufficient Balance",
                account_id
            )
            return "Insufficient balance"

        if account["daily_transactions"] + amount > self.daily_limit:
            return "Daily transaction limit exceeded"

        fraud = self.fraud_detection(account_id, amount)

        account["balance"] -= amount
        account["daily_transactions"] += amount

        self.record_transaction(
            "Withdrawal",
            amount,
            "SUSPICIOUS" if fraud else "SUCCESS",
            account_id
        )

        if fraud:
            return "Withdrawal successful - SUSPICIOUS: " + ", ".join(fraud)

        return "Withdrawal successful"

    # Money Transfer
    def transfer(self, sender_id, receiver_id, amount, pin):

        if sender_id not in self.accounts:
            return "Sender account does not exist"

        if receiver_id not in self.accounts:
            return "Receiver account does not exist"

        if amount <= 0:
            return "Invalid amount"

        if not self.verify_pin(sender_id, pin):
            return "Invalid PIN"

        with self.lock:

            sender = self.accounts[sender_id]

            if sender["balance"] < amount:
                self.record_transaction(
                    "Transfer",
                    amount,
                    "FAILED - Insufficient Balance",
                    sender_id
                )
                return "Insufficient balance"

            if sender["daily_transactions"] + amount > self.daily_limit:
                return "Daily transaction limit exceeded"

            fraud = self.fraud_detection(sender_id, amount)

            sender["balance"] -= amount
            self.accounts[receiver_id]["balance"] += amount

            sender["daily_transactions"] += amount

            self.record_transaction(
                "Transfer",
                amount,
                "SUSPICIOUS" if fraud else "SUCCESS",
                sender_id
            )

            self.record_transaction(
                "Transfer Received",
                amount,
                "SUCCESS",
                receiver_id
            )

            if fraud:
                return "Transfer successful - SUSPICIOUS: " + ", ".join(fraud)

            return "Transfer successful"

    # Transaction History
    def transaction_history(self, account_id):
        if account_id not in self.accounts:
            return []

        return self.accounts[account_id]["transactions"]

    # Balance Verification
    def check_balance(self, account_id, pin):
        if not self.verify_pin(account_id, pin):
            return "Invalid PIN"

        return self.accounts[account_id]["balance"]


# Demo
if __name__ == "__main__":

    wallet = DigitalWallet(daily_limit=50000)

    print(wallet.create_account("A101", "Rahul", "1234"))
    print(wallet.create_account("A102", "Arun", "5678"))

    print(wallet.deposit("A101", 20000, "1234"))

    print("Balance:", wallet.check_balance("A101", "1234"))

    print(wallet.withdraw("A101", 2000, "1234"))

    print(wallet.transfer("A101", "A102", 5000, "1234"))

    print("Final Balance:",
          wallet.check_balance("A101", "1234"))

    print("\nTransaction History:")

    for transaction in wallet.transaction_history("A101"):
        print(transaction)
