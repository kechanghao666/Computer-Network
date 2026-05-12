import tempfile
import unittest
from pathlib import Path

from database.account_service import (
    add_flow,
    check_password,
    check_user,
    deposit_money,
    get_balance,
    get_email,
    get_flow,
    init_database,
    withdraw_money,
)
from email_service.smtp_email import send_email


class RecordingEmailSender:
    def __init__(self):
        self.messages = []

    def send(self, to_email, subject, content):
        self.messages.append((to_email, subject, content))
        return True


class Member4ServiceTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "atm.db"
        init_database(self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_init_database_creates_tables_and_seed_accounts(self):
        self.assertTrue(check_user("zhangsan", self.db_path))
        self.assertTrue(check_user("lisi", self.db_path))
        self.assertTrue(check_user("admin", self.db_path))
        self.assertEqual(get_balance("zhangsan", self.db_path), 5000.0)
        self.assertEqual(get_email("lisi", self.db_path), "lisi@qq.com")

    def test_check_password_validates_existing_user_password(self):
        self.assertTrue(check_password("zhangsan", "123456", self.db_path))
        self.assertFalse(check_password("zhangsan", "wrong", self.db_path))
        self.assertFalse(check_password("missing", "123456", self.db_path))

    def test_withdraw_money_updates_balance_and_records_flow(self):
        result = withdraw_money("zhangsan", 500, self.db_path)

        self.assertTrue(result["success"])
        self.assertEqual(result["status_code"], 202)
        self.assertEqual(result["balance"], 4500.0)
        self.assertEqual(get_balance("zhangsan", self.db_path), 4500.0)

        flows = get_flow("zhangsan", self.db_path)
        self.assertEqual(len(flows), 1)
        self.assertEqual(flows[0]["type"], "WITHDRAW")
        self.assertEqual(flows[0]["amount"], 500.0)
        self.assertEqual(flows[0]["balance_after"], 4500.0)

    def test_deposit_money_updates_balance_and_records_flow(self):
        result = deposit_money("lisi", "300", self.db_path)

        self.assertTrue(result["success"])
        self.assertEqual(result["status_code"], 203)
        self.assertEqual(result["balance"], 3300.0)
        self.assertEqual(get_balance("lisi", self.db_path), 3300.0)

        flows = get_flow("lisi", self.db_path)
        self.assertEqual(len(flows), 1)
        self.assertEqual(flows[0]["type"], "DEPOSIT")
        self.assertEqual(flows[0]["amount"], 300.0)
        self.assertEqual(flows[0]["balance_after"], 3300.0)

    def test_invalid_amount_does_not_change_balance_or_add_flow(self):
        result = deposit_money("zhangsan", "-1", self.db_path)

        self.assertFalse(result["success"])
        self.assertEqual(result["status_code"], 403)
        self.assertEqual(get_balance("zhangsan", self.db_path), 5000.0)
        self.assertEqual(get_flow("zhangsan", self.db_path), [])

    def test_insufficient_balance_does_not_change_balance_or_add_flow(self):
        result = withdraw_money("lisi", 5000, self.db_path)

        self.assertFalse(result["success"])
        self.assertEqual(result["status_code"], 402)
        self.assertEqual(get_balance("lisi", self.db_path), 3000.0)
        self.assertEqual(get_flow("lisi", self.db_path), [])

    def test_add_flow_records_query_operation(self):
        add_flow("admin", "BALANCE_QUERY", 0, 10000, self.db_path, "查询余额")

        flows = get_flow("admin", self.db_path)
        self.assertEqual(len(flows), 1)
        self.assertEqual(flows[0]["type"], "BALANCE_QUERY")
        self.assertEqual(flows[0]["remark"], "查询余额")

    def test_send_email_uses_injected_sender(self):
        sender = RecordingEmailSender()

        result = send_email(
            "zhangsan@qq.com",
            "Bank ATM Withdraw Notice",
            "取款金额：500.00 RMB",
            sender=sender,
        )

        self.assertTrue(result)
        self.assertEqual(
            sender.messages,
            [
                (
                    "zhangsan@qq.com",
                    "Bank ATM Withdraw Notice",
                    "取款金额：500.00 RMB",
                )
            ],
        )


if __name__ == "__main__":
    unittest.main()
