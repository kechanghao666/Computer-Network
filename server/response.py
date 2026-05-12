"""服务器响应报文封装。"""

from __future__ import annotations


STATUS_TEXT = {
    200: "OK Login success",
    201: "OK Balance query success",
    202: "OK Withdraw success",
    203: "OK Deposit success",
    204: "OK Flow query success",
    300: "OK Quit success",
    400: "ERROR Wrong password",
    401: "ERROR User not found",
    402: "ERROR Insufficient balance",
    403: "ERROR Invalid amount",
    404: "ERROR Please login first",
    500: "ERROR Server error",
}


def ensure_newline(message: str) -> str:
    """保证每条响应都以换行符结束，符合统一通信协议。"""
    return message if message.endswith("\n") else f"{message}\n"


def build_response(status_code: int, detail: str | None = None) -> str:
    """按 StatusCode StatusPhrase Data 格式构造服务器响应。"""
    text = detail if detail is not None else STATUS_TEXT.get(status_code, "ERROR Server error")
    return ensure_newline(f"{status_code} {text}")


def format_money(amount: float) -> str:
    """统一金额展示格式。"""
    return f"{amount:.2f} RMB"

