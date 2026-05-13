"""ATM 客户端入口程序。

默认启动图形化界面；如需命令行界面，可使用 --cli 参数。
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bank ATM client")
    parser.add_argument(
        "--cli",
        action="store_true",
        help="start the command-line client instead of the graphical client",
    )
    return parser.parse_args()


def run_gui() -> None:
    from client.gui_client import main as gui_main

    gui_main()


def run_cli() -> None:
    from client.ui import run_app

    run_app()


if __name__ == "__main__":
    args = parse_args()
    try:
        if args.cli:
            run_cli()
        else:
            run_gui()
    except KeyboardInterrupt:
        print("\n[INFO] Client interrupted and exited.")
