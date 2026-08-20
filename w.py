import unittest
import threading
from DigitalWallet import DigitalWallet


class WalletSecurityQA(unittest.TestCase):

    def setUp(self):
        self.wallet = DigitalWallet(daily_limit=50000)

        self.wallet.create_account(
            "A101",
            "Rahul",
            "1234"
        )

        self.wallet.create_account(
            "A102",
            "Arun",
            "5678"
        )

        self.wallet.deposit(
            "A101",
            20000,
            "1234"
        )

    # 1. Normal Transaction
    def test_normal_transaction(self):

        result = self.wallet.withdraw(
            "A101",
            2000,
            "1234"
        )

        self.assertEqual(
            result,
            "Withdrawal successful"
        )

    # 2. Insufficient Balance
    def test_insufficient_balance(self):

        result = self.wallet.withdraw(
            "A101",
            50000,
            "1234"
        )

        self.assertEqual(
            result,
            "Insufficient balance"
        )

    # 3. Daily Transaction Limit
    def test_daily_limit(self):

        result = self.wallet.withdraw(
            "A101",
            50001,
            "1234"
        )

        self.assertEqual(
            result,
            "Daily transaction limit exceeded"
        )

    # 4. Multiple Failed PINs
    def test_multiple_failed_pins(self):

        self.wallet.withdraw(
            "A101",
            1000,
            "1111"
        )

        self.wallet.withdraw(
            "A101",
            1000,
            "2222"
        )

        self.wallet.withdraw(
            "A101",
            1000,
            "3333"
        )

        self.assertEqual(
            self.wallet.accounts["A101"]["failed_pins"],
            3
        )

    # 5. Suspicious Transaction
    def test_suspicious_transaction(self):

        result = self.wallet.withdraw(
            "A101",
            15000,
            "1234"
        )

        self.assertIn(
            "SUSPICIOUS",
            result
        )

    # 6. Duplicate Transaction
    def test_duplicate_transaction(self):

        self.wallet.withdraw(
            "A101",
            1000,
            "1234"
        )

        self.wallet.withdraw(
            "A101",
            1000,
            "1234"
        )

        transactions = self.wallet.transaction_history(
            "A101"
        )

        self.assertEqual(
            len(transactions),
            3
        )

    # 7. Negative Amount
    def test_negative_amount(self):

        result = self.wallet.deposit(
            "A101",
            -1000,
            "1234"
        )

        self.assertEqual(
            result,
            "Invalid amount"
        )

    # 8. Concurrent Transactions
    def test_concurrent_transactions(self):

        results = []

        def withdraw_money():
            result = self.wallet.withdraw(
                "A101",
                1000,
                "1234"
            )
            results.append(result)

        threads = []

        for i in range(5):
            thread = threading.Thread(
                target=withdraw_money
            )
            threads.append(thread)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        self.assertEqual(
            len(results),
            5
        )


if __name__ == "__main__":
    unittest.main()
