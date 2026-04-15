"""Base repository helpers for SQLite query execution."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

import sqlite3

from db.sqlite_db import get_connection


class BaseRepository:
    """Common DB helper methods shared by repository classes."""

    @staticmethod
    def _rows_to_dicts(cursor: sqlite3.Cursor, rows: list[tuple[Any, ...]]) -> list[dict[str, Any]]:
        """Convert raw DB rows into dictionary records."""
        columns = [col[0].lower() for col in cursor.description or []]
        return [dict(zip(columns, row)) for row in rows]

    @staticmethod
    def _normalize_params(params: dict[str, Any] | None) -> dict[str, Any]:
        """Normalize bind params for sqlite execution."""
        normalized: dict[str, Any] = {}
        for key, value in (params or {}).items():
            if isinstance(value, datetime):
                normalized[key] = value.isoformat(sep=" ", timespec="seconds")
            elif isinstance(value, date):
                normalized[key] = value.isoformat()
            else:
                normalized[key] = value
        return normalized

    def fetch_all(self, query: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Execute select query and return all rows as dictionaries."""
        bind_params = self._normalize_params(params)
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(query, bind_params)
            rows = cursor.fetchall()
            return self._rows_to_dicts(cursor, rows)

    def fetch_one(self, query: str, params: dict[str, Any] | None = None) -> dict[str, Any] | None:
        """Execute select query and return one row as dictionary."""
        bind_params = self._normalize_params(params)
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(query, bind_params)
            row = cursor.fetchone()
            if row is None:
                return None
            rows = self._rows_to_dicts(cursor, [row])
            return rows[0]

    def execute(self, query: str, params: dict[str, Any] | None = None) -> int:
        """
        Execute DML and commit.

        Returns:
            int: Cursor rowcount.
        """
        bind_params = self._normalize_params(params)
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(query, bind_params)
            connection.commit()
            return cursor.rowcount

    def execute_returning_id(
        self,
        query: str,
        params: dict[str, Any] | None = None,
        out_param: str = "out_id",
    ) -> int:
        """
        Execute insert and return generated id.

        Note:
            `out_param` is retained only for compatibility with older code paths.
        """
        bind_params = self._normalize_params(params)
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(query, bind_params)
            connection.commit()
            return int(cursor.lastrowid)
