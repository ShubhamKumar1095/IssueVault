"""Analytics and dashboard DB queries."""

from __future__ import annotations

from repositories.base_repository import BaseRepository


class AnalyticsRepository(BaseRepository):
    """Repository for dashboard metrics and chart data."""

    def get_kpi_snapshot(self) -> dict[str, object]:
        """Return core KPI cards for dashboard header."""
        query = """
            SELECT
                (SELECT COUNT(*)
                 FROM issues
                 WHERE status NOT IN ('Resolved', 'Closed')) AS total_open_issues,

                (SELECT COUNT(*)
                 FROM issue_status_history
                 WHERE new_status = 'Resolved'
                   AND changed_at >= TRUNC(SYSDATE, 'IW')) AS resolved_this_week,

                (SELECT ROUND(AVG(resolution_minutes), 2)
                 FROM resolutions) AS avg_resolution_minutes,

                (
                    SELECT CASE
                           WHEN resolved_count = 0 THEN 0
                           ELSE ROUND((reopened_count / resolved_count) * 100, 2)
                           END
                    FROM (
                        SELECT
                            SUM(CASE WHEN new_status = 'Resolved' THEN 1 ELSE 0 END) AS resolved_count,
                            SUM(CASE WHEN new_status = 'Reopened' THEN 1 ELSE 0 END) AS reopened_count
                        FROM issue_status_history
                    )
                ) AS reopen_rate_pct,

                (SELECT COUNT(*)
                 FROM linked_issues
                 WHERE link_type = 'duplicate') AS duplicate_issues_avoided
            FROM dual
        """
        row = self.fetch_one(query)
        return row or {}

    def get_status_distribution(self) -> list[dict[str, object]]:
        """Return issue count by current status."""
        query = """
            SELECT status, COUNT(*) AS issue_count
            FROM issues
            GROUP BY status
            ORDER BY issue_count DESC, status
        """
        return self.fetch_all(query)

    def get_top_recurring_categories(self, top_n: int = 5) -> list[dict[str, object]]:
        """Return categories with highest recurrence and volume."""
        query = """
            SELECT *
            FROM (
                SELECT
                    ic.category_name,
                    COUNT(DISTINCT i.issue_id) AS issue_count,
                    COUNT(li.link_id) AS recurring_links
                FROM issues i
                JOIN issue_categories ic ON ic.category_id = i.category_id
                LEFT JOIN linked_issues li
                    ON li.issue_id = i.issue_id
                   AND li.link_type = 'recurring'
                GROUP BY ic.category_name
                ORDER BY recurring_links DESC, issue_count DESC, ic.category_name
            )
            WHERE ROWNUM <= :top_n
        """
        return self.fetch_all(query, {"top_n": top_n})

    def get_top_affected_modules(self, top_n: int = 5) -> list[dict[str, object]]:
        """Return modules with highest issue counts."""
        query = """
            SELECT *
            FROM (
                SELECT module_name, COUNT(*) AS issue_count
                FROM issues
                GROUP BY module_name
                ORDER BY issue_count DESC, module_name
            )
            WHERE ROWNUM <= :top_n
        """
        return self.fetch_all(query, {"top_n": top_n})

    def get_resolution_time_trend(self, days: int = 30) -> list[dict[str, object]]:
        """Return daily average resolution times."""
        query = """
            SELECT
                TRUNC(resolved_at) AS resolved_date,
                ROUND(AVG(resolution_minutes), 2) AS avg_resolution_minutes,
                COUNT(*) AS resolved_count
            FROM resolutions
            WHERE resolved_at >= (SYSTIMESTAMP - NUMTODSINTERVAL(:days, 'DAY'))
            GROUP BY TRUNC(resolved_at)
            ORDER BY resolved_date
        """
        return self.fetch_all(query, {"days": days})

    def get_most_helpful_solutions(self, top_n: int = 5) -> list[dict[str, object]]:
        """Return top helpful resolutions by feedback."""
        query = """
            SELECT *
            FROM (
                SELECT
                    i.issue_id,
                    i.title,
                    i.module_name,
                    ROUND(NVL(AVG(sf.rating), 0), 2) AS avg_rating,
                    COUNT(sf.feedback_id) AS feedback_count,
                    SUM(CASE WHEN sf.is_helpful = 'Y' THEN 1 ELSE 0 END) AS helpful_votes
                FROM issues i
                JOIN resolutions r ON r.issue_id = i.issue_id
                LEFT JOIN solution_feedback sf ON sf.resolution_id = r.resolution_id
                GROUP BY i.issue_id, i.title, i.module_name
                ORDER BY avg_rating DESC, helpful_votes DESC, feedback_count DESC
            )
            WHERE ROWNUM <= :top_n
        """
        return self.fetch_all(query, {"top_n": top_n})

    def get_resolved_vs_open_by_day(self, days: int = 14) -> list[dict[str, object]]:
        """Return daily counts of issue creation and resolutions."""
        query = """
            SELECT
                d.activity_date,
                SUM(d.created_count) AS created_count,
                SUM(d.resolved_count) AS resolved_count
            FROM (
                SELECT TRUNC(created_at) AS activity_date, COUNT(*) AS created_count, 0 AS resolved_count
                FROM issues
                WHERE created_at >= (SYSTIMESTAMP - NUMTODSINTERVAL(:days, 'DAY'))
                GROUP BY TRUNC(created_at)
                UNION ALL
                SELECT TRUNC(resolved_at) AS activity_date, 0 AS created_count, COUNT(*) AS resolved_count
                FROM resolutions
                WHERE resolved_at >= (SYSTIMESTAMP - NUMTODSINTERVAL(:days, 'DAY'))
                GROUP BY TRUNC(resolved_at)
            ) d
            GROUP BY d.activity_date
            ORDER BY d.activity_date
        """
        return self.fetch_all(query, {"days": days})
