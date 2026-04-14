"""Oracle DB connection pool management."""

from __future__ import annotations

from contextlib import contextmanager
import threading
from typing import Generator

import oracledb

from config import get_settings

_pool: oracledb.ConnectionPool | None = None
_pool_lock = threading.Lock()


def init_pool() -> oracledb.ConnectionPool:
    """
    Initialize a singleton Oracle connection pool.

    Returns:
        oracledb.ConnectionPool: Active pool instance.
    """
    global _pool

    if _pool is not None:
        return _pool

    with _pool_lock:
        if _pool is not None:
            return _pool

        settings = get_settings()
        if not settings.oracle_user or not settings.oracle_password:
            raise RuntimeError(
                "Oracle credentials are missing. Set ORACLE_USER and ORACLE_PASSWORD."
            )

        _pool = oracledb.create_pool(
            user=settings.oracle_user,
            password=settings.oracle_password,
            dsn=settings.dsn,
            min=settings.oracle_pool_min,
            max=settings.oracle_pool_max,
            increment=settings.oracle_pool_increment,
            getmode=oracledb.POOL_GETMODE_WAIT,
        )
        return _pool


def get_pool() -> oracledb.ConnectionPool:
    """Return initialized Oracle connection pool."""
    return init_pool()


@contextmanager
def get_connection() -> Generator[oracledb.Connection, None, None]:
    """
    Yield a pooled Oracle connection and ensure release.

    Yields:
        oracledb.Connection: Pooled DB connection.
    """
    pool = get_pool()
    connection = pool.acquire()
    try:
        yield connection
    finally:
        pool.release(connection)


def close_pool() -> None:
    """Close Oracle connection pool."""
    global _pool

    if _pool is not None:
        _pool.close()
        _pool = None
