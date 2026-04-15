"""Backward-compatible wrapper for legacy imports."""

from __future__ import annotations

from db.sqlite_db import get_connection, get_sqlite_connection, initialize_database

__all__ = ["get_connection", "get_sqlite_connection", "initialize_database"]
