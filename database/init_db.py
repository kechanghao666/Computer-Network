try:
    from .account_service import init_database
    from .database import DEFAULT_DB_PATH
except ImportError:
    from account_service import init_database
    from database import DEFAULT_DB_PATH


if __name__ == "__main__":
    init_database(DEFAULT_DB_PATH)
    print(f"Database initialized: {DEFAULT_DB_PATH}")
