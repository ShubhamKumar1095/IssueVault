"""Dashboard aggregation service."""

from __future__ import annotations

from typing import Any

import pandas as pd

from repositories.analytics_repository import AnalyticsRepository


class DashboardService:
    """Service that converts analytics repository output into dashboard payloads."""

    def __init__(self) -> None:
        self.analytics_repo = AnalyticsRepository()

    def get_kpis(self) -> dict[str, Any]:
        """Return KPI card values."""
        kpis = self.analytics_repo.get_kpi_snapshot()
        return {
            "total_open_issues": int(kpis.get("total_open_issues") or 0),
            "resolved_this_week": int(kpis.get("resolved_this_week") or 0),
            "avg_resolution_minutes": float(kpis.get("avg_resolution_minutes") or 0),
            "reopen_rate_pct": float(kpis.get("reopen_rate_pct") or 0),
            "duplicate_issues_avoided": int(kpis.get("duplicate_issues_avoided") or 0),
        }

    def get_status_distribution_df(self) -> pd.DataFrame:
        """Return status distribution as DataFrame."""
        rows = self.analytics_repo.get_status_distribution()
        return pd.DataFrame(rows)

    def get_top_recurring_categories_df(self, top_n: int = 5) -> pd.DataFrame:
        """Return top recurring categories as DataFrame."""
        rows = self.analytics_repo.get_top_recurring_categories(top_n=top_n)
        return pd.DataFrame(rows)

    def get_top_affected_modules_df(self, top_n: int = 5) -> pd.DataFrame:
        """Return top affected modules as DataFrame."""
        rows = self.analytics_repo.get_top_affected_modules(top_n=top_n)
        return pd.DataFrame(rows)

    def get_resolution_trend_df(self, days: int = 30) -> pd.DataFrame:
        """Return daily average resolution minutes."""
        rows = self.analytics_repo.get_resolution_time_trend(days=days)
        return pd.DataFrame(rows)

    def get_resolved_vs_open_df(self, days: int = 14) -> pd.DataFrame:
        """Return daily created/resolved counts."""
        rows = self.analytics_repo.get_resolved_vs_open_by_day(days=days)
        return pd.DataFrame(rows)

    def get_most_helpful_solutions_df(self, top_n: int = 5) -> pd.DataFrame:
        """Return top helpful solutions for table display."""
        rows = self.analytics_repo.get_most_helpful_solutions(top_n=top_n)
        return pd.DataFrame(rows)

    def get_dashboard_payload(self) -> dict[str, Any]:
        """Return all dashboard datasets in one call."""
        return {
            "kpis": self.get_kpis(),
            "status_distribution": self.get_status_distribution_df(),
            "top_categories": self.get_top_recurring_categories_df(),
            "top_modules": self.get_top_affected_modules_df(),
            "resolution_trend": self.get_resolution_trend_df(),
            "resolved_vs_open": self.get_resolved_vs_open_df(),
            "helpful_solutions": self.get_most_helpful_solutions_df(),
        }
