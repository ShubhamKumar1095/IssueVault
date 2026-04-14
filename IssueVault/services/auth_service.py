"""Authentication and authorization service layer."""

from __future__ import annotations

from typing import Any

from models.enums import RoleEnum
from models.schemas import AuthUser
from repositories.user_repository import UserRepository
from utils.exceptions import AuthenticationError, AuthorizationError
from utils.security import verify_password


class AuthService:
    """Business logic for login and role-based access checks."""

    def __init__(self) -> None:
        self.user_repo = UserRepository()

    def authenticate(self, username: str, password: str) -> AuthUser:
        """Validate credentials and return authenticated user session payload."""
        user = self.user_repo.get_user_by_username(username)
        if not user:
            raise AuthenticationError("Invalid username or password.")

        if user["is_active"] != "Y":
            raise AuthenticationError("User is inactive. Contact admin.")

        if not verify_password(password, str(user["password_hash"])):
            raise AuthenticationError("Invalid username or password.")

        self.user_repo.update_last_login(int(user["user_id"]))
        return AuthUser(
            user_id=int(user["user_id"]),
            username=str(user["username"]),
            full_name=str(user["full_name"]),
            email=str(user["email"]),
            role_name=str(user["role_name"]),
            team_name=str(user["team_name"]) if user.get("team_name") else None,
        )

    def authorize(self, user: dict[str, Any], allowed_roles: set[str]) -> None:
        """Raise when user's role is not permitted."""
        if user.get("role_name") not in allowed_roles:
            raise AuthorizationError("You are not authorized for this action.")

    def can_view_issue(self, user: dict[str, Any], issue: dict[str, Any]) -> bool:
        """Check whether user can view issue details."""
        role = user.get("role_name")
        if role in {RoleEnum.ADMIN.value, RoleEnum.MANAGER.value, RoleEnum.CONSULTANT.value, RoleEnum.SUPPORT_ANALYST.value}:
            return True
        if role == RoleEnum.END_USER.value:
            return self._safe_int(issue.get("reported_by")) == self._safe_int(user.get("user_id"))
        return False

    def can_update_issue(self, user: dict[str, Any], issue: dict[str, Any]) -> bool:
        """Check whether user can update issue status/assignment."""
        role = user.get("role_name")
        if role in {RoleEnum.ADMIN.value, RoleEnum.CONSULTANT.value}:
            return True
        if role == RoleEnum.SUPPORT_ANALYST.value:
            return self._safe_int(issue.get("assigned_to")) == self._safe_int(user.get("user_id"))
        return False

    def can_submit_issue(self, user: dict[str, Any]) -> bool:
        """Check whether user can submit issue."""
        return user.get("role_name") in {
            RoleEnum.END_USER.value,
            RoleEnum.SUPPORT_ANALYST.value,
            RoleEnum.CONSULTANT.value,
            RoleEnum.ADMIN.value,
        }

    @staticmethod
    def _safe_int(value: Any) -> int:
        """Convert nullable values to int sentinel."""
        try:
            return int(value)
        except (TypeError, ValueError):
            return -1
