"""成员1调用成员2通信模块的适配器。"""

from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from typing import Any


@dataclass(frozen=True)
class LocalResponse:
    """通信模块未接入时返回的本地错误响应。"""

    raw: str
    code: int
    phrase: str
    message: str

    @property
    def is_success(self) -> bool:
        return False

    @property
    def is_error(self) -> bool:
        return True


@dataclass(frozen=True)
class LocalRttResult:
    """通信模块未接入时返回的 RTT 错误结果。"""

    success: bool
    count: int
    values: list[float]
    min_ms: float | None
    max_ms: float | None
    avg_ms: float | None
    network_status: str
    error: str | None = None


class MissingCommunication:
    """成员2通信模块未合并时的明确错误提示。"""

    error_message = "成员2通信模块 client.communication 尚未接入"

    def connect_server(self, *args: Any, **kwargs: Any) -> bool:
        return False

    def login(self, username: str, password: str) -> LocalResponse:
        return self._error()

    def query_balance(self) -> LocalResponse:
        return self._error()

    def withdraw(self, amount: float) -> LocalResponse:
        return self._error()

    def deposit(self, amount: float) -> LocalResponse:
        return self._error()

    def query_flow(self) -> LocalResponse:
        return self._error()

    def test_rtt(self, count: int = 5) -> LocalRttResult:
        return LocalRttResult(
            success=False,
            count=0,
            values=[],
            min_ms=None,
            max_ms=None,
            avg_ms=None,
            network_status="通信模块未接入",
            error=self.error_message,
        )

    def quit_system(self) -> LocalResponse:
        return self._error()

    def close_connection(self) -> None:
        return None

    def _error(self) -> LocalResponse:
        return LocalResponse(
            raw=f"500 ERROR {self.error_message}",
            code=500,
            phrase="ERROR",
            message=self.error_message,
        )


def load_communication() -> Any:
    """优先加载成员2的 client.communication 模块。"""
    try:
        return import_module("client.communication")
    except ModuleNotFoundError:
        return MissingCommunication()

