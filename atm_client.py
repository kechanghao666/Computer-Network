# -*- coding: utf-8 -*-
"""
银行 ATM 客户端（成员1）：界面、输入校验、菜单与结果显示。
通信由 client_comm_adapter 提供，不包含 Socket 等底层实现。
"""

from __future__ import annotations

import sys

import client_comm_adapter as comm


def _try_utf8_stdio() -> None:
    """尽量将标准输出/错误设为 UTF-8，降低 Windows 控制台中文乱码概率；失败则忽略。"""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        except Exception:
            pass


def _print_separator() -> None:
    print("-" * 48)


def show_startup() -> None:
    """客户端启动界面：系统名称、欢迎信息、连接提示。"""
    _print_separator()
    print("       银行 ATM 自助服务系统（客户端）")
    _print_separator()
    print("欢迎您使用本系统。")
    print("连接提示：请确认本机网络正常，且成员2 通信服务已就绪后再操作。")
    _print_separator()
    print()


def show_main_menu() -> None:
    """主菜单界面。"""
    print("主菜单 — 请输入选项编号（1-7）：")
    print("  1. Login")
    print("  2. Balance Query")
    print("  3. Withdraw")
    print("  4. Deposit")
    print("  5. Transaction Flow Query")
    print("  6. Network RTT Test")
    print("  7. Exit")
    _print_separator()


def read_menu_choice() -> str:
    """读取主菜单选择，仅接受 1-7。"""
    raw = input("请选择 [1-7]: ").strip()
    if raw not in {"1", "2", "3", "4", "5", "6", "7"}:
        raise ValueError("菜单输入无效，请输入 1 到 7 的数字。")
    return raw


def print_server_result(title: str, message: str) -> None:
    """将通信函数返回结果清晰展示给用户。"""
    print()
    _print_separator()
    print(title)
    _print_separator()
    print(message)
    _print_separator()
    print()


def do_login() -> None:
    """登录：用户名、密码非空校验，调用 login()。"""
    print("\n【登录】请输入凭据（用户名与密码均不能为空，输入 q 放弃返回主菜单）。")
    while True:
        try:
            username = input("用户名: ").strip()
        except EOFError:
            print("输入结束，返回主菜单。")
            return

        if username.lower() == "q":
            print("已取消登录，返回主菜单。")
            return

        try:
            password = input("密码: ").strip()
        except EOFError:
            print("输入结束，返回主菜单。")
            return

        if not username or not password:
            print("提示：用户名和密码不能为空，请重新输入。")
            continue

        break

    try:
        result = comm.login(username, password)
    except Exception as exc:  # noqa: BLE001 — 客户端需避免因通信层异常崩溃
        print_server_result("登录 — 调用异常", str(exc))
        return

    print_server_result("登录 — 服务器返回", result)


def prompt_positive_amount_or_quit(action_label: str) -> float | None:
    """
    循环读取金额：须为数字且大于 0。
    输入 q/Q 表示放弃并返回主菜单；EOF 视为放弃。
    """
    while True:
        try:
            raw = input(
                f"{action_label}请输入金额（正数），输入 q 放弃并返回主菜单: "
            ).strip()
        except EOFError:
            print("输入结束，返回主菜单。")
            return None

        if raw.lower() == "q":
            print("已取消操作，返回主菜单。")
            return None

        try:
            value = float(raw)
        except ValueError:
            print("提示：金额必须是有效数字，请重新输入。")
            continue

        if value <= 0:
            print("提示：金额必须大于 0，请重新输入。")
            continue

        return value


def do_withdraw() -> None:
    """取款入口：校验金额后调用 withdraw(amount)。"""
    print("\n【取款】")
    amount = prompt_positive_amount_or_quit("")
    if amount is None:
        return

    try:
        result = comm.withdraw(amount)
    except Exception as exc:  # noqa: BLE001
        print_server_result("取款 — 调用异常", str(exc))
        return

    print_server_result("取款 — 服务器返回", result)


def do_deposit() -> None:
    """存款入口：校验金额后调用 deposit(amount)。"""
    print("\n【存款】")
    amount = prompt_positive_amount_or_quit("")
    if amount is None:
        return

    try:
        result = comm.deposit(amount)
    except Exception as exc:  # noqa: BLE001
        print_server_result("存款 — 调用异常", str(exc))
        return

    print_server_result("存款 — 服务器返回", result)


def do_balance_query() -> None:
    """余额查询：调用 queryBalance()。"""
    print("\n【余额查询】正在请求服务器…")
    try:
        result = comm.queryBalance()
    except Exception as exc:  # noqa: BLE001
        print_server_result("余额查询 — 调用异常", str(exc))
        return

    print_server_result("余额查询 — 服务器返回", result)


def do_flow_query() -> None:
    """流水查询：调用 queryFlow()。"""
    print("\n【交易流水查询】正在请求服务器…")
    try:
        result = comm.queryFlow()
    except Exception as exc:  # noqa: BLE001
        print_server_result("流水查询 — 调用异常", str(exc))
        return

    print_server_result("流水查询 — 服务器返回", result)


def do_rtt_test() -> None:
    """RTT 测试：调用 testRTT()。"""
    print("\n【网络 RTT 测试】正在请求服务器…")
    try:
        result = comm.testRTT()
    except Exception as exc:  # noqa: BLE001
        print_server_result("RTT 测试 — 调用异常", str(exc))
        return

    print_server_result("RTT 测试 — 服务器返回", result)


def do_exit() -> None:
    """退出：调用 quitSystem() 后正常结束程序。"""
    print("\n【退出】正在通知服务器并退出…")
    try:
        result = comm.quitSystem()
    except Exception as exc:  # noqa: BLE001
        print_server_result("退出 — 调用异常（仍将尝试退出进程）", str(exc))
        sys.exit(0)

    print_server_result("退出 — 服务器返回", result)
    sys.exit(0)


def main() -> None:
    _try_utf8_stdio()
    show_startup()

    while True:
        show_main_menu()
        try:
            choice = read_menu_choice()
        except ValueError as err:
            print(str(err))
            continue
        except EOFError:
            print("\n检测到输入结束，正在退出…")
            do_exit()

        if choice == "1":
            do_login()
        elif choice == "2":
            do_balance_query()
        elif choice == "3":
            do_withdraw()
        elif choice == "4":
            do_deposit()
        elif choice == "5":
            do_flow_query()
        elif choice == "6":
            do_rtt_test()
        elif choice == "7":
            do_exit()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n已中断，正在尝试正常退出…")
        try:
            print_server_result("退出 — 服务器返回", comm.quitSystem())
        except Exception:  # noqa: BLE001
            pass
        sys.exit(0)
