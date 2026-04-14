"""Resolution memory business logic."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from models.schemas import ResolutionInput
from repositories.issue_repository import IssueRepository
from repositories.resolution_repository import ResolutionRepository
from services.auth_service import AuthService
from utils.exceptions import AuthorizationError, NotFoundError, ValidationError
from utils.validators import validate_resolution_input


class ResolutionService:
    """Service for storing and retrieving issue resolutions."""

    def __init__(self) -> None:
        self.issue_repo = IssueRepository()
        self.resolution_repo = ResolutionRepository()
        self.auth_service = AuthService()

    def upsert_resolution(
        self,
        payload: ResolutionInput,
        actor_user: dict[str, Any],
        status_note: str | None = None,
    ) -> int:
        """Create or update issue resolution and move issue to Resolved."""
        errors = validate_resolution_input(payload)
        if errors:
            raise ValidationError("; ".join(errors))

        issue = self.issue_repo.get_issue_by_id(payload.issue_id)
        if not issue:
            raise NotFoundError("Issue not found.")

        if not self.auth_service.can_update_issue(actor_user, issue):
            raise AuthorizationError("You do not have permission to resolve this issue.")

        if payload.resolved_at is None:
            payload.resolved_at = datetime.now()

        resolution_id = self.resolution_repo.upsert_resolution(payload)

        old_status = str(issue["status"])
        if old_status != "Resolved":
            self.issue_repo.update_issue_status(payload.issue_id, "Resolved")
            self.issue_repo.add_status_history(
                issue_id=payload.issue_id,
                old_status=old_status,
                new_status="Resolved",
                changed_by=int(actor_user["user_id"]),
                notes=status_note or "Resolution details saved.",
            )

        return resolution_id

    def add_solution_feedback(
        self,
        issue_id: int,
        user_id: int,
        rating: float,
        is_helpful: bool,
        comments: str | None,
    ) -> int:
        """Capture feedback for resolved issue memory."""
        if rating < 1 or rating > 5:
            raise ValidationError("Rating must be between 1 and 5.")

        resolution = self.resolution_repo.get_resolution_by_issue_id(issue_id)
        if not resolution:
            raise NotFoundError("Resolution not found for this issue.")

        return self.resolution_repo.add_solution_feedback(
            issue_id=issue_id,
            resolution_id=int(resolution["resolution_id"]),
            user_id=user_id,
            rating=rating,
            is_helpful=is_helpful,
            comments=comments,
        )

    def get_resolution_bundle(self, issue_id: int) -> dict[str, Any]:
        """Return resolution with feedback list."""
        resolution = self.resolution_repo.get_resolution_by_issue_id(issue_id)
        if not resolution:
            return {"resolution": None, "feedback": []}
        feedback = self.resolution_repo.list_solution_feedback(issue_id)
        return {"resolution": resolution, "feedback": feedback}
