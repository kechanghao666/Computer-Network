"""ATM 客户端 Socket 通信模块。

成员2负责的范围：
- 建立并关闭 TCP 连接；
- 按统一协议封装请求；
- 接收并解析服务器响应状态码；
- 提供登录、余额查询、取款、存款、流水查询、RTT 测试等函数。
"""

from __future__ import annotations

import socket
import statistics
import time
from dataclasses import dataclass
from typing import Optional


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8888
DEFAULT_TIMEOUT = 5.0
ENCODING = "utf-8"
MESSAGE_END = "\n"


@dataclass(frozen=True)
class AtmResponse:
    """服务器响应解析结果。"""

    raw: str
    code: int
    phrase: str
    message: str

    @property
    def is_success(self) -> bool:
        """判断响应是否表示成功。"""
        return 200 <= self.code < 400 and self.phrase.upper() == "OK"

    @property
    def is_error(self) -> bool:
        """判断响应是否表示失败。"""
        return not self.is_success


@dataclass(frozen=True)
class RttResult:
    """RTT 测试统计结果，单位为毫秒。"""

    success: bool
    count: int
    values: list[float]
    min_ms: Optional[float]
    max_ms: Optional[float]
    avg_ms: Optional[float]
    network_status: str
    error: Optional[str] = None


class CommunicationError(RuntimeError):
    """通信层异常。"""


