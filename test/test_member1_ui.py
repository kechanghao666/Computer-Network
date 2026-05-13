from __future__ import annotations

import io
import unittest
from contextlib import redirect_stdout
from dataclasses import dataclass

from client.ui import display_response, display_rtt_result, read_amount, read_choice, run_app


@dataclass(frozen=True)
class FakeResponse:
    code: int
    phrase: str
    message: str

    @property
    def raw(self) -> str:
        return f"{self.code} {self.phrase} {self.message}"

    @property
    def is_success(self) -> bool:
        return self.phrase == "OK" and 200 <= self.code < 400


@dataclass(frozen=True)
class FakeRtt:
    success: bool = True
    count: int = 5
    values: list[float] | None = None
    min_ms: float = 1.0
    max_ms: float = 5.0
    avg_ms: float = 3.0
    network_status: str = "网络状态优秀"
    error: str | None = None


class FakeCommunication:
    def __init__(self) -> None:
        self.calls: list[tuple[str, object]] = []

    def connect_server(self) -> bool:
        self.calls.append(("connect_server", None))
        return True

    def login(self, username: str, password: str) -> FakeResponse:
        self.calls.append(("login", (username, password)))
        return FakeResponse(200, "OK", "Login success")

    def query_balance(self) -> FakeResponse:
        self.calls.append(("query_balance", None))
        return FakeResponse(201, "OK", "Balance: 5000.00 RMB")

    def withdraw(self, amount: float) -> FakeResponse:
        self.calls.append(("withdraw", amount))
        return FakeResponse(202, "OK", "Withdraw success")

    def deposit(self, amount: float) -> FakeResponse:
        self.calls.append(("deposit", amount))
        return FakeResponse(203, "OK", "Deposit success")

    def query_flow(self) -> FakeResponse:
        self.calls.append(("query_flow", None))
        return FakeResponse(204, "OK", "Flow query success")

    def test_rtt(self, count: int = 5) -> FakeRtt:
        self.calls.append(("test_rtt", count))
        return FakeRtt(values=[1.0, 2.0, 3.0, 4.0, 5.0])

    def quit_system(self) -> FakeResponse:
        self.calls.append(("quit_system", None))
        return FakeResponse(300, "OK", "Quit success")


class Member1UiTest(unittest.TestCase):
    def test_read_choice_rejects_invalid_option(self) -> None:
        with self.assertRaises(ValueError):
            read_choice(lambda prompt: "9")

    def test_read_amount_accepts_positive_number(self) -> None:
        self.assertEqual(read_amount(lambda prompt: "500"), 500.0)

    def test_read_amount_rejects_invalid_amount(self) -> None:
        with self.assertRaises(ValueError):
            read_amount(lambda prompt: "-1")

    def test_display_response_uses_success_and_error_tags(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            display_response(FakeResponse(201, "OK", "Balance: 5000.00 RMB"))
            display_response(FakeResponse(404, "ERROR", "Please login first"))

        output = buffer.getvalue()
        self.assertIn("[SUCCESS] Balance: 5000.00 RMB", output)
        self.assertIn("[ERROR] Please login first", output)

    def test_display_rtt_result_outputs_statistics(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            display_rtt_result(FakeRtt(values=[1.0, 2.0, 3.0, 4.0, 5.0]))

        output = buffer.getvalue()
        self.assertIn("Min RTT", output)
        self.assertIn("Max RTT", output)
        self.assertIn("Avg RTT", output)

    def test_run_app_calls_member2_snake_case_interfaces(self) -> None:
        fake_comm = FakeCommunication()
        inputs = iter(["1", "zhangsan", "2", "3", "500", "4", "300", "5", "6", "7"])

        buffer = io.StringIO()
        with redirect_stdout(buffer):
            run_app(
                communication=fake_comm,
                input_func=lambda prompt: next(inputs),
                password_func=lambda prompt: "123456",
                pause=False,
            )

        self.assertEqual(
            [call[0] for call in fake_comm.calls],
            [
                "connect_server",
                "login",
                "query_balance",
                "withdraw",
                "deposit",
                "query_flow",
                "test_rtt",
                "quit_system",
            ],
        )


if __name__ == "__main__":
    unittest.main()

