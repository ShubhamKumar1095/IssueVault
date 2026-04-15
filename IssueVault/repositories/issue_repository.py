"""Issue persistence operations."""

from __future__ import annotations

from typing import Any

from models.schemas import IssueSearchFilters, IssueSubmissionInput
from repositories.base_repository import BaseRepository


class IssueRepository(BaseRepository):
    """Repository for issues, status history, links, and metadata lookup."""

    def list_categories(self) -> list[dict[str, Any]]:
        """Return active issue categories."""
        query = """
            SELECT category_id, category_name, description
            FROM issue_categories
            WHERE is_active = 'Y'
            ORDER BY category_name
        """
        return self.fetch_all(query)

    def create_category(self, category_name: str, description: str | None = None) -> int:
        """Create issue category and return generated id."""
        query = """
            INSERT INTO issue_categories (category_name, description, is_active)
            VALUES (:category_name, :description, 'Y')
        """
        return self.execute_returning_id(
            query,
            {"category_name": category_name, "description": description},
        )

    def list_releases(self) -> list[dict[str, Any]]:
        """Return known releases."""
        query = """
            SELECT release_id, release_name, release_date, notes
            FROM releases
            ORDER BY release_date DESC, release_name
        """
        return self.fetch_all(query)

    def list_tags(self) -> list[dict[str, Any]]:
        """Return issue tags."""
        query = "SELECT tag_id, tag_name FROM issue_tags ORDER BY tag_name"
        return self.fetch_all(query)

    def get_or_create_tag(self, tag_name: str) -> int:
        """Fetch tag id or create one."""
        existing = self.fetch_one(
            "SELECT tag_id FROM issue_tags WHERE tag_name = :tag_name COLLATE NOCASE",
            {"tag_name": tag_name},
        )
        if existing:
            return int(existing["tag_id"])

        return self.execute_returning_id(
            """
            INSERT INTO issue_tags (tag_name)
            VALUES (:tag_name)
            """,
            {"tag_name": tag_name.lower().strip()},
        )

    def add_issue_tag(self, issue_id: int, tag_id: int, created_by: int) -> int:
        """Attach a tag to an issue."""
        query = """
            INSERT OR IGNORE INTO issue_tag_map (issue_id, tag_id, created_by)
            VALUES (:issue_id, :tag_id, :created_by)
        """
        return self.execute(
            query,
            {"issue_id": issue_id, "tag_id": tag_id, "created_by": created_by},
        )

    def create_issue(self, payload: IssueSubmissionInput, reported_by: int) -> int:
        """Insert issue and return generated issue id."""
        query = """
            INSERT INTO issues (
                title,
                description,
                module_name,
                environment,
                severity,
                priority,
                status,
                category_id,
                error_code,
                steps_to_reproduce,
                expected_result,
                actual_result,
                business_impact,
                reported_by,
                assigned_to,
                release_id
            ) VALUES (
                :title,
                :description,
                :module_name,
                :environment,
                :severity,
                :priority,
                'New',
                :category_id,
                :error_code,
                :steps_to_reproduce,
                :expected_result,
                :actual_result,
                :business_impact,
                :reported_by,
                :assigned_to,
                :release_id
            )
        """
        return self.execute_returning_id(
            query,
            {
                "title": payload.title,
                "description": payload.description,
                "module_name": payload.module_name,
                "environment": payload.environment,
                "severity": payload.severity,
                "priority": payload.priority,
                "category_id": payload.category_id,
                "error_code": payload.error_code,
                "steps_to_reproduce": payload.steps_to_reproduce,
                "expected_result": payload.expected_result,
                "actual_result": payload.actual_result,
                "business_impact": payload.business_impact,
                "reported_by": reported_by,
                "assigned_to": payload.assigned_to,
                "release_id": payload.release_id,
            },
        )

    def add_status_history(
        self,
        issue_id: int,
        old_status: str | None,
        new_status: str,
        changed_by: int,
        notes: str | None = None,
    ) -> int:
        """Write one issue status transition history record."""
        query = """
            INSERT INTO issue_status_history (
                issue_id,
                old_status,
                new_status,
                changed_by,
                notes
            ) VALUES (
                :issue_id,
                :old_status,
                :new_status,
                :changed_by,
                :notes
            )
        """
        return self.execute(
            query,
            {
                "issue_id": issue_id,
                "old_status": old_status,
                "new_status": new_status,
                "changed_by": changed_by,
                "notes": notes,
            },
        )

    def get_issue_status(self, issue_id: int) -> str | None:
        """Get current issue status."""
        row = self.fetch_one("SELECT status FROM issues WHERE issue_id = :issue_id", {"issue_id": issue_id})
        return None if row is None else str(row["status"])

    def update_issue_status(self, issue_id: int, new_status: str) -> int:
        """Update issue status only."""
        query = """
            UPDATE issues
            SET status = :new_status, updated_at = CURRENT_TIMESTAMP
            WHERE issue_id = :issue_id
        """
        return self.execute(query, {"issue_id": issue_id, "new_status": new_status})

    def assign_issue(self, issue_id: int, assigned_to: int | None) -> int:
        """Assign or unassign an issue."""
        query = """
            UPDATE issues
            SET assigned_to = :assigned_to, updated_at = CURRENT_TIMESTAMP
            WHERE issue_id = :issue_id
        """
        return self.execute(query, {"issue_id": issue_id, "assigned_to": assigned_to})

    def get_issue_by_id(self, issue_id: int) -> dict[str, Any] | None:
        """Fetch issue details with names for related entities."""
        query = """
            SELECT
                i.issue_id,
                i.title,
                i.description,
                i.module_name,
                i.environment,
                i.severity,
                i.priority,
                i.status,
                i.error_code,
                i.steps_to_reproduce,
                i.expected_result,
                i.actual_result,
                i.business_impact,
                i.reported_by,
                i.assigned_to,
                i.release_id,
                i.category_id,
                i.created_at,
                i.updated_at,
                ic.category_name,
                ru.username AS reported_by_username,
                ru.full_name AS reported_by_name,
                au.username AS assigned_to_username,
                au.full_name AS assigned_to_name,
                r.release_name
            FROM issues i
            JOIN issue_categories ic ON ic.category_id = i.category_id
            JOIN users ru ON ru.user_id = i.reported_by
            LEFT JOIN users au ON au.user_id = i.assigned_to
            LEFT JOIN releases r ON r.release_id = i.release_id
            WHERE i.issue_id = :issue_id
        """
        return self.fetch_one(query, {"issue_id": issue_id})

    def list_issue_status_history(self, issue_id: int) -> list[dict[str, Any]]:
        """Fetch status transitions in chronological order."""
        query = """
            SELECT
                ish.history_id,
                ish.issue_id,
                ish.old_status,
                ish.new_status,
                ish.changed_at,
                ish.notes,
                u.user_id AS changed_by,
                u.full_name AS changed_by_name
            FROM issue_status_history ish
            JOIN users u ON u.user_id = ish.changed_by
            WHERE ish.issue_id = :issue_id
            ORDER BY ish.changed_at ASC
        """
        return self.fetch_all(query, {"issue_id": issue_id})

    def search_issues(self, filters: IssueSearchFilters) -> list[dict[str, Any]]:
        """Search issues using multiple optional filters."""
        query = """
            SELECT
                i.issue_id,
                i.title,
                i.module_name,
                i.environment,
                i.severity,
                i.priority,
                i.status,
                i.error_code,
                i.created_at,
                i.updated_at,
                ic.category_name,
                ru.full_name AS reported_by_name,
                au.full_name AS assigned_to_name
            FROM issues i
            JOIN issue_categories ic ON ic.category_id = i.category_id
            JOIN users ru ON ru.user_id = i.reported_by
            LEFT JOIN users au ON au.user_id = i.assigned_to
            WHERE 1 = 1
        """
        params: dict[str, Any] = {}

        if filters.keyword:
            query += " AND (i.title LIKE :keyword COLLATE NOCASE OR i.description LIKE :keyword COLLATE NOCASE)"
            params["keyword"] = f"%{filters.keyword}%"
        if filters.title:
            query += " AND i.title LIKE :title COLLATE NOCASE"
            params["title"] = f"%{filters.title}%"
        if filters.error_code:
            query += " AND i.error_code = :error_code COLLATE NOCASE"
            params["error_code"] = filters.error_code
        if filters.module_name:
            query += " AND i.module_name = :module_name COLLATE NOCASE"
            params["module_name"] = filters.module_name
        if filters.severity:
            query += " AND i.severity = :severity"
            params["severity"] = filters.severity
        if filters.status:
            query += " AND i.status = :status"
            params["status"] = filters.status
        if filters.category_id:
            query += " AND i.category_id = :category_id"
            params["category_id"] = filters.category_id
        if filters.assigned_to:
            query += " AND i.assigned_to = :assigned_to"
            params["assigned_to"] = filters.assigned_to
        if filters.reported_by:
            query += " AND i.reported_by = :reported_by"
            params["reported_by"] = filters.reported_by
        if filters.created_from:
            query += " AND date(i.created_at) >= date(:created_from)"
            params["created_from"] = filters.created_from.isoformat()
        if filters.created_to:
            query += " AND date(i.created_at) <= date(:created_to)"
            params["created_to"] = filters.created_to.isoformat()

        query += " ORDER BY i.created_at DESC LIMIT 500"
        return self.fetch_all(query, params)

    def create_issue_link(
        self,
        issue_id: int,
        linked_issue_id: int,
        link_type: str,
        created_by: int,
    ) -> int:
        """Insert link relationship between two issues."""
        query = """
            INSERT INTO linked_issues (issue_id, linked_issue_id, link_type, created_by)
            VALUES (:issue_id, :linked_issue_id, :link_type, :created_by)
        """
        return self.execute(
            query,
            {
                "issue_id": issue_id,
                "linked_issue_id": linked_issue_id,
                "link_type": link_type,
                "created_by": created_by,
            },
        )

    def list_linked_issues(self, issue_id: int) -> list[dict[str, Any]]:
        """Return issue links for one issue."""
        query = """
            SELECT
                li.link_id,
                li.link_type,
                li.created_at,
                li.linked_issue_id,
                i.title AS linked_issue_title,
                i.status AS linked_issue_status
            FROM linked_issues li
            JOIN issues i ON i.issue_id = li.linked_issue_id
            WHERE li.issue_id = :issue_id
            ORDER BY li.created_at DESC
        """
        return self.fetch_all(query, {"issue_id": issue_id})

    def list_similarity_candidates(self, max_rows: int = 500) -> list[dict[str, Any]]:
        """
        Return issue records used by similarity ranking.

        Includes average rating and helpfulness ratio for ranking boost.
        """
        query = """
            SELECT
                i.issue_id,
                i.title,
                i.description,
                i.module_name,
                i.error_code,
                i.status,
                ic.category_name,
                COALESCE(AVG(sf.rating), 0) AS avg_rating,
                COALESCE(
                    (1.0 * SUM(CASE WHEN sf.is_helpful = 'Y' THEN 1 ELSE 0 END))
                    / NULLIF(COUNT(sf.feedback_id), 0),
                    0
                ) AS helpful_ratio
            FROM issues i
            JOIN issue_categories ic ON ic.category_id = i.category_id
            LEFT JOIN solution_feedback sf ON sf.issue_id = i.issue_id
            GROUP BY
                i.issue_id,
                i.title,
                i.description,
                i.module_name,
                i.error_code,
                i.status,
                ic.category_name,
                i.created_at
            ORDER BY i.created_at DESC
            LIMIT :max_rows
        """
        return self.fetch_all(query, {"max_rows": max_rows})

    def list_issue_tags(self, issue_id: int) -> list[dict[str, Any]]:
        """Get tags attached to issue."""
        query = """
            SELECT t.tag_id, t.tag_name
            FROM issue_tag_map itm
            JOIN issue_tags t ON t.tag_id = itm.tag_id
            WHERE itm.issue_id = :issue_id
            ORDER BY t.tag_name
        """
        return self.fetch_all(query, {"issue_id": issue_id})
