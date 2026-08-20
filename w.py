import unittest
import threading
from datetime import datetime, timedelta


class TestWallet:

    def __init__(self, daily_limit=50000):
        self.balance = 20000
        self.daily_limit = daily_limit
        self.daily_total = 0
        self.failed_pins = 0
        self.pin = "1234"
        self.transactions = []
        self.lock = threading.Lock()

    def verify_pin(self, pin):

        if pin == self.pin:
            self.failed_pins = 0
            return True

        self.failed_pins += 1
        return False

    def fraud_detection(self, amount):

        alerts = []

        ten_minutes_ago = datetime.now() - timedelta(minutes=10)

        recent = 0

        for transaction in self.transactions:
            if transaction["time"] >= ten_minutes_ago:
                recent += 1

        if recent >= 5:
            alerts.append("More than 5 transactions")

        if amount > 10000:
            alerts.append("Large transaction")

        if self.failed_pins >= 3:
            alerts.append("Multiple failed PIN attempts")

        if self.balance > 0 and amount > self.balance * 0.8:
            alerts.append("Unusual transaction amount")

        return alerts

    def withdraw(self, amount, pin):

        if amount <= 0:
            return "Invalid amount"

        if not self.verify_pin(pin):
            return "Invalid PIN"

        if self.balance < amount:
            return "Insufficient balance"

        if self.daily_total + amount > self.daily_limit:
            return "Daily transaction limit exceeded"

        alerts = self.fraud_detection(amount)

        with self.lock:

            self.balance -= amount
            self.daily_total += amount

            self.transactions.append({
                "type": "Withdrawal",
                "amount": amount,
                "time": datetime.now()
            })

        if alerts:
            return "SUSPICIOUS transaction"

        return "Withdrawal successful"

    def deposit(self, amount, pin):

        if amount <= 0:
            return "Invalid amount"

        if not self.verify_pin(pin):
            return "Invalid PIN"

        self.balance += amount

        return "Deposit successful"


class WalletSecurityQA(unittest.TestCase):

    def setUp(self):

        self.wallet = TestWallet()

    # Normal Transaction
    def test_normal_transaction(self):

        result = self.wallet.withdraw(
            1000,
            "1234"
        )

        self.assertEqual(
            result,
            "Withdrawal successful"
        )

    # Insufficient Balance
    def test_insufficient_balance(self):

        result = self.wallet.withdraw(
            50000,
            "1234"
        )

        self.assertEqual(
            result,
            "Insufficient balance"
        )

    # Daily Transaction Limit
    def test_daily_limit(self):

        self.wallet.daily_total = 49000

        result = self.wallet.withdraw(
            2000,
            "1234"
        )

        self.assertEqual(
            result,
            "Daily transaction limit exceeded"
        )

    # Multiple Failed PINs
    def test_multiple_failed_pins(self):

        self.wallet.withdraw(1000, "1111")
        self.wallet.withdraw(1000, "2222")
        self.wallet.withdraw(1000, "3333")

        self.assertEqual(
            self.wallet.failed_pins,
            3
        )

    # Suspicious Transaction
    def test_suspicious_transaction(self):

        result = self.wallet.withdraw(
            15000,
            "1234"
        )

        self.assertIn(
            "SUSPICIOUS",
            result
        )

    # Duplicate Transaction
    def test_duplicate_transaction(self):

        self.wallet.withdraw(
            1000,
            "1234"
        )

        self.wallet.withdraw(
            1000,
            "1234"
        )

        self.assertEqual(
            len(self.wallet.transactions),
            2
        )

    # Negative Amount
    def test_negative_amount(self):

        result = self.wallet.deposit(
            -1000,
            "1234"
        )

        self.assertEqual(
            result,
            "Invalid amount"
        )

    # Concurrent Transactions
    def test_concurrent_transactions(self):

        results = []

        def transaction():

            result = self.wallet.withdraw(
                1000,
                "1234"
            )

            results.append(result)

        threads = []

        for i in range(5):

            t = threading.Thread(
                target=transaction
            )

            threads.append(t)

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        self.assertEqual(
            len(results),
            5
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
