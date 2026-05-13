"""银行中央服务器主程序。"""

from __future__ import annotations

import argparse
import socket
import sys
import threading
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from server.command_handler import CommandHandler


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8888
BUFFER_SIZE = 4096


def handle_client(client_socket: socket.socket, address: tuple[str, int]) -> None:
    """处理单个客户端连接，按行接收请求并返回响应。"""
    handler = CommandHandler()
    receive_buffer = b""
    print(f"[INFO] Client connected: {address[0]}:{address[1]}")

    with client_socket:
        while True:
            try:
                data = client_socket.recv(BUFFER_SIZE)
            except ConnectionResetError:
                break
            if not data:
                break

            receive_buffer += data
            while b"\n" in receive_buffer:
                raw_request, receive_buffer = receive_buffer.split(b"\n", 1)
                request = raw_request.decode("utf-8", errors="replace").strip()
                if not request.strip():
                    continue
                result = handler.handle_request(request)
                client_socket.sendall(result.response.encode("utf-8"))
                if result.close_connection:
                    print(f"[INFO] Client quit: {address[0]}:{address[1]}")
                    return

    print(f"[INFO] Client disconnected: {address[0]}:{address[1]}")


def start_server(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:
    """启动银行中央服务器。"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((host, port))
        server_socket.listen()
        print(f"[INFO] Bank server started on {host}:{port}")
        print("[INFO] Waiting for ATM client connections...")

        while True:
            try:
                client_socket, address = server_socket.accept()
            except KeyboardInterrupt:
                print("\n[INFO] Bank server stopped")
                break

            client_thread = threading.Thread(
                target=handle_client,
                args=(client_socket, address),
                daemon=True,
            )
            client_thread.start()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bank ATM central server")
    parser.add_argument("--host", default=DEFAULT_HOST, help="server bind address")
    parser.add_argument("--port", default=DEFAULT_PORT, type=int, help="server bind port")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    start_server(args.host, args.port)
