"""Issue comments DB operations."""

from __future__ import annotations

from repositories.base_repository import BaseRepository


class CommentRepository(BaseRepository):
    """Repository for issue comments."""

    def add_comment(self, issue_id: int, commented_by: int, comment_text: str, is_internal: bool = False) -> int:
        """Insert one comment row."""
        query = """
            INSERT INTO comments (
                issue_id,
                commented_by,
                comment_text,
                is_internal
            ) VALUES (
                :issue_id,
                :commented_by,
                :comment_text,
                :is_internal
            )
        """
        return self.execute(
            query,
            {
                "issue_id": issue_id,
                "commented_by": commented_by,
                "comment_text": comment_text,
                "is_internal": "Y" if is_internal else "N",
            },
        )

    def list_comments(self, issue_id: int, include_internal: bool = True) -> list[dict[str, object]]:
        """Fetch issue comments ordered by latest first."""
        query = """
            SELECT
                c.comment_id,
                c.issue_id,
                c.comment_text,
                c.is_internal,
                c.created_at,
                u.user_id AS commented_by,
                u.full_name AS commented_by_name
            FROM comments c
            JOIN users u ON u.user_id = c.commented_by
            WHERE c.issue_id = :issue_id
        """
        params: dict[str, object] = {"issue_id": issue_id}
        if not include_internal:
            query += " AND c.is_internal = 'N'"
        query += " ORDER BY c.created_at DESC"
        return self.fetch_all(query, params)
