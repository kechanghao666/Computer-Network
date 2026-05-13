"""ATM 客户端入口程序。"""

from __future__ import annotations

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from client.ui import run_app


if __name__ == "__main__":
    try:
        run_app()
    except KeyboardInterrupt:
        print("\n[INFO] Client interrupted and exited.")

