"""Attachment metadata DB operations."""

from __future__ import annotations

from models.schemas import AttachmentInput
from repositories.base_repository import BaseRepository


class AttachmentRepository(BaseRepository):
    """Repository for issue attachment metadata."""

    def add_attachment(self, payload: AttachmentInput) -> int:
        """Insert attachment metadata and return generated id."""
        query = """
            INSERT INTO attachments (
                issue_id,
                original_filename,
                stored_filename,
                file_path,
                file_size_bytes,
                content_type,
                uploaded_by
            ) VALUES (
                :issue_id,
                :original_filename,
                :stored_filename,
                :file_path,
                :file_size_bytes,
                :content_type,
                :uploaded_by
            )
        """
        return self.execute_returning_id(
            query,
            {
                "issue_id": payload.issue_id,
                "original_filename": payload.original_filename,
                "stored_filename": payload.stored_filename,
                "file_path": payload.file_path,
                "file_size_bytes": payload.file_size_bytes,
                "content_type": payload.content_type,
                "uploaded_by": payload.uploaded_by,
            },
        )

    def list_attachments(self, issue_id: int) -> list[dict[str, object]]:
        """Return attachment metadata for one issue."""
        query = """
            SELECT
                a.attachment_id,
                a.issue_id,
                a.original_filename,
                a.stored_filename,
                a.file_path,
                a.file_size_bytes,
                a.content_type,
                a.uploaded_at,
                u.full_name AS uploaded_by_name
            FROM attachments a
            JOIN users u ON u.user_id = a.uploaded_by
            WHERE a.issue_id = :issue_id
            ORDER BY a.uploaded_at DESC
        """
        return self.fetch_all(query, {"issue_id": issue_id})
