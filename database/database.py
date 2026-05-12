import sqlite3
from pathlib import Path


DEFAULT_DB_PATH = Path(__file__).with_name("atm.db")


def connect_database(db_path=DEFAULT_DB_PATH):
    """连接 SQLite 数据库，并统一启用字典式查询结果。"""
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    return connection
