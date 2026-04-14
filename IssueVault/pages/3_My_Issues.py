"""Streamlit page: My Issues."""

from __future__ import annotations

import streamlit as st

from models.enums import RoleEnum
from services.issue_service import IssueService
from services.resolution_service import ResolutionService
from utils.exceptions import IssueVaultError
from utils.session import require_login


st.set_page_config(page_title="My Issues - IssueVault", layout="wide")
st.title("My Issues")
st.caption("Track issues in your scope and collaborate through comments and feedback.")

current_user = require_login()
issue_service = IssueService()
resolution_service = ResolutionService()

try:
    my_issues = issue_service.list_my_issues(current_user)
except Exception as exc:  # pragma: no cover - runtime safety
    st.error(f"Could not load issues: {exc}")
    st.stop()

if not my_issues:
    st.info("No issues found for your scope.")
    st.stop()

st.dataframe(my_issues, use_container_width=True, hide_index=True)

issue_options = {f"#{row['issue_id']} | {row['title']}": int(row["issue_id"]) for row in my_issues}
selected_label = st.selectbox("Select Issue", list(issue_options.keys()))
issue_id = issue_options[selected_label]

try:
    bundle = issue_service.get_issue_bundle(issue_id, current_user)
except IssueVaultError as exc:
    st.error(str(exc))
    st.stop()
except Exception as exc:  # pragma: no cover - runtime safety
    st.error(f"Could not load issue details: {exc}")
    st.stop()

issue = bundle["issue"]
st.subheader(f"Issue #{issue['issue_id']} - {issue['title']}")
st.write(f"**Status:** {issue['status']} | **Severity:** {issue['severity']} | **Priority:** {issue['priority']}")
st.write(f"**Description:** {issue['description']}")

st.markdown("### Comments")
if bundle["comments"]:
    st.dataframe(bundle["comments"], use_container_width=True, hide_index=True)
else:
    st.caption("No comments yet.")

with st.form("my_issue_comment_form"):
    comment_text = st.text_area("Add Comment", height=100)
    add_comment_clicked = st.form_submit_button("Post Comment")

if add_comment_clicked:
    try:
        issue_service.add_comment(issue_id=issue_id, actor_user=current_user, comment_text=comment_text)
        st.success("Comment added.")
        st.rerun()
    except IssueVaultError as exc:
        st.error(str(exc))
    except Exception as exc:  # pragma: no cover - runtime safety
        st.error(f"Could not add comment: {exc}")

st.markdown("### Resolution")
if bundle["resolution"]:
    st.write(bundle["resolution"])
    if bundle["solution_feedback"]:
        st.markdown("#### Existing Feedback")
        st.dataframe(bundle["solution_feedback"], use_container_width=True, hide_index=True)
else:
    st.caption("No resolution captured yet.")

if current_user.get("role_name") == RoleEnum.END_USER.value and bundle["resolution"]:
    with st.form("solution_feedback_form"):
        rating = st.slider("Rating", min_value=1.0, max_value=5.0, value=4.0, step=0.5)
        is_helpful = st.checkbox("This solution was helpful", value=True)
        feedback_comment = st.text_area("Feedback", height=80)
        feedback_clicked = st.form_submit_button("Submit Feedback")

    if feedback_clicked:
        try:
            resolution_service.add_solution_feedback(
                issue_id=issue_id,
                user_id=int(current_user["user_id"]),
                rating=rating,
                is_helpful=is_helpful,
                comments=feedback_comment.strip() or None,
            )
            st.success("Feedback submitted.")
            st.rerun()
        except IssueVaultError as exc:
            st.error(str(exc))
        except Exception as exc:  # pragma: no cover - runtime safety
            st.error(f"Could not submit feedback: {exc}")
