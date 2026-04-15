"""Streamlit page: Dashboard."""

from __future__ import annotations

import plotly.express as px
import streamlit as st

from config import get_settings
from models.enums import RoleEnum
from services.dashboard_service import DashboardService
from utils.session import require_login


st.set_page_config(page_title="Dashboard - ResolveHub", layout="wide")
st.title("Dashboard")
st.caption("Operational metrics for issue flow, recurrence, and resolution effectiveness.")

require_login({RoleEnum.MANAGER.value, RoleEnum.ADMIN.value})


@st.cache_data(ttl=get_settings().query_cache_ttl_sec, show_spinner=False)
def _dashboard_payload_cached() -> dict[str, object]:
    """Cache dashboard dataset payload for snappier rendering."""
    return DashboardService().get_dashboard_payload()


try:
    payload = _dashboard_payload_cached()
except Exception as exc:  # pragma: no cover - runtime safety
    st.error(f"Could not load dashboard data: {exc}")
    st.stop()

kpis = payload["kpis"]
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Open Issues", kpis["total_open_issues"])
c2.metric("Resolved This Week", kpis["resolved_this_week"])
c3.metric("Avg Resolution (min)", f"{kpis['avg_resolution_minutes']:.1f}")
c4.metric("Reopen Rate", f"{kpis['reopen_rate_pct']:.1f}%")
c5.metric("Duplicate Issues Avoided", kpis["duplicate_issues_avoided"])

status_df = payload["status_distribution"].copy()
top_categories_df = payload["top_categories"].copy()
top_modules_df = payload["top_modules"].copy()
resolution_trend_df = payload["resolution_trend"].copy()
resolved_vs_open_df = payload["resolved_vs_open"].copy()
helpful_df = payload["helpful_solutions"].copy()

row1_col1, row1_col2 = st.columns(2)
with row1_col1:
    st.markdown("### Issue Status Distribution")
    if not status_df.empty:
        fig = px.pie(status_df, names="status", values="issue_count", hole=0.45)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No status data available.")

with row1_col2:
    st.markdown("### Top Recurring Categories")
    if not top_categories_df.empty:
        fig = px.bar(
            top_categories_df,
            x="category_name",
            y="issue_count",
            color="recurring_links",
            text="recurring_links",
            labels={"category_name": "Category", "issue_count": "Issues", "recurring_links": "Recurring Links"},
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No category trend data available.")

row2_col1, row2_col2 = st.columns(2)
with row2_col1:
    st.markdown("### Top Affected Modules")
    if not top_modules_df.empty:
        fig = px.bar(top_modules_df, x="module_name", y="issue_count", text="issue_count")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No module data available.")

with row2_col2:
    st.markdown("### Resolution Time Trend")
    if not resolution_trend_df.empty:
        resolution_trend_df["resolved_date"] = resolution_trend_df["resolved_date"].astype(str)
        fig = px.line(
            resolution_trend_df,
            x="resolved_date",
            y="avg_resolution_minutes",
            markers=True,
            labels={"resolved_date": "Date", "avg_resolution_minutes": "Avg Minutes"},
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No resolution trend data available.")

st.markdown("### Created vs Resolved Trend")
if not resolved_vs_open_df.empty:
    resolved_vs_open_df["activity_date"] = resolved_vs_open_df["activity_date"].astype(str)
    fig = px.bar(
        resolved_vs_open_df,
        x="activity_date",
        y=["created_count", "resolved_count"],
        barmode="group",
        labels={"activity_date": "Date", "value": "Count", "variable": "Metric"},
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No created/resolved trend data available.")

st.markdown("### Most Helpful Solutions")
if not helpful_df.empty:
    st.dataframe(helpful_df, use_container_width=True, hide_index=True)
else:
    st.info("No solution feedback data available.")
