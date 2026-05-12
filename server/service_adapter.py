"""成员3调用成员4业务接口的适配层。

成员4完成 database/account_service.py 与 email_service/smtp_email.py 后，本文件会
优先导入真实模块；如果真实模块暂时不存在，则使用内存版服务，保证成员3服务器
可以先独立运行和测试。
"""

from __future__ import annotations

from datetime import datetime
from importlib import import_module
from typing import Any


class InMemoryAccountService:
    """临时内存服务，仅用于成员4模块未接入前的本地演示。"""

    def __init__(self) -> None:
        self.accounts: dict[str, dict[str, Any]] = {
            "zhangsan": {
                "password": "123456",
                "balance": 5000.0,
                "email": "zhangsan@qq.com",
                "status": 1,
            },
            "lisi": {
                "password": "123456",
                "balance": 3000.0,
                "email": "lisi@qq.com",
                "status": 1,
            },
            "admin": {
                "password": "123456",
                "balance": 10000.0,
                "email": "admin@qq.com",
                "status": 1,
            },
        }
        self.flows: list[dict[str, Any]] = []

    def check_user(self, username: str) -> bool:
        account = self.accounts.get(username)
        return bool(account and account.get("status") == 1)

    def check_password(self, username: str, password: str) -> bool:
        account = self.accounts.get(username)
        return bool(account and account.get("password") == password)

    def get_balance(self, username: str) -> float:
        return float(self.accounts[username]["balance"])

    def withdraw_money(self, username: str, amount: float) -> float:
        balance = self.get_balance(username)
        if amount > balance:
            raise ValueError("Insufficient balance")
        new_balance = balance - amount
        self.accounts[username]["balance"] = new_balance
        self.add_flow(username, "WITHDRAW", amount, new_balance)
        return new_balance

    def deposit_money(self, username: str, amount: float) -> float:
        new_balance = self.get_balance(username) + amount
        self.accounts[username]["balance"] = new_balance
        self.add_flow(username, "DEPOSIT", amount, new_balance)
        return new_balance

    def add_flow(self, username: str, flow_type: str, amount: float, balance_after: float) -> None:
        self.flows.append(
            {
                "username": username,
                "type": flow_type,
                "amount": amount,
                "balance_after": balance_after,
                "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "remark": "in-memory demo",
            }
        )

    def get_flow(self, username: str) -> list[dict[str, Any]]:
        return [flow for flow in self.flows if flow["username"] == username]

    def get_email(self, username: str) -> str:
        return str(self.accounts[username].get("email", ""))

    def send_email(self, to_email: str, subject: str, content: str) -> bool:
        return bool(to_email and subject and content)


class AccountServiceAdapter:
    """统一封装成员4提供的账户函数和邮件函数。"""

    def __init__(self, backend: Any | None = None, email_sender: Any | None = None) -> None:
        self.backend = backend if backend is not None else self._load_account_backend()
        self.email_sender = email_sender if email_sender is not None else self._load_email_sender()

    @staticmethod
    def _load_account_backend() -> Any:
        try:
            return import_module("database.account_service")
        except ModuleNotFoundError:
            return InMemoryAccountService()

    def _load_email_sender(self) -> Any:
        try:
            module = import_module("email_service.smtp_email")
            return getattr(module, "send_email")
        except (ModuleNotFoundError, AttributeError):
            return getattr(self.backend, "send_email", None)

    def check_user(self, username: str) -> bool:
        return bool(self.backend.check_user(username))

    def check_password(self, username: str, password: str) -> bool:
        return bool(self.backend.check_password(username, password))

    def get_balance(self, username: str, record_flow: bool = True) -> float:
        try:
            return float(self.backend.get_balance(username, record_flow=record_flow))
        except TypeError:
            return float(self.backend.get_balance(username))

    def withdraw_money(self, username: str, amount: float) -> Any:
        return self.backend.withdraw_money(username, amount)

    def deposit_money(self, username: str, amount: float) -> Any:
        return self.backend.deposit_money(username, amount)

    def get_flow(self, username: str) -> Any:
        return self.backend.get_flow(username)

    def get_email(self, username: str) -> str:
        return str(self.backend.get_email(username))

    def send_email(self, to_email: str, subject: str, content: str) -> bool:
        if self.email_sender is None:
            return False
        result = self.email_sender(to_email, subject, content)
        return True if result is None else bool(result)
