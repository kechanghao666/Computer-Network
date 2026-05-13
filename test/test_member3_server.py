from __future__ import annotations

import unittest

from server.command_handler import CommandHandler


class FakeAccountService:
    def __init__(self) -> None:
        self.accounts = {
            "zhangsan": {"password": "123456", "balance": 5000.0, "email": "demo@example.com"},
        }
        self.flows = []

    def check_user(self, username: str) -> bool:
        return username in self.accounts

    def check_password(self, username: str, password: str) -> bool:
        return self.accounts[username]["password"] == password

    def get_balance(self, username: str) -> float:
        return self.accounts[username]["balance"]

    def withdraw_money(self, username: str, amount: float) -> float:
        self.accounts[username]["balance"] -= amount
        balance_after = self.accounts[username]["balance"]
        self.flows.append(
            {
                "type": "WITHDRAW",
                "amount": amount,
                "balance_after": balance_after,
                "create_time": "2026-05-12 15:30:00",
            }
        )
        return balance_after

    def deposit_money(self, username: str, amount: float) -> dict[str, float]:
        self.accounts[username]["balance"] += amount
        balance_after = self.accounts[username]["balance"]
        self.flows.append(
            {
                "type": "DEPOSIT",
                "amount": amount,
                "balance_after": balance_after,
                "create_time": "2026-05-12 15:31:00",
            }
        )
        return {"balance_after": balance_after}

    def get_flow(self, username: str):
        return self.flows

    def get_email(self, username: str) -> str:
        return self.accounts[username]["email"]

    def send_email(self, to_email: str, subject: str, content: str) -> bool:
        return True


class Member3ServerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.handler = CommandHandler(FakeAccountService())

    def login(self) -> None:
        self.assertIn("200 OK HELO accepted, User: zhangsan", self.handler.handle_request("HELO zhangsan").response)
        self.assertIn("200 OK Login success", self.handler.handle_request("PASS 123456").response)

    def test_login_success_and_balance_query(self) -> None:
        self.login()
        response = self.handler.handle_request("BALA").response
        self.assertEqual("201 OK Balance: 5000.00 RMB\n", response)

    def test_reject_operation_before_login(self) -> None:
        response = self.handler.handle_request("BALA").response
        self.assertEqual("404 ERROR Please login first\n", response)

    def test_helo_does_not_set_login_state(self) -> None:
        response = self.handler.handle_request("HELO zhangsan").response
        self.assertEqual("200 OK HELO accepted, User: zhangsan\n", response)
        self.assertEqual("404 ERROR Please login first\n", self.handler.handle_request("BALA").response)

    def test_wrong_password(self) -> None:
        self.handler.handle_request("HELO zhangsan")
        response = self.handler.handle_request("PASS bad").response
        self.assertEqual("400 ERROR Wrong password\n", response)

    def test_withdraw_and_deposit_success(self) -> None:
        self.login()
        withdraw_response = self.handler.handle_request("WITHDRAW 500").response
        self.assertIn("202 OK Withdraw success", withdraw_response)
        self.assertIn("Balance: 4500.00 RMB", withdraw_response)
        self.assertIn("Email Notice: Queued", withdraw_response)

        deposit_response = self.handler.handle_request("DEPOSIT 300").response
        self.assertIn("203 OK Deposit success", deposit_response)
        self.assertIn("Balance: 4800.00 RMB", deposit_response)
        self.assertIn("Email Notice: Queued", deposit_response)

    def test_invalid_and_insufficient_amount(self) -> None:
        self.login()
        self.assertEqual("403 ERROR Invalid amount\n", self.handler.handle_request("WITHDRAW -1").response)
        self.assertEqual("403 ERROR Invalid amount\n", self.handler.handle_request("DEPOSIT abc").response)
        self.assertEqual("402 ERROR Insufficient balance\n", self.handler.handle_request("WITHDRAW 99999").response)

    def test_flow_ping_and_quit(self) -> None:
        self.login()
        self.handler.handle_request("DEPOSIT 100")
        flow_response = self.handler.handle_request("FLOW").response
        self.assertIn("204 OK Flow query success", flow_response)
        self.assertIn("DEPOSIT", flow_response)

        self.assertEqual("PONG\n", self.handler.handle_request("PING").response)
        quit_result = self.handler.handle_request("QUIT")
        self.assertEqual("300 OK Quit success\n", quit_result.response)
        self.assertTrue(quit_result.close_connection)


if __name__ == "__main__":
    unittest.main()
