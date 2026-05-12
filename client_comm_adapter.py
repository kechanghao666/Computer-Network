# -*- coding: utf-8 -*-
"""
ATM 客户端通信适配层（成员1 调用入口 / 成员2 实现协议）。

当前为占位实现，返回模拟字符串，便于成员1 界面独立联调。
成员2 完成 Socket 通信后：将各函数体替换为真实请求，或改为从成员2 模块 import 并转发调用。

TODO（成员2）：用真实网络通信替换以下全部对外函数：
  - login(username, password)
  - queryBalance()
  - withdraw(amount)
  - deposit(amount)
  - queryFlow()
  - testRTT()
  - quitSystem()
"""

from __future__ import annotations

# 若成员2 已提供统一模块，可在此 import 并删除占位实现。示例（模块名以实际为准）：
# from atm_socket_client import (
#     login,
#     query_balance as queryBalance,
#     ...
# )


def login(username: str, password: str) -> str:
    """登录请求。TODO：后续替换为成员2 真实通信函数。"""
    return (
        f"[模拟响应] 登录已受理。\n"
        f"用户名: {username}\n"
        f"说明: 当前为占位数据，未连接服务器。"
    )


def queryBalance() -> str:
    """余额查询。TODO：后续替换为成员2 真实通信函数。"""
    return "[模拟响应] 当前余额: 12345.67 元（占位数据）"


def withdraw(amount: float) -> str:
    """取款请求。TODO：后续替换为成员2 真实通信函数。"""
    return f"[模拟响应] 取款 {amount:.2f} 元已受理（占位数据）"


def deposit(amount: float) -> str:
    """存款请求。TODO：后续替换为成员2 真实通信函数。"""
    return f"[模拟响应] 存款 {amount:.2f} 元已受理（占位数据）"


def queryFlow() -> str:
    """交易流水查询。TODO：后续替换为成员2 真实通信函数。"""
    return (
        "[模拟响应] 最近流水（占位）:\n"
        "  2026-05-01  存款  +100.00 元\n"
        "  2026-05-02  取款  -50.00 元"
    )


def testRTT() -> str:
    """网络 RTT 测试。TODO：后续替换为成员2 真实通信函数。"""
    return "[模拟响应] RTT 约 12ms（占位，未实际测量）"


def quitSystem() -> str:
    """通知服务端正常退出/登出。TODO：后续替换为成员2 真实通信函数。"""
    return "[模拟响应] 已与服务器同步退出会话（占位数据）"
