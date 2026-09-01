import sqlite3
import os
from contextlib import contextmanager

_DEFAULT_DB = os.path.join(os.path.dirname(__file__), "..", "..", "data", "db", "sales.db")


def get_connection(db_path: str = _DEFAULT_DB) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


@contextmanager
def db_connection(db_path: str = _DEFAULT_DB):
    conn = get_connection(db_path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
