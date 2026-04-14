"""Base repository helpers for Oracle query execution."""

from __future__ import annotations

from typing import Any

import oracledb

from db.oracle_pool import get_connection


class BaseRepository:
    """Common DB helper methods shared by repository classes."""

    @staticmethod
    def _rows_to_dicts(cursor: oracledb.Cursor, rows: list[tuple[Any, ...]]) -> list[dict[str, Any]]:
        """Convert raw DB rows into dictionary records."""
        columns = [col[0].lower() for col in cursor.description or []]
        return [dict(zip(columns, row)) for row in rows]

    def fetch_all(self, query: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Execute select query and return all rows as dictionaries."""
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, params or {})
                rows = cursor.fetchall()
                return self._rows_to_dicts(cursor, rows)

    def fetch_one(self, query: str, params: dict[str, Any] | None = None) -> dict[str, Any] | None:
        """Execute select query and return one row as dictionary."""
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, params or {})
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
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, params or {})
                connection.commit()
                return cursor.rowcount

    def execute_returning_id(
        self,
        query: str,
        params: dict[str, Any] | None = None,
        out_param: str = "out_id",
    ) -> int:
        """Execute insert with RETURNING INTO and return generated id."""
        with get_connection() as connection:
            with connection.cursor() as cursor:
                out_var = cursor.var(oracledb.DB_TYPE_NUMBER)
                bind_params = dict(params or {})
                bind_params[out_param] = out_var
                cursor.execute(query, bind_params)
                connection.commit()
                value = out_var.getvalue()
                if isinstance(value, list):
                    value = value[0]
                return int(value)
