"""Issue search and filter business logic."""

from __future__ import annotations

from models.enums import RoleEnum
from models.schemas import IssueSearchFilters
from repositories.issue_repository import IssueRepository
from utils.exceptions import ValidationError
from utils.validators import validate_search_filters


class SearchService:
    """Service for role-aware issue search."""

    def __init__(self) -> None:
        self.issue_repo = IssueRepository()

    def search_issues(self, filters: IssueSearchFilters, user: dict[str, object]) -> list[dict[str, object]]:
        """Execute filtered issue search with role-based scope restrictions."""
        errors = validate_search_filters(filters)
        if errors:
            raise ValidationError("; ".join(errors))

        role_name = str(user.get("role_name"))
        user_id = int(user.get("user_id", 0))

        scoped_filters = IssueSearchFilters(**filters.__dict__)
        if role_name == RoleEnum.END_USER.value:
            scoped_filters.reported_by = user_id

        return self.issue_repo.search_issues(scoped_filters)

    def list_my_issues(self, user: dict[str, object]) -> list[dict[str, object]]:
        """Return issues relevant to current user."""
        role_name = str(user.get("role_name"))
        user_id = int(user.get("user_id", 0))

        filters = IssueSearchFilters()
        if role_name == RoleEnum.END_USER.value:
            filters.reported_by = user_id
        elif role_name in {RoleEnum.SUPPORT_ANALYST.value, RoleEnum.CONSULTANT.value}:
            filters.assigned_to = user_id

        return self.issue_repo.search_issues(filters)