class AtmCommunication:
    """ATM 客户端与银行中央服务器之间的 TCP 通信客户端。"""

    def __init__(
        self,
        host: str = DEFAULT_HOST,
        port: int = DEFAULT_PORT,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout
        self._socket: Optional[socket.socket] = None
        self._recv_buffer = ""

    @property
    def is_connected(self) -> bool:
        """判断当前是否已经建立 Socket 连接。"""
        return self._socket is not None

    def connect_server(
        self,
        ip: Optional[str] = None,
        port: Optional[int] = None,
        timeout: Optional[float] = None,
    ) -> bool:
        """连接银行中央服务器，默认地址为 127.0.0.1:8888。"""
        if ip is not None:
            self.host = ip
        if port is not None:
            self.port = port
        if timeout is not None:
            self.timeout = timeout

        self.close_connection()

        try:
            client_socket = socket.create_connection(
                (self.host, self.port),
                timeout=self.timeout,
            )
            client_socket.settimeout(self.timeout)
        except OSError as exc:
            raise CommunicationError(f"无法连接服务器 {self.host}:{self.port}") from exc

        self._socket = client_socket
        self._recv_buffer = ""
        return True

    def send_request(self, request: str) -> bool:
        """发送一条协议请求，请求末尾统一添加换行符。"""
        client_socket = self._require_socket()
        request_text = self._normalize_request(request)

        try:
            client_socket.sendall(request_text.encode(ENCODING))
        except OSError as exc:
            self.close_connection()
            raise CommunicationError("请求发送失败，服务器可能已断开") from exc

        return True

    def receive_response(self) -> AtmResponse:
        """接收一条服务器响应，并解析状态码、状态短语和消息内容。"""
        line = self._receive_line()
        return parse_response(line)

    def request(self, request_text: str) -> AtmResponse:
        """发送请求并接收响应。"""
        self.send_request(request_text)
        return self.receive_response()

    def login(self, username: str, password: str) -> AtmResponse:
        """登录系统，先发送 HELO 用户名，再发送 PASS 密码。"""
        username = username.strip()
        password = password.strip()
        if not username or not password:
            return build_local_error("用户名和密码不能为空")

        helo_response = self.request(f"HELO {username}")
        if helo_response.is_error:
            return helo_response

        return self.request(f"PASS {password}")

    def query_balance(self) -> AtmResponse:
        """查询当前登录用户余额。"""
        return self.request("BALA")

    def withdraw(self, amount: float | int | str) -> AtmResponse:
        """发送取款请求。"""
        formatted_amount = format_amount(amount)
        if formatted_amount is None:
            return build_local_error("金额必须为大于 0 的数字")
        return self.request(f"WITHDRAW {formatted_amount}")

    def deposit(self, amount: float | int | str) -> AtmResponse:
        """发送存款请求。"""
        formatted_amount = format_amount(amount)
        if formatted_amount is None:
            return build_local_error("金额必须为大于 0 的数字")
        return self.request(f"DEPOSIT {formatted_amount}")

    def query_flow(self) -> AtmResponse:
        """查询当前登录用户交易流水。"""
        return self.request("FLOW")

    def test_rtt(self, count: int = 5) -> RttResult:
        """发送 PING 并统计 RTT，默认至少测试 5 次。"""
        if count < 5:
            count = 5

        values: list[float] = []
        try:
            for _ in range(count):
                start = time.perf_counter()
                response = self.request("PING")
                elapsed_ms = (time.perf_counter() - start) * 1000

                if response.raw.upper() != "PONG":
                    return RttResult(
                        success=False,
                        count=len(values),
                        values=values,
                        min_ms=min(values) if values else None,
                        max_ms=max(values) if values else None,
                        avg_ms=statistics.mean(values) if values else None,
                        network_status="测试失败",
                        error=response.raw,
                    )

                values.append(elapsed_ms)
        except CommunicationError as exc:
            return RttResult(
                success=False,
                count=len(values),
                values=values,
                min_ms=min(values) if values else None,
                max_ms=max(values) if values else None,
                avg_ms=statistics.mean(values) if values else None,
                network_status="连接异常",
                error=str(exc),
            )

        avg_ms = statistics.mean(values)
        return RttResult(
            success=True,
            count=len(values),
            values=values,
            min_ms=min(values),
            max_ms=max(values),
            avg_ms=avg_ms,
            network_status=classify_network(avg_ms),
        )

    def quit_system(self) -> AtmResponse:
        """通知服务器退出系统，并关闭客户端连接。"""
        try:
            return self.request("QUIT")
        finally:
            self.close_connection()

    def close_connection(self) -> None:
        """关闭 Socket 连接。"""
        if self._socket is None:
            return

        try:
            self._socket.close()
        finally:
            self._socket = None
            self._recv_buffer = ""

    def _require_socket(self) -> socket.socket:
        if self._socket is None:
            raise CommunicationError("尚未连接服务器")
        return self._socket

    def _receive_line(self) -> str:
        client_socket = self._require_socket()

        try:
            while MESSAGE_END not in self._recv_buffer:
                data = client_socket.recv(4096)
                if not data:
                    self.close_connection()
                    raise CommunicationError("服务器连接已断开")
                self._recv_buffer += data.decode(ENCODING)
        except socket.timeout as exc:
            raise CommunicationError("接收响应超时") from exc
        except UnicodeDecodeError as exc:
            raise CommunicationError("服务器响应不是 UTF-8 编码") from exc
        except OSError as exc:
            self.close_connection()
            raise CommunicationError("接收响应失败") from exc

        line, self._recv_buffer = self._recv_buffer.split(MESSAGE_END, 1)
        return line.strip()

    @staticmethod
    def _normalize_request(request: str) -> str:
        request = request.strip()
        if not request:
            raise CommunicationError("请求内容不能为空")
        return f"{request}{MESSAGE_END}"


def parse_response(response_text: str) -> AtmResponse:
    """解析 StatusCode StatusPhrase Data 格式响应。"""
    response_text = response_text.strip()
    if response_text.upper() == "PONG":
        return AtmResponse(raw=response_text, code=200, phrase="OK", message="PONG")

    parts = response_text.split(maxsplit=2)
    if len(parts) < 2 or not parts[0].isdigit():
        return AtmResponse(
            raw=response_text,
            code=500,
            phrase="ERROR",
            message="Invalid response format",
        )

    code = int(parts[0])
    phrase = parts[1]
    message = parts[2] if len(parts) == 3 else ""
    return AtmResponse(raw=response_text, code=code, phrase=phrase, message=message)


def format_amount(amount: float | int | str) -> Optional[str]:
    """将金额格式化为两位小数，非法金额返回 None。"""
    try:
        value = float(str(amount).strip())
    except (TypeError, ValueError):
        return None

    if value <= 0:
        return None

    return f"{value:.2f}"


def build_local_error(message: str) -> AtmResponse:
    """构造客户端本地校验错误响应。"""
    return AtmResponse(
        raw=f"403 ERROR {message}",
        code=403,
        phrase="ERROR",
        message=message,
    )


def classify_network(avg_ms: float) -> str:
    """根据平均 RTT 给出简单网络状态。"""
    if avg_ms < 50:
        return "网络状态优秀"
    if avg_ms < 150:
        return "网络状态良好"
    if avg_ms < 300:
        return "网络状态一般"
    return "网络状态较差"


_default_client = AtmCommunication()


def connect_server(
    ip: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    timeout: float = DEFAULT_TIMEOUT,
) -> bool:
    """模块级连接函数，供成员1直接调用。"""
    return _default_client.connect_server(ip, port, timeout)


def send_request(request: str) -> bool:
    """模块级请求发送函数。"""
    return _default_client.send_request(request)


def receive_response() -> AtmResponse:
    """模块级响应接收函数。"""
    return _default_client.receive_response()


def login(username: str, password: str) -> AtmResponse:
    """模块级登录函数。"""
    return _default_client.login(username, password)


def query_balance() -> AtmResponse:
    """模块级余额查询函数。"""
    return _default_client.query_balance()


def withdraw(amount: float | int | str) -> AtmResponse:
    """模块级取款函数。"""
    return _default_client.withdraw(amount)


def deposit(amount: float | int | str) -> AtmResponse:
    """模块级存款函数。"""
    return _default_client.deposit(amount)


def query_flow() -> AtmResponse:
    """模块级流水查询函数。"""
    return _default_client.query_flow()


def test_rtt(count: int = 5) -> RttResult:
    """模块级 RTT 测试函数。"""
    return _default_client.test_rtt(count)


def quit_system() -> AtmResponse:
    """模块级退出函数。"""
    return _default_client.quit_system()


def close_connection() -> None:
    """模块级关闭连接函数。"""
    _default_client.close_connection()

