"""Graphical ATM client based on Tkinter."""

from __future__ import annotations

from pathlib import Path
import sys
import threading
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from client.communication import AtmCommunication, CommunicationError


class AtmGuiApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Bank ATM System")
        self.root.geometry("760x560")
        self.root.minsize(720, 520)

        self.client: AtmCommunication | None = None
        self.username: str | None = None
        self.busy = False

        self.host_var = tk.StringVar(value="127.0.0.1")
        self.port_var = tk.StringVar(value="8888")
        self.username_var = tk.StringVar(value="zhangsan")
        self.password_var = tk.StringVar(value="123456")
        self.amount_var = tk.StringVar(value="100")
        self.status_var = tk.StringVar(value="Not connected")

        self._build_ui()

    def _build_ui(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(2, weight=1)

        header = ttk.Frame(self.root, padding=(14, 12))
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(1, weight=1)
        ttk.Label(header, text="Bank ATM System", font=("Segoe UI", 18, "bold")).grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(header, textvariable=self.status_var).grid(row=0, column=1, sticky="e")

        form = ttk.Frame(self.root, padding=(14, 4))
        form.grid(row=1, column=0, sticky="ew")
        for col in (1, 3, 5):
            form.columnconfigure(col, weight=1)

        ttk.Label(form, text="Host").grid(row=0, column=0, sticky="w", padx=(0, 6))
        ttk.Entry(form, textvariable=self.host_var, width=16).grid(row=0, column=1, sticky="ew", padx=(0, 12))
        ttk.Label(form, text="Port").grid(row=0, column=2, sticky="w", padx=(0, 6))
        ttk.Entry(form, textvariable=self.port_var, width=8).grid(row=0, column=3, sticky="ew", padx=(0, 12))
        ttk.Button(form, text="Connect", command=self.connect).grid(row=0, column=4, sticky="ew", padx=(0, 6))
        ttk.Button(form, text="Quit", command=self.quit_system).grid(row=0, column=5, sticky="ew")

        ttk.Label(form, text="Username").grid(row=1, column=0, sticky="w", padx=(0, 6), pady=(10, 0))
        ttk.Entry(form, textvariable=self.username_var).grid(row=1, column=1, sticky="ew", padx=(0, 12), pady=(10, 0))
        ttk.Label(form, text="Password").grid(row=1, column=2, sticky="w", padx=(0, 6), pady=(10, 0))
        ttk.Entry(form, textvariable=self.password_var, show="*").grid(row=1, column=3, sticky="ew", padx=(0, 12), pady=(10, 0))
        ttk.Button(form, text="Login", command=self.login).grid(row=1, column=4, columnspan=2, sticky="ew", pady=(10, 0))

        ttk.Label(form, text="Amount").grid(row=2, column=0, sticky="w", padx=(0, 6), pady=(10, 0))
        ttk.Entry(form, textvariable=self.amount_var).grid(row=2, column=1, sticky="ew", padx=(0, 12), pady=(10, 0))
        ttk.Button(form, text="Balance", command=self.query_balance).grid(row=2, column=2, sticky="ew", padx=(0, 6), pady=(10, 0))
        ttk.Button(form, text="Withdraw", command=self.withdraw).grid(row=2, column=3, sticky="ew", padx=(0, 6), pady=(10, 0))
        ttk.Button(form, text="Deposit", command=self.deposit).grid(row=2, column=4, sticky="ew", padx=(0, 6), pady=(10, 0))
        ttk.Button(form, text="Flow", command=self.query_flow).grid(row=2, column=5, sticky="ew", pady=(10, 0))

        actions = ttk.Frame(self.root, padding=(14, 4))
        actions.grid(row=3, column=0, sticky="ew")
        actions.columnconfigure(0, weight=1)
        actions.columnconfigure(1, weight=1)
        ttk.Button(actions, text="RTT Test", command=self.test_rtt).grid(row=0, column=0, sticky="ew", padx=(0, 8))
        ttk.Button(actions, text="Clear Output", command=self.clear_output).grid(row=0, column=1, sticky="ew")

        output_frame = ttk.Frame(self.root, padding=(14, 8))
        output_frame.grid(row=2, column=0, sticky="nsew")
        output_frame.rowconfigure(0, weight=1)
        output_frame.columnconfigure(0, weight=1)
        self.output = tk.Text(output_frame, wrap="word", height=16)
        self.output.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(output_frame, command=self.output.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.output.configure(yscrollcommand=scrollbar.set)

        self._append("GUI client ready. Start server first, then click Connect.\n")

    def connect(self) -> None:
        host = self.host_var.get().strip() or "127.0.0.1"
        try:
            port = int(self.port_var.get().strip())
        except ValueError:
            messagebox.showerror("Connect", "Port must be a number.")
            return

        def task() -> str:
            client = AtmCommunication(host=host, port=port)
            client.connect_server()
            self.client = client
            return f"Connected to {host}:{port}"

        self._run_task("Connect", task, self._set_connected)

    def login(self) -> None:
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        if not username or not password:
            messagebox.showerror("Login", "Username and password cannot be empty.")
            return

        def task():
            client = self._require_client()
            response = client.login(username, password)
            if response.is_success:
                self.username = username
            return response.raw

        self._run_task("Login", task)

    def query_balance(self) -> None:
        self._run_task("Balance", lambda: self._require_client().query_balance().raw)

    def withdraw(self) -> None:
        amount = self._amount_or_none()
        if amount is None:
            return
        self._run_task("Withdraw", lambda: self._require_client().withdraw(amount).raw)

    def deposit(self) -> None:
        amount = self._amount_or_none()
        if amount is None:
            return
        self._run_task("Deposit", lambda: self._require_client().deposit(amount).raw)

    def query_flow(self) -> None:
        self._run_task("Flow", lambda: self._require_client().query_flow().raw)

    def test_rtt(self) -> None:
        def task() -> str:
            result = self._require_client().test_rtt(5)
            if not result.success:
                return f"RTT failed: {result.error}"
            lines = [
                "RTT test success",
                *(f"RTT {index}: {value:.2f} ms" for index, value in enumerate(result.values, start=1)),
                f"Min: {result.min_ms:.2f} ms",
                f"Max: {result.max_ms:.2f} ms",
                f"Avg: {result.avg_ms:.2f} ms",
                f"Status: {result.network_status}",
            ]
            if result.record_id is not None:
                lines.append(f"Saved as RTT record #{result.record_id}")
            return "\n".join(lines)

        self._run_task("RTT Test", task)

    def quit_system(self) -> None:
        if self.client is None:
            self.root.destroy()
            return

        def task() -> str:
            response = self.client.quit_system()
            return response.raw

        def done(_: str) -> None:
            self.status_var.set("Disconnected")
            self.root.destroy()

        self._run_task("Quit", task, done)

    def clear_output(self) -> None:
        self.output.delete("1.0", tk.END)

    def _require_client(self) -> AtmCommunication:
        if self.client is None or not self.client.is_connected:
            raise CommunicationError("Please connect to server first.")
        return self.client

    def _amount_or_none(self) -> str | None:
        amount = self.amount_var.get().strip()
        if not amount:
            messagebox.showerror("Amount", "Amount cannot be empty.")
            return None
        return amount

    def _run_task(
        self,
        title: str,
        func: Callable[[], object],
        on_success: Callable[[object], None] | None = None,
    ) -> None:
        if self.busy:
            return
        self.busy = True
        self.status_var.set(f"{title} running...")

        def worker() -> None:
            try:
                result = func()
            except Exception as exc:
                self.root.after(0, lambda exc=exc: self._task_failed(title, exc))
                return
            self.root.after(0, lambda: self._task_done(title, result, on_success))

        threading.Thread(target=worker, daemon=True).start()

    def _task_done(
        self,
        title: str,
        result: object,
        on_success: Callable[[object], None] | None,
    ) -> None:
        self.busy = False
        self.status_var.set(f"Logged in as {self.username}" if self.username else "Connected")
        self._append(f"[{title}]\n{result}\n\n")
        if on_success is not None:
            on_success(result)

    def _task_failed(self, title: str, exc: Exception) -> None:
        self.busy = False
        self.status_var.set("Error")
        self._append(f"[{title} ERROR]\n{exc}\n\n")
        messagebox.showerror(title, str(exc))

    def _set_connected(self, result: object) -> None:
        self.status_var.set(str(result))

    def _append(self, text: str) -> None:
        self.output.insert(tk.END, text)
        self.output.see(tk.END)


def main() -> None:
    root = tk.Tk()
    AtmGuiApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
