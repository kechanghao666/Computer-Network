from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from contextlib import closing

try:
    from .database import DEFAULT_DB_PATH, connect_database
except ImportError:
    from database import DEFAULT_DB_PATH, connect_database


MONEY_QUANT = Decimal("0.01")
SEED_ACCOUNTS = (
    ("zhangsan", "123456", 5000.00, "zhangsan@qq.com", 1),
    ("lisi", "123456", 3000.00, "lisi@qq.com", 1),
    ("admin", "123456", 10000.00, "admin@qq.com", 1),
)


def init_database(db_path=DEFAULT_DB_PATH):
    """初始化数据库表结构，并写入统一测试账号。"""
    with closing(connect_database(db_path)) as connection:
        with connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS account (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    balance REAL NOT NULL,
                    email TEXT,
                    status INTEGER
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS transaction_flow (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    type TEXT NOT NULL,
                    amount REAL,
                    balance_after REAL,
                    create_time TEXT,
                    remark TEXT
                )
                """
            )
            connection.executemany(
                """
                INSERT OR IGNORE INTO account
                    (username, password, balance, email, status)
                VALUES (?, ?, ?, ?, ?)
                """,
                SEED_ACCOUNTS,
            )


def check_user(username, db_path=DEFAULT_DB_PATH):
    """检查用户是否存在且账户状态正常。"""
    if not username:
        return False
    with closing(connect_database(db_path)) as connection:
        row = connection.execute(
            "SELECT 1 FROM account WHERE username = ? AND status = 1",
            (username,),
        ).fetchone()
    return row is not None


def check_password(username, password, db_path=DEFAULT_DB_PATH):
    """校验指定用户的登录密码。"""
    with closing(connect_database(db_path)) as connection:
        row = connection.execute(
            """
            SELECT 1
            FROM account
            WHERE username = ? AND password = ? AND status = 1
            """,
            (username, password),
        ).fetchone()
    return row is not None


def get_balance(username, db_path=DEFAULT_DB_PATH, record_flow=True):
    """查询指定用户的账户余额，并按需记录余额查询流水。"""
    with closing(connect_database(db_path)) as connection:
        with connection:
            row = _account_row(connection, username)
            if row is not None and record_flow:
                _insert_flow(
                    connection,
                    username,
                    "BALANCE_QUERY",
                    0,
                    _decimal_money(row["balance"]),
                    "查询余额",
                )
    if row is None:
        return None
    return _float_money(row["balance"])


def withdraw_money(username, amount, db_path=DEFAULT_DB_PATH):
    """完成取款操作：扣减余额并记录交易流水。"""
    parsed_amount = _parse_positive_money(amount)
    if parsed_amount is None:
        return _result(False, 403, "Invalid amount")

    with closing(connect_database(db_path)) as connection:
        with connection:
            row = _account_row(connection, username)
            if row is None:
                return _result(False, 401, "User not found")

            current_balance = _decimal_money(row["balance"])
            if current_balance < parsed_amount:
                return _result(False, 402, "Insufficient balance", current_balance)

            balance_after = current_balance - parsed_amount
            _update_balance(connection, username, balance_after)
            _insert_flow(
                connection,
                username,
                "WITHDRAW",
                parsed_amount,
                balance_after,
                "取款成功",
            )

    return _result(True, 202, "Withdraw success", balance_after)


def deposit_money(username, amount, db_path=DEFAULT_DB_PATH):
    """完成存款操作：增加余额并记录交易流水。"""
    parsed_amount = _parse_positive_money(amount)
    if parsed_amount is None:
        return _result(False, 403, "Invalid amount")

    with closing(connect_database(db_path)) as connection:
        with connection:
            row = _account_row(connection, username)
            if row is None:
                return _result(False, 401, "User not found")

            balance_after = _decimal_money(row["balance"]) + parsed_amount
            _update_balance(connection, username, balance_after)
            _insert_flow(
                connection,
                username,
                "DEPOSIT",
                parsed_amount,
                balance_after,
                "存款成功",
            )

    return _result(True, 203, "Deposit success", balance_after)


def add_flow(
    username,
    transaction_type,
    amount,
    balance_after,
    db_path=DEFAULT_DB_PATH,
    remark="",
):
    """新增一条交易流水记录。"""
    with closing(connect_database(db_path)) as connection:
        with connection:
            cursor = _insert_flow(
                connection,
                username,
                transaction_type,
                None if amount is None else _decimal_money(amount),
                None if balance_after is None else _decimal_money(balance_after),
                remark,
            )
            return cursor.lastrowid


def get_flow(username, db_path=DEFAULT_DB_PATH, record_flow=True):
    """查询指定用户的交易流水，按需记录流水查询操作。"""
    with closing(connect_database(db_path)) as connection:
        with connection:
            row = _account_row(connection, username)
            if row is not None and record_flow:
                _insert_flow(
                    connection,
                    username,
                    "FLOW_QUERY",
                    0,
                    _decimal_money(row["balance"]),
                    "查询流水",
                )
        rows = connection.execute(
            """
            SELECT id, username, type, amount, balance_after, create_time, remark
            FROM transaction_flow
            WHERE username = ?
            ORDER BY id ASC
            """,
            (username,),
        ).fetchall()
    return [_flow_to_dict(row) for row in rows]


def get_email(username, db_path=DEFAULT_DB_PATH):
    """查询指定用户的邮箱地址。"""
    with closing(connect_database(db_path)) as connection:
        row = connection.execute(
            "SELECT email FROM account WHERE username = ? AND status = 1",
            (username,),
        ).fetchone()
    if row is None:
        return None
    return row["email"]


def _account_row(connection, username):
    return connection.execute(
        """
        SELECT username, password, balance, email, status
        FROM account
        WHERE username = ? AND status = 1
        """,
        (username,),
    ).fetchone()


def _update_balance(connection, username, balance):
    connection.execute(
        "UPDATE account SET balance = ? WHERE username = ?",
        (_float_money(balance), username),
    )


def _insert_flow(connection, username, transaction_type, amount, balance_after, remark):
    return connection.execute(
        """
        INSERT INTO transaction_flow
            (username, type, amount, balance_after, create_time, remark)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            username,
            transaction_type,
            None if amount is None else _float_money(amount),
            None if balance_after is None else _float_money(balance_after),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            remark,
        ),
    )


def _parse_positive_money(amount):
    try:
        money = _decimal_money(amount)
    except (InvalidOperation, ValueError, TypeError):
        return None
    if money <= 0:
        return None
    return money


def _decimal_money(value):
    if isinstance(value, bool):
        raise ValueError("amount must be a number")
    return Decimal(str(value).strip()).quantize(MONEY_QUANT, ROUND_HALF_UP)


def _float_money(value):
    if value is None:
        return None
    return float(_decimal_money(value))


def _flow_to_dict(row):
    return {
        "id": row["id"],
        "username": row["username"],
        "type": row["type"],
        "amount": _float_money(row["amount"]),
        "balance_after": _float_money(row["balance_after"]),
        "create_time": row["create_time"],
        "remark": row["remark"],
    }


def _result(success, status_code, message, balance=None):
    return {
        "success": success,
        "status_code": status_code,
        "message": message,
        "balance": None if balance is None else _float_money(balance),
    }
