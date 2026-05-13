"""ATM 客户端命令行界面与用户输入处理。"""

from __future__ import annotations

import getpass
import sys
from typing import Any, Callable

from client.communication_adapter import load_communication


WIDTH = 50
MONEY_UNIT = "RMB"


def configure_stdio() -> None:
    """尽量使用 UTF-8 输出，降低 Windows 终端乱码概率。"""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        except Exception:
            pass


def border(char: str = "=") -> str:
    return char * WIDTH


def center_text(text: str) -> str:
    return text.center(WIDTH)


def print_startup() -> None:
    """显示客户端启动界面。"""
    print(border("="))
    print(center_text("Bank ATM System"))
    print(border("="))
    print("[INFO] Welcome to Bank ATM client.")
    print("[INFO] Default server: 127.0.0.1:8888")
    print(border("-"))


def print_main_menu(username: str | None, connected: bool) -> None:
    """显示主菜单、登录状态和服务器连接状态。"""
    user_status = f"Logged in as {username}" if username else "Not logged in"
    server_status = "Connected" if connected else "Not connected"

    print(border("="))
    print(center_text("Bank ATM System"))
    print(border("="))
    print(f"User Status : {user_status}")
    print(f"Server      : 127.0.0.1:8888  {server_status}")
    print(border("-"))
    print("1. Login")
    print("2. Balance Query")
    print("3. Withdraw")
    print("4. Deposit")
    print("5. Transaction Flow Query")
    print("6. Network RTT Test")
    print("7. Logout / Exit")
    print(border("-"))


def read_choice(input_func: Callable[[str], str] = input) -> str:
    """读取菜单选项。"""
    choice = input_func("Please enter your choice: ").strip()
    if choice not in {"1", "2", "3", "4", "5", "6", "7"}:
        raise ValueError("Please enter a number from 1 to 7.")
    return choice


def read_login(
    input_func: Callable[[str], str] = input,
    password_func: Callable[[str], str] | None = None,
) -> tuple[str, str]:
    """读取用户名和密码，并检查非空。"""
    password_reader = password_func or getpass.getpass
    username = input_func("Username: ").strip()
    password = password_reader("Password: ").strip()
    if not username or not password:
        raise ValueError("Username and password cannot be empty.")
    return username, password


def read_amount(input_func: Callable[[str], str] = input) -> float:
    """读取并校验金额，金额必须为正数。"""
    raw = input_func("Amount: ").strip()
    try:
        amount = float(raw)
    except ValueError as exc:
        raise ValueError("Amount must be a positive number.") from exc
    if amount <= 0:
        raise ValueError("Amount must be a positive number.")
    return amount


def wait_return(input_func: Callable[[str], str] = input, pause: bool = True) -> None:
    """每次操作结束后停留，避免结果一闪而过。"""
    if pause:
        input_func("Press Enter to return to menu...")


def display_response(response: Any) -> None:
    """按成功、失败、提示三类显示服务器返回结果。"""
    code = getattr(response, "code", None)
    phrase = str(getattr(response, "phrase", "")).upper()
    raw = str(getattr(response, "raw", response))
    message = str(getattr(response, "message", raw))

    if phrase == "OK" or (isinstance(code, int) and 200 <= code < 400):
        tag = "[SUCCESS]"
    elif phrase == "ERROR" or (isinstance(code, int) and code >= 400):
        tag = "[ERROR]"
    else:
        tag = "[INFO]"

    print(tag, message if message else raw)


def display_rtt_result(result: Any) -> None:
    """显示 RTT 测试结果。"""
    if not getattr(result, "success", False):
        print(f"[ERROR] RTT test failed: {getattr(result, 'error', 'Unknown error')}")
        return

    values = list(getattr(result, "values", []))
    print("[SUCCESS] Network RTT Test")
    for index, value in enumerate(values, start=1):
        print(f"RTT {index:<2}: {value:.2f} ms")
    print(f"Min RTT : {getattr(result, 'min_ms', 0):.2f} ms")
    print(f"Max RTT : {getattr(result, 'max_ms', 0):.2f} ms")
    print(f"Avg RTT : {getattr(result, 'avg_ms', 0):.2f} ms")
    print(f"Status  : {getattr(result, 'network_status', '')}")


def display_money(label: str, amount: float) -> None:
    """统一金额显示格式。"""
    print(f"{label}: {amount:.2f} {MONEY_UNIT}")


def run_app(
    communication: Any | None = None,
    input_func: Callable[[str], str] = input,
    password_func: Callable[[str], str] | None = None,
    pause: bool = True,
) -> None:
    """运行 ATM 客户端主循环。"""
    configure_stdio()
    comm = communication or load_communication()
    username: str | None = None

    connected = False
    try:
        connected = bool(comm.connect_server())
    except Exception as exc:
        print(f"[ERROR] Unable to connect server: {exc}")

    print_startup()

    while True:
        print_main_menu(username, connected)
        try:
            choice = read_choice(input_func)
        except ValueError as exc:
            print(f"[ERROR] {exc}")
            wait_return(input_func, pause)
            continue

        try:
            if choice == "1":
                username_input, password = read_login(input_func, password_func)
                response = comm.login(username_input, password)
                display_response(response)
                if getattr(response, "is_success", False):
                    username = username_input
            elif choice == "2":
                display_response(comm.query_balance())
            elif choice == "3":
                amount = read_amount(input_func)
                display_response(comm.withdraw(amount))
            elif choice == "4":
                amount = read_amount(input_func)
                display_response(comm.deposit(amount))
            elif choice == "5":
                display_response(comm.query_flow())
            elif choice == "6":
                display_rtt_result(comm.test_rtt(5))
            elif choice == "7":
                display_response(comm.quit_system())
                return
        except ValueError as exc:
            print(f"[ERROR] {exc}")
        except Exception as exc:
            print(f"[ERROR] {exc}")

        wait_return(input_func, pause)

