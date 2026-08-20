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
            "balance": 0,
            "daily_total": 0,
            "transactions": [],
            "failed_pins": 0
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
        return False

    # Fraud Detection
    def fraud_detection(self, account_id, amount):

        account = self.accounts[account_id]
        alerts = []

        ten_minutes_ago = datetime.now() - timedelta(minutes=10)

        recent_transactions = 0

        for transaction in account["transactions"]:
            if transaction["time"] >= ten_minutes_ago:
                recent_transactions += 1

        # More than 5 transactions in 10 minutes
        if recent_transactions >= 5:
            alerts.append("More than 5 transactions in 10 minutes")

        # Large transaction
        if amount > 10000:
            alerts.append("Large transaction")

        # Multiple failed PIN attempts
        if account["failed_pins"] >= 3:
            alerts.append("Multiple failed PIN attempts")

        # Unusual transaction amount
        if account["balance"] > 0:
            if amount > account["balance"] * 0.8:
                alerts.append("Unusual transaction amount")

        return alerts

    # Record Transaction
    def record_transaction(self, account_id, transaction_type,
                           amount, status):

        self.accounts[account_id]["transactions"].append({
            "type": transaction_type,
            "amount": amount,
            "status": status,
            "time": datetime.now()
        })

    # Deposit
    def deposit(self, account_id, amount, pin):

        if account_id not in self.accounts:
            return "Account not found"

        if amount <= 0:
            return "Invalid amount"

        if not self.verify_pin(account_id, pin):
            return "Invalid PIN"

        alerts = self.fraud_detection(account_id, amount)

        self.accounts[account_id]["balance"] += amount
        self.accounts[account_id]["daily_total"] += amount

        status = "SUSPICIOUS" if alerts else "SUCCESS"

        self.record_transaction(
            account_id,
            "Deposit",
            amount,
            status
        )

        if alerts:
            return "Deposit successful - SUSPICIOUS"

        return "Deposit successful"

    # Withdrawal
    def withdraw(self, account_id, amount, pin):

        if account_id not in self.accounts:
            return "Account not found"

        if amount <= 0:
            return "Invalid amount"

        if not self.verify_pin(account_id, pin):
            return "Invalid PIN"

        account = self.accounts[account_id]

        if account["balance"] < amount:
            return "Insufficient balance"

        if account["daily_total"] + amount > self.daily_limit:
            return "Daily transaction limit exceeded"

        alerts = self.fraud_detection(account_id, amount)

        account["balance"] -= amount
        account["daily_total"] += amount

        status = "SUSPICIOUS" if alerts else "SUCCESS"

        self.record_transaction(
            account_id,
            "Withdrawal",
            amount,
            status
        )

        if alerts:
            return "Withdrawal successful - SUSPICIOUS"

        return "Withdrawal successful"

    # Money Transfer
    def transfer(self, sender, receiver, amount, pin):

        if sender not in self.accounts:
            return "Sender account not found"

        if receiver not in self.accounts:
            return "Receiver account not found"

        if amount <= 0:
            return "Invalid amount"

        if not self.verify_pin(sender, pin):
            return "Invalid PIN"

        with self.lock:

            sender_account = self.accounts[sender]

            if sender_account["balance"] < amount:
                return "Insufficient balance"

            if sender_account["daily_total"] + amount > self.daily_limit:
                return "Daily transaction limit exceeded"

            alerts = self.fraud_detection(sender, amount)

            sender_account["balance"] -= amount
            sender_account["daily_total"] += amount

            self.accounts[receiver]["balance"] += amount

            status = "SUSPICIOUS" if alerts else "SUCCESS"

            self.record_transaction(
                sender,
                "Transfer",
                amount,
                status
            )

            self.record_transaction(
                receiver,
                "Transfer Received",
                amount,
                "SUCCESS"
            )

            if alerts:
                return "Transfer successful - SUSPICIOUS"

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


if __name__ == "__main__":

    wallet = DigitalWallet()

    print(wallet.create_account("A101", "Rahul", "1234"))
    print(wallet.create_account("A102", "Arun", "5678"))

    print(wallet.deposit("A101", 20000, "1234"))
    print(wallet.withdraw("A101", 2000, "1234"))
    print(wallet.transfer("A101", "A102", 5000, "1234"))

    print("Balance:",
          wallet.check_balance("A101", "1234"))

    print("Transaction History:")

    for transaction in wallet.transaction_history("A101"):
        print(transaction)
