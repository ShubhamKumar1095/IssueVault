"""User and role related DB operations."""

from __future__ import annotations

from typing import Any

from repositories.base_repository import BaseRepository


class UserRepository(BaseRepository):
    """Repository for users, roles, and teams."""

    def get_user_by_username(self, username: str) -> dict[str, Any] | None:
        """Fetch one active user by username."""
        query = """
            SELECT
                u.user_id,
                u.username,
                u.full_name,
                u.email,
                u.password_hash,
                u.is_active,
                u.last_login_at,
                u.role_id,
                u.team_id,
                r.role_name,
                t.team_name
            FROM users u
            JOIN roles r ON r.role_id = u.role_id
            LEFT JOIN teams t ON t.team_id = u.team_id
            WHERE LOWER(u.username) = LOWER(:username)
        """
        return self.fetch_one(query, {"username": username})

    def get_user_by_id(self, user_id: int) -> dict[str, Any] | None:
        """Fetch one user by id."""
        query = """
            SELECT
                u.user_id,
                u.username,
                u.full_name,
                u.email,
                u.password_hash,
                u.is_active,
                u.last_login_at,
                u.role_id,
                u.team_id,
                r.role_name,
                t.team_name
            FROM users u
            JOIN roles r ON r.role_id = u.role_id
            LEFT JOIN teams t ON t.team_id = u.team_id
            WHERE u.user_id = :user_id
        """
        return self.fetch_one(query, {"user_id": user_id})

    def list_users(self, role_name: str | None = None, team_id: int | None = None) -> list[dict[str, Any]]:
        """List users with optional role/team filters."""
        query = """
            SELECT
                u.user_id,
                u.username,
                u.full_name,
                u.email,
                u.is_active,
                u.created_at,
                r.role_name,
                t.team_name
            FROM users u
            JOIN roles r ON r.role_id = u.role_id
            LEFT JOIN teams t ON t.team_id = u.team_id
            WHERE 1 = 1
        """
        params: dict[str, Any] = {}
        if role_name:
            query += " AND r.role_name = :role_name"
            params["role_name"] = role_name
        if team_id:
            query += " AND u.team_id = :team_id"
            params["team_id"] = team_id
        query += " ORDER BY u.created_at DESC"
        return self.fetch_all(query, params)

    def create_user(
        self,
        username: str,
        full_name: str,
        email: str,
        password_hash: str,
        role_id: int,
        team_id: int | None,
        is_active: str = "Y",
    ) -> int:
        """Create a user and return generated user id."""
        query = """
            INSERT INTO users (
                username,
                full_name,
                email,
                password_hash,
                role_id,
                team_id,
                is_active
            ) VALUES (
                :username,
                :full_name,
                :email,
                :password_hash,
                :role_id,
                :team_id,
                :is_active
            )
            RETURNING user_id INTO :out_id
        """
        return self.execute_returning_id(
            query,
            {
                "username": username,
                "full_name": full_name,
                "email": email,
                "password_hash": password_hash,
                "role_id": role_id,
                "team_id": team_id,
                "is_active": is_active,
            },
        )

    def update_last_login(self, user_id: int) -> int:
        """Set user's last_login_at timestamp."""
        query = "UPDATE users SET last_login_at = SYSTIMESTAMP WHERE user_id = :user_id"
        return self.execute(query, {"user_id": user_id})

    def list_roles(self) -> list[dict[str, Any]]:
        """List available roles."""
        query = "SELECT role_id, role_name, description FROM roles ORDER BY role_name"
        return self.fetch_all(query)

    def list_teams(self) -> list[dict[str, Any]]:
        """List available teams."""
        query = "SELECT team_id, team_name, description FROM teams ORDER BY team_name"
        return self.fetch_all(query)
