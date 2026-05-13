"""银行中央服务器命令解析与业务调度。"""

from __future__ import annotations

from dataclasses import dataclass
import threading
from typing import Any

from server.response import build_response, format_money
from server.service_adapter import AccountServiceAdapter


@dataclass
class SessionState:
    """保存单个客户端连接的登录状态。"""

    username: str | None = None
    pending_username: str | None = None
    is_login: bool = False


@dataclass
class CommandResult:
    """服务器处理一条命令后的结果。"""

    response: str
    close_connection: bool = False


class CommandHandler:
    """解析客户端命令，并调用成员4业务函数完成实际操作。"""

    def __init__(self, service: Any | None = None) -> None:
        self.service = service if service is not None else AccountServiceAdapter()
        self.session = SessionState()

    def handle_request(self, request: str) -> CommandResult:
        """处理客户端发送的一条协议命令。"""
        command, argument = self.parse_command(request)

        try:
            if command == "PING":
                return self.handle_ping()
            if command == "QUIT":
                return self.handle_quit()
            if command == "HELO":
                return self.handle_helo(argument)
            if command == "PASS":
                return self.handle_pass(argument)
            if command == "BALA":
                return self.handle_balance()
            if command == "WITHDRAW":
                return self.handle_withdraw(argument)
            if command == "DEPOSIT":
                return self.handle_deposit(argument)
            if command == "FLOW":
                return self.handle_flow()
            return CommandResult(build_response(500, "ERROR Invalid command"))
        except ValueError as exc:
            if str(exc) == "Insufficient balance":
                return CommandResult(build_response(402, "ERROR Insufficient balance"))
            return CommandResult(build_response(403, "ERROR Invalid amount"))
        except Exception:
            return CommandResult(build_response(500, "ERROR Server error"))

    @staticmethod
    def parse_command(request: str) -> tuple[str, str]:
        """将 COMMAND [data] 请求拆分为命令和参数。"""
        clean_request = request.strip()
        if not clean_request:
            return "", ""
        parts = clean_request.split(maxsplit=1)
        command = parts[0].upper()
        argument = parts[1].strip() if len(parts) > 1 else ""
        return command, argument

    def handle_helo(self, username: str) -> CommandResult:
        """处理用户名检查。"""
        if not username:
            return CommandResult(build_response(500, "ERROR Invalid command"))
        if not self.service.check_user(username):
            self.session = SessionState()
            return CommandResult(build_response(401, "ERROR User not found"))

        self.session.pending_username = username
        self.session.username = None
        self.session.is_login = False
        return CommandResult(build_response(200, f"OK HELO accepted, User: {username}"))

    def handle_pass(self, password: str) -> CommandResult:
        """处理密码校验，成功后设置登录状态。"""
        username = self.session.pending_username
        if not username:
            return CommandResult(build_response(401, "ERROR User not found"))
        if not self.service.check_password(username, password):
            self.session.is_login = False
            return CommandResult(build_response(400, "ERROR Wrong password"))

        self.session.username = username
        self.session.pending_username = None
        self.session.is_login = True
        return CommandResult(build_response(200, "OK Login success"))

    def handle_balance(self) -> CommandResult:
        """处理余额查询。"""
        if not self._require_login():
            return CommandResult(build_response(404, "ERROR Please login first"))

        balance = self._get_balance(self.session.username, record_flow=True)
        return CommandResult(build_response(201, f"OK Balance: {format_money(balance)}"))

    def handle_withdraw(self, amount_text: str) -> CommandResult:
        """处理取款请求。"""
        if not self._require_login():
            return CommandResult(build_response(404, "ERROR Please login first"))

        amount = self._parse_amount(amount_text)
        username = self.session.username
        current_balance = self._get_balance(username, record_flow=False)
        if amount > current_balance:
            return CommandResult(build_response(402, "ERROR Insufficient balance"))

        result = self.service.withdraw_money(username, amount)
        balance_after = self._extract_balance(result)
        if balance_after is None:
            balance_after = self._get_balance(username, record_flow=False)

        email_notice = self._send_transaction_email(
            username=username,
            subject="Bank ATM Withdraw Notice",
            content=(
                "尊敬的用户，您的账户刚刚完成一笔取款操作。\n"
                f"取款金额：{format_money(amount)}\n"
                f"当前余额：{format_money(balance_after)}\n"
                "如非本人操作，请及时联系银行。"
            ),
        )
        detail = f"OK Withdraw success, Balance: {format_money(balance_after)}, Email Notice: {email_notice}"
        return CommandResult(build_response(202, detail))

    def handle_deposit(self, amount_text: str) -> CommandResult:
        """处理存款请求。"""
        if not self._require_login():
            return CommandResult(build_response(404, "ERROR Please login first"))

        amount = self._parse_amount(amount_text)
        username = self.session.username
        result = self.service.deposit_money(username, amount)
        balance_after = self._extract_balance(result)
        if balance_after is None:
            balance_after = self._get_balance(username, record_flow=False)

        email_notice = self._send_transaction_email(
            username=username,
            subject="Bank ATM Deposit Notice",
            content=(
                "尊敬的用户，您的账户刚刚完成一笔存款操作。\n"
                f"存款金额：{format_money(amount)}\n"
                f"当前余额：{format_money(balance_after)}"
            ),
        )
        detail = f"OK Deposit success, Balance: {format_money(balance_after)}, Email Notice: {email_notice}"
        return CommandResult(build_response(203, detail))

    def handle_flow(self) -> CommandResult:
        """处理交易流水查询。"""
        if not self._require_login():
            return CommandResult(build_response(404, "ERROR Please login first"))

        records = self.service.get_flow(self.session.username)
        flow_text = self._format_flow_records(records)
        return CommandResult(build_response(204, f"OK Flow query success: {flow_text}"))

    @staticmethod
    def handle_ping() -> CommandResult:
        """处理 RTT 检测请求。"""
        return CommandResult("PONG\n")

    @staticmethod
    def handle_quit() -> CommandResult:
        """处理退出请求。"""
        return CommandResult(build_response(300, "OK Quit success"), close_connection=True)

    def _require_login(self) -> bool:
        return bool(self.session.is_login and self.session.username)

    def _get_balance(self, username: str, record_flow: bool) -> float:
        try:
            return float(self.service.get_balance(username, record_flow=record_flow))
        except TypeError:
            return float(self.service.get_balance(username))

    @staticmethod
    def _parse_amount(amount_text: str) -> float:
        try:
            amount = float(amount_text)
        except (TypeError, ValueError) as exc:
            raise ValueError("Invalid amount") from exc
        if amount <= 0:
            raise ValueError("Invalid amount")
        return amount

    @staticmethod
    def _extract_balance(result: Any) -> float | None:
        """兼容成员4函数可能返回 float、dict、tuple 或 bool 的情况。"""
        if isinstance(result, bool) or result is None:
            return None
        if isinstance(result, (int, float)):
            return float(result)
        if isinstance(result, dict):
            for key in ("balance", "balance_after", "new_balance"):
                if key in result:
                    return float(result[key])
        if isinstance(result, (list, tuple)):
            for item in reversed(result):
                if isinstance(item, (int, float)):
                    return float(item)
        return None

    def _send_transaction_email(self, username: str, subject: str, content: str) -> str:
        """后台发送邮件，避免 SMTP 网络问题阻塞 ATM 响应。"""
        try:
            to_email = self.service.get_email(username)
            if not to_email:
                return "No email"
        except Exception:
            return "Failed"

        threading.Thread(
            target=self._send_email_safely,
            args=(to_email, subject, content),
            daemon=True,
        ).start()
        return "Queued"

    def _send_email_safely(self, to_email: str, subject: str, content: str) -> None:
        try:
            self.service.send_email(to_email, subject, content)
        except Exception:
            pass

    @staticmethod
    def _format_flow_records(records: Any) -> str:
        if not records:
            return "No records"

        lines: list[str] = []
        for index, record in enumerate(records, start=1):
            lines.append(CommandHandler._format_one_flow(index, record))
        return " | ".join(lines)

    @staticmethod
    def _format_one_flow(index: int, record: Any) -> str:
        if isinstance(record, dict):
            create_time = record.get("create_time", "")
            flow_type = record.get("type", "")
            amount = float(record.get("amount") or 0)
            balance_after = float(record.get("balance_after") or 0)
            return f"{index} - {create_time} - {flow_type} - {format_money(amount)} - {format_money(balance_after)}"

        if isinstance(record, (list, tuple)) and len(record) >= 5:
            create_time = record[-2]
            flow_type = record[2] if len(record) >= 6 else record[1]
            amount = float(record[3] if len(record) >= 6 else record[2] or 0)
            balance_after = float(record[4] if len(record) >= 6 else record[3] or 0)
            return f"{index} - {create_time} - {flow_type} - {format_money(amount)} - {format_money(balance_after)}"

        return f"{index} - {record}"
