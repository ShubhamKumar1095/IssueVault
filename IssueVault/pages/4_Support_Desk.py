"""Streamlit page: Support Desk."""

from __future__ import annotations

from datetime import datetime

import streamlit as st

from config import get_settings
from models.enums import IssueStatusEnum, LinkTypeEnum, RoleEnum
from models.schemas import IssueSearchFilters, ResolutionInput
from services.issue_service import IssueService
from services.resolution_service import ResolutionService
from utils.exceptions import ResolveHubError
from utils.session import require_login


st.set_page_config(page_title="Support Desk - ResolveHub", layout="wide")
st.title("Support Desk")
st.caption("Triage, assign, collaborate, link related issues, and capture resolutions.")

current_user = require_login(
    {
        RoleEnum.SUPPORT_ANALYST.value,
        RoleEnum.CONSULTANT.value,
        RoleEnum.ADMIN.value,
    }
)

issue_service = IssueService()
resolution_service = ResolutionService()


@st.cache_data(ttl=get_settings().query_cache_ttl_sec, show_spinner=False)
def _support_metadata_cached() -> dict[str, list[dict[str, object]]]:
    """Cache support desk reference data."""
    return IssueService().get_submission_metadata()


@st.cache_data(ttl=get_settings().query_cache_ttl_sec, show_spinner=False)
def _support_issue_queue_cached(user_id: int, role_name: str) -> list[dict[str, object]]:
    """Cache support desk issue queue results."""
    return IssueService().search_issues(
        filters=IssueSearchFilters(),
        user={"user_id": user_id, "role_name": role_name},
    )


@st.cache_data(ttl=get_settings().query_cache_ttl_sec, show_spinner=False)
def _support_issue_bundle_cached(issue_id: int, user_id: int, role_name: str) -> dict[str, object]:
    """Cache support issue details."""
    return IssueService().get_issue_bundle(
        issue_id=issue_id,
        viewer_user={"user_id": user_id, "role_name": role_name},
    )


metadata = _support_metadata_cached()

try:
    all_issues = _support_issue_queue_cached(
        user_id=int(current_user["user_id"]),
        role_name=str(current_user["role_name"]),
    )
except Exception as exc:  # pragma: no cover - runtime safety
    st.error(f"Could not load issue queue: {exc}")
    st.stop()

open_statuses = {
    IssueStatusEnum.NEW.value,
    IssueStatusEnum.UNDER_REVIEW.value,
    IssueStatusEnum.KNOWN_ISSUE.value,
    IssueStatusEnum.IN_PROGRESS.value,
    IssueStatusEnum.WAITING_FOR_USER.value,
    IssueStatusEnum.REOPENED.value,
}
queue_rows = [row for row in all_issues if str(row.get("status")) in open_statuses]

st.markdown("### Open Queue")
if queue_rows:
    st.dataframe(queue_rows, use_container_width=True, hide_index=True)
else:
    st.info("No open issues in your scope.")

select_pool = queue_rows if queue_rows else all_issues
if not select_pool:
    st.stop()

issue_options = {f"#{row['issue_id']} | {row['title']}": int(row["issue_id"]) for row in select_pool}
selected_label = st.selectbox("Select Issue", list(issue_options.keys()))
issue_id = issue_options[selected_label]

try:
    bundle = _support_issue_bundle_cached(
        issue_id=issue_id,
        user_id=int(current_user["user_id"]),
        role_name=str(current_user["role_name"]),
    )
except ResolveHubError as exc:
    st.error(str(exc))
    st.stop()
except Exception as exc:  # pragma: no cover - runtime safety
    st.error(f"Could not load issue details: {exc}")
    st.stop()

issue = bundle["issue"]
st.write(f"**Current Status:** {issue['status']}")
st.write(f"**Assigned To:** {issue.get('assigned_to_name') or 'Unassigned'}")
st.write(f"**Description:** {issue['description']}")

assign_options = {"Unassigned": None}
for row in metadata["assignable_users"]:
    assign_options[f"{row['full_name']} ({row['role_name']})"] = int(row["user_id"])

