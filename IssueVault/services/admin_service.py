"""Admin and configuration management service."""

from __future__ import annotations

from typing import Any

from repositories.issue_repository import IssueRepository
from repositories.user_repository import UserRepository
from utils.exceptions import ValidationError
from utils.security import hash_password


class AdminService:
    """Service for managing users and categories in MVP."""

    def __init__(self) -> None:
        self.user_repo = UserRepository()
        self.issue_repo = IssueRepository()

    def get_admin_reference_data(self) -> dict[str, list[dict[str, Any]]]:
        """Return users, roles, teams, and categories."""
        return {
            "users": self.user_repo.list_users(),
            "roles": self.user_repo.list_roles(),
            "teams": self.user_repo.list_teams(),
            "categories": self.issue_repo.list_categories(),
        }

    def create_user(
        self,
        username: str,
        full_name: str,
        email: str,
        password: str,
        role_name: str,
        team_id: int | None,
    ) -> int:
        """Create a user record."""
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters.")

        role_lookup = {row["role_name"]: int(row["role_id"]) for row in self.user_repo.list_roles()}
        if role_name not in role_lookup:
            raise ValidationError("Invalid role selected.")

        return self.user_repo.create_user(
            username=username.strip(),
            full_name=full_name.strip(),
            email=email.strip().lower(),
            password_hash=hash_password(password),
            role_id=role_lookup[role_name],
            team_id=team_id,
        )

    def create_category(self, category_name: str, description: str | None) -> int:
        """Create active issue category."""
        name = category_name.strip()
        if len(name) < 3:
            raise ValidationError("Category name must be at least 3 characters.")
        return self.issue_repo.create_category(name, description.strip() if description else None)
