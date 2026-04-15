"""SQLite connection and bootstrap helpers for ResolveHub."""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
import sqlite3
import threading
from typing import Generator

from config import get_settings

_init_lock = threading.Lock()
_initialized = False
_local = threading.local()


def _db_path() -> Path:
    """Return resolved SQLite database file path."""
    settings = get_settings()
    db_path = Path(settings.sqlite_db_path).expanduser()
    if not db_path.is_absolute():
        db_path = Path.cwd() / db_path
    return db_path


def _apply_pragmas(connection: sqlite3.Connection) -> None:
    """Apply performance and consistency pragmas."""
    settings = get_settings()
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA journal_mode = WAL")
    connection.execute("PRAGMA synchronous = NORMAL")
    connection.execute("PRAGMA temp_store = MEMORY")
    connection.execute("PRAGMA cache_size = -64000")
    connection.execute(f"PRAGMA busy_timeout = {settings.sqlite_busy_timeout_ms}")


def _table_exists(connection: sqlite3.Connection, table_name: str) -> bool:
    row = connection.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=:table_name",
        {"table_name": table_name},
    ).fetchone()
    return row is not None


def _bootstrap_database(connection: sqlite3.Connection) -> None:
    """Create schema and seed data when DB is first initialized."""
    if _table_exists(connection, "issues"):
        return

    project_root = Path(__file__).resolve().parents[1]
    schema_path = project_root / "sql" / "schema.sql"
    seed_path = project_root / "sql" / "seed_data.sql"

    if not schema_path.exists():
        raise RuntimeError(f"Schema file not found: {schema_path}")
    if not seed_path.exists():
        raise RuntimeError(f"Seed file not found: {seed_path}")

    schema_sql = schema_path.read_text(encoding="utf-8")
    seed_sql = seed_path.read_text(encoding="utf-8")

    connection.executescript(schema_sql)
    connection.executescript(seed_sql)
    connection.commit()


def initialize_database() -> None:
    """Initialize SQLite DB file, schema, and default seed data once."""
    global _initialized
    if _initialized:
        return

    with _init_lock:
        if _initialized:
            return

        db_path = _db_path()
        db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(db_path, timeout=30) as connection:
            _apply_pragmas(connection)
            _bootstrap_database(connection)
        _initialized = True


def get_sqlite_connection() -> sqlite3.Connection:
    """Get a thread-local SQLite connection."""
    initialize_database()
    connection = getattr(_local, "connection", None)
    if connection is None:
        connection = sqlite3.connect(
            _db_path(),
            timeout=30,
            check_same_thread=False,
        )
        connection.row_factory = sqlite3.Row
        _apply_pragmas(connection)
        _local.connection = connection
    return connection


@contextmanager
def get_connection() -> Generator[sqlite3.Connection, None, None]:
    """Yield SQLite connection with rollback safety."""
    connection = get_sqlite_connection()
    try:
        yield connection
    except Exception:
        connection.rollback()
        raise