with st.form("status_assignment_form"):
    col1, col2 = st.columns(2)
    with col1:
        assign_labels = list(assign_options.keys())
        current_assigned_id = issue.get("assigned_to")
        default_assign_index = 0
        for idx, key in enumerate(assign_labels):
            if assign_options[key] == current_assigned_id:
                default_assign_index = idx
                break
        assigned_label = st.selectbox("Assign Owner", assign_labels, index=default_assign_index)
    with col2:
        status_values = [item.value for item in IssueStatusEnum]
        current_status_index = status_values.index(issue["status"]) if issue["status"] in status_values else 0
        status = st.selectbox("Update Status", status_values, index=current_status_index)
    status_note = st.text_input("Status Note")
    update_clicked = st.form_submit_button("Apply Updates", type="primary")

if update_clicked:
    try:
        issue_service.assign_issue(issue_id=issue_id, assigned_to=assign_options[assigned_label], actor_user=current_user)
        issue_service.update_issue_status(
            issue_id=issue_id,
            new_status=status,
            actor_user=current_user,
            notes=status_note.strip() or None,
        )
        _support_issue_queue_cached.clear()
        _support_issue_bundle_cached.clear()
        st.success("Issue assignment/status updated.")
        st.rerun()
    except ResolveHubError as exc:
        st.error(str(exc))
    except Exception as exc:  # pragma: no cover - runtime safety
        st.error(f"Could not update issue: {exc}")

with st.form("support_comment_form"):
    comment_text = st.text_area("Add Comment", height=100)
    is_internal = st.checkbox("Internal Note", value=True)
    comment_clicked = st.form_submit_button("Post Comment")

if comment_clicked:
    try:
        issue_service.add_comment(
            issue_id=issue_id,
            actor_user=current_user,
            comment_text=comment_text,
            is_internal=is_internal,
        )
        _support_issue_bundle_cached.clear()
        st.success("Comment added.")
        st.rerun()
    except ResolveHubError as exc:
        st.error(str(exc))
    except Exception as exc:  # pragma: no cover - runtime safety
        st.error(f"Could not add comment: {exc}")

with st.form("link_issue_form"):
    link_candidates = {f"#{row['issue_id']} | {row['title']}": int(row["issue_id"]) for row in all_issues if int(row["issue_id"]) != issue_id}
    linked_label = st.selectbox("Link With Issue", list(link_candidates.keys())) if link_candidates else None
    link_type = st.selectbox("Link Type", [item.value for item in LinkTypeEnum])
    link_clicked = st.form_submit_button("Create Link")

if link_clicked and linked_label:
    try:
        issue_service.link_issues(
            issue_id=issue_id,
            linked_issue_id=link_candidates[linked_label],
            link_type=link_type,
            actor_user=current_user,
        )
        _support_issue_bundle_cached.clear()
        st.success("Issue link created.")
        st.rerun()
    except ResolveHubError as exc:
        st.error(str(exc))
    except Exception as exc:  # pragma: no cover - runtime safety
        st.error(f"Could not link issue: {exc}")

st.markdown("### Resolution Memory")
with st.form("resolution_form"):
    root_cause = st.text_area("Root Cause", height=80)
    workaround = st.text_area("Workaround", height=80)
    final_fix = st.text_area("Final Fix", height=80)
    resolution_steps = st.text_area("Resolution Steps", height=120)
    resolution_minutes = st.number_input("Resolution Minutes", min_value=1, value=60, step=5)
    resolve_clicked = st.form_submit_button("Save Resolution + Mark Resolved")

if resolve_clicked:
    try:
        payload = ResolutionInput(
            issue_id=issue_id,
            root_cause=root_cause.strip(),
            workaround=workaround.strip(),
            final_fix=final_fix.strip(),
            resolution_steps=resolution_steps.strip(),
            resolver_id=int(current_user["user_id"]),
            resolution_minutes=int(resolution_minutes),
            resolved_at=datetime.now(),
        )
        resolution_service.upsert_resolution(payload=payload, actor_user=current_user, status_note="Resolved by Support Desk.")
        _support_issue_queue_cached.clear()
        _support_issue_bundle_cached.clear()
        st.success("Resolution saved and status updated to Resolved.")
        st.rerun()
    except ResolveHubError as exc:
        st.error(str(exc))
    except Exception as exc:  # pragma: no cover - runtime safety
        st.error(f"Could not save resolution: {exc}")

st.markdown("### Existing Collaboration Data")
st.write("**Comments**")
st.dataframe(bundle["comments"], use_container_width=True, hide_index=True)
st.write("**Linked Issues**")
st.dataframe(bundle["linked_issues"], use_container_width=True, hide_index=True)
