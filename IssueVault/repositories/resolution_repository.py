"""Resolution memory and feedback DB operations."""

from __future__ import annotations

from typing import Any

from models.schemas import ResolutionInput
from repositories.base_repository import BaseRepository


class ResolutionRepository(BaseRepository):
    """Repository for issue resolutions and solution feedback."""

    def get_resolution_by_issue_id(self, issue_id: int) -> dict[str, Any] | None:
        """Fetch one resolution by issue id."""
        query = """
            SELECT
                r.resolution_id,
                r.issue_id,
                r.root_cause,
                r.workaround,
                r.final_fix,
                r.resolution_steps,
                r.resolver_id,
                r.resolved_at,
                r.resolution_minutes,
                u.full_name AS resolver_name
            FROM resolutions r
            JOIN users u ON u.user_id = r.resolver_id
            WHERE r.issue_id = :issue_id
        """
        return self.fetch_one(query, {"issue_id": issue_id})

    def create_resolution(self, payload: ResolutionInput) -> int:
        """Insert resolution and return generated id."""
        query = """
            INSERT INTO resolutions (
                issue_id,
                root_cause,
                workaround,
                final_fix,
                resolution_steps,
                resolver_id,
                resolved_at,
                resolution_minutes
            ) VALUES (
                :issue_id,
                :root_cause,
                :workaround,
                :final_fix,
                :resolution_steps,
                :resolver_id,
                :resolved_at,
                :resolution_minutes
            )
        """
        return self.execute_returning_id(
            query,
            {
                "issue_id": payload.issue_id,
                "root_cause": payload.root_cause,
                "workaround": payload.workaround,
                "final_fix": payload.final_fix,
                "resolution_steps": payload.resolution_steps,
                "resolver_id": payload.resolver_id,
                "resolved_at": payload.resolved_at,
                "resolution_minutes": payload.resolution_minutes,
            },
        )

    def update_resolution(self, issue_id: int, payload: ResolutionInput) -> int:
        """Update existing resolution by issue id."""
        query = """
            UPDATE resolutions
            SET
                root_cause = :root_cause,
                workaround = :workaround,
                final_fix = :final_fix,
                resolution_steps = :resolution_steps,
                resolver_id = :resolver_id,
                resolved_at = :resolved_at,
                resolution_minutes = :resolution_minutes,
                updated_at = CURRENT_TIMESTAMP
            WHERE issue_id = :issue_id
        """
        return self.execute(
            query,
            {
                "issue_id": issue_id,
                "root_cause": payload.root_cause,
                "workaround": payload.workaround,
                "final_fix": payload.final_fix,
                "resolution_steps": payload.resolution_steps,
                "resolver_id": payload.resolver_id,
                "resolved_at": payload.resolved_at,
                "resolution_minutes": payload.resolution_minutes,
            },
        )

    def upsert_resolution(self, payload: ResolutionInput) -> int:
        """
        Upsert resolution by issue.

        Returns:
            int: Resolution id.
        """
        existing = self.get_resolution_by_issue_id(payload.issue_id)
        if existing:
            self.update_resolution(payload.issue_id, payload)
            return int(existing["resolution_id"])
        return self.create_resolution(payload)

    def add_solution_feedback(
        self,
        issue_id: int,
        resolution_id: int,
        user_id: int,
        rating: float,
        is_helpful: bool,
        comments: str | None,
    ) -> int:
        """Insert feedback for a resolution."""
        query = """
            INSERT INTO solution_feedback (
                issue_id,
                resolution_id,
                user_id,
                rating,
                is_helpful,
                comments
            ) VALUES (
                :issue_id,
                :resolution_id,
                :user_id,
                :rating,
                :is_helpful,
                :comments
            )
        """
        return self.execute(
            query,
            {
                "issue_id": issue_id,
                "resolution_id": resolution_id,
                "user_id": user_id,
                "rating": rating,
                "is_helpful": "Y" if is_helpful else "N",
                "comments": comments,
            },
        )

    def list_solution_feedback(self, issue_id: int) -> list[dict[str, Any]]:
        """Fetch feedback rows for issue resolution."""
        query = """
            SELECT
                sf.feedback_id,
                sf.issue_id,
                sf.resolution_id,
                sf.user_id,
                sf.rating,
                sf.is_helpful,
                sf.comments,
                sf.created_at,
                u.full_name AS user_name
            FROM solution_feedback sf
            JOIN users u ON u.user_id = sf.user_id
            WHERE sf.issue_id = :issue_id
            ORDER BY sf.created_at DESC
        """
        return self.fetch_all(query, {"issue_id": issue_id})
