"""Streamlit page: Search Issues."""

from __future__ import annotations

from datetime import date

import streamlit as st

from config import get_settings
from models.schemas import IssueSearchFilters
from services.issue_service import IssueService
from utils.exceptions import ResolveHubError
from utils.session import require_login


st.set_page_config(page_title="Search Issues - ResolveHub", layout="wide")
st.title("Search Issues")
st.caption("Use multi-field filters to find historical issues and resolution memory.")

current_user = require_login()
issue_service = IssueService()


@st.cache_data(ttl=get_settings().query_cache_ttl_sec, show_spinner=False)
def _load_search_metadata() -> dict[str, list[dict[str, object]]]:
    """Cache metadata shared by issue-search controls."""
    return IssueService().get_submission_metadata()


@st.cache_data(ttl=get_settings().query_cache_ttl_sec, show_spinner=False)
def _load_issue_bundle_cached(issue_id: int, viewer_user_id: int, viewer_role: str) -> dict[str, object]:
    """Cache issue detail bundle for smoother drill-down UX."""
    return IssueService().get_issue_bundle(
        issue_id=issue_id,
        viewer_user={"user_id": viewer_user_id, "role_name": viewer_role},
    )


metadata = _load_search_metadata()

category_options = {"All": None}
for row in metadata["categories"]:
    category_options[str(row["category_name"])] = int(row["category_id"])

owner_options = {"All": None}
for row in metadata["users"]:
    owner_options[str(row["full_name"])] = int(row["user_id"])

status_options = [
    "All",
    "New",
    "Under Review",
    "Known Issue",
    "In Progress",
    "Waiting for User",
    "Resolved",
    "Closed",
    "Reopened",
]

with st.expander("Search Filters", expanded=True):
    c1, c2, c3 = st.columns(3)
    with c1:
        keyword = st.text_input("Keyword")
        title = st.text_input("Title")
        error_code = st.text_input("Error Code")
    with c2:
        module_name = st.text_input("Module")
        severity = st.selectbox("Severity", ["All", "Low", "Medium", "High", "Critical"])
        status = st.selectbox("Status", status_options)
    with c3:
        category_name = st.selectbox("Category", list(category_options.keys()))
        owner_name = st.selectbox("Assigned Owner", list(owner_options.keys()))
        date_range = st.date_input(
            "Created Date Range",
            value=(date.today().replace(day=1), date.today()),
        )
    search_clicked = st.button("Run Search", type="primary")

if "search_results" not in st.session_state:
    st.session_state["search_results"] = []

if search_clicked:
    created_from = None
    created_to = None
    if isinstance(date_range, tuple) and len(date_range) == 2:
        created_from, created_to = date_range

    filters = IssueSearchFilters(
        keyword=keyword.strip() or None,
        title=title.strip() or None,
        error_code=error_code.strip() or None,
        module_name=module_name.strip() or None,
        severity=None if severity == "All" else severity,
        status=None if status == "All" else status,
        category_id=category_options.get(category_name),
        assigned_to=owner_options.get(owner_name),
        created_from=created_from,
        created_to=created_to,
    )
    try:
        st.session_state["search_results"] = issue_service.search_issues(filters, current_user)
    except ResolveHubError as exc:
        st.error(str(exc))
    except Exception as exc:  # pragma: no cover - runtime safety
        st.error(f"Search failed: {exc}")

results = st.session_state["search_results"]
st.markdown("### Results")
st.caption(f"{len(results)} issue(s) found")
if results:
    st.dataframe(results, use_container_width=True, hide_index=True)
else:
    st.info("No issues found with current filters.")

st.markdown("### Issue Details")
if not results:
    st.stop()

options = {
    f"#{row['issue_id']} | {row['title']}": int(row["issue_id"])
    for row in results
}
selected_label = st.selectbox("Select Issue", list(options.keys()))
selected_issue_id = options[selected_label]

try:
    bundle = _load_issue_bundle_cached(
        issue_id=selected_issue_id,
        viewer_user_id=int(current_user["user_id"]),
        viewer_role=str(current_user["role_name"]),
    )
except ResolveHubError as exc:
    st.error(str(exc))
    st.stop()
except Exception as exc:  # pragma: no cover - runtime safety
    st.error(f"Could not load issue details: {exc}")
    st.stop()

issue = bundle["issue"]
s1, s2, s3, s4 = st.columns(4)
s1.metric("Status", str(issue["status"]))
s2.metric("Severity", str(issue["severity"]))
s3.metric("Priority", str(issue["priority"]))
s4.metric("Module", str(issue["module_name"]))

st.write(f"**Title:** {issue['title']}")
st.write(f"**Category:** {issue['category_name']}")
st.write(f"**Reported By:** {issue['reported_by_name']}")
st.write(f"**Assigned To:** {issue.get('assigned_to_name') or 'Unassigned'}")
st.write(f"**Error Code:** {issue.get('error_code') or '-'}")
st.write(f"**Description:** {issue.get('description')}")

if issue.get("steps_to_reproduce"):
    st.write(f"**Steps to Reproduce:** {issue['steps_to_reproduce']}")
if issue.get("expected_result"):
    st.write(f"**Expected Result:** {issue['expected_result']}")
if issue.get("actual_result"):
    st.write(f"**Actual Result:** {issue['actual_result']}")
if issue.get("business_impact"):
    st.write(f"**Business Impact:** {issue['business_impact']}")

st.markdown("#### Tags")
if bundle["tags"]:
    st.dataframe(bundle["tags"], use_container_width=True, hide_index=True)
else:
    st.caption("No tags.")

st.markdown("#### Status History")
if bundle["status_history"]:
    st.dataframe(bundle["status_history"], use_container_width=True, hide_index=True)
else:
    st.caption("No status history.")

st.markdown("#### Comments")
if bundle["comments"]:
    st.dataframe(bundle["comments"], use_container_width=True, hide_index=True)
else:
    st.caption("No comments.")

st.markdown("#### Attachments")
if bundle["attachments"]:
    st.dataframe(bundle["attachments"], use_container_width=True, hide_index=True)
else:
    st.caption("No attachments.")

st.markdown("#### Linked Issues")
if bundle["linked_issues"]:
    st.dataframe(bundle["linked_issues"], use_container_width=True, hide_index=True)
else:
    st.caption("No linked issues.")

st.markdown("#### Resolution Memory")
if bundle["resolution"]:
    st.json(bundle["resolution"])
    if bundle["solution_feedback"]:
        st.dataframe(bundle["solution_feedback"], use_container_width=True, hide_index=True)
else:
    st.caption("No resolution has been captured yet.")
