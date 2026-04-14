"""Streamlit page: Submit Issue."""

from __future__ import annotations

import streamlit as st

from models.enums import PriorityEnum, RoleEnum, SeverityEnum
from models.schemas import IssueSubmissionInput
from services.issue_service import IssueService
from utils.exceptions import IssueVaultError
from utils.session import require_login


st.set_page_config(page_title="Submit Issue - IssueVault", layout="wide")
st.title("Submit Issue")
st.caption("Capture structured issue details and detect similar historical issues before save.")

current_user = require_login(
    {
        RoleEnum.END_USER.value,
        RoleEnum.SUPPORT_ANALYST.value,
        RoleEnum.CONSULTANT.value,
        RoleEnum.ADMIN.value,
    }
)

issue_service = IssueService()
metadata = issue_service.get_submission_metadata()

category_options = {row["category_name"]: int(row["category_id"]) for row in metadata["categories"]}
release_options = {"None": None}
for release in metadata["releases"]:
    release_options[str(release["release_name"])] = int(release["release_id"])

assign_options = {"Unassigned": None}
for user in metadata["assignable_users"]:
    label = f"{user['full_name']} ({user['role_name']})"
    assign_options[label] = int(user["user_id"])

tag_options = [str(tag["tag_name"]) for tag in metadata["tags"]]

with st.form("submit_issue_form"):
    title = st.text_input("Title *", max_chars=250)
    description = st.text_area("Description *", height=120)

    col1, col2, col3 = st.columns(3)
    with col1:
        module_name = st.text_input("Module *", max_chars=120)
        environment = st.text_input("Environment *", value="Production")
    with col2:
        severity = st.selectbox("Severity *", [item.value for item in SeverityEnum], index=1)
        priority = st.selectbox("Priority *", [item.value for item in PriorityEnum], index=1)
    with col3:
        category_name = st.selectbox("Issue Category *", list(category_options.keys()))
        release_name = st.selectbox("Release", list(release_options.keys()))

    error_code = st.text_input("Error Code", max_chars=80)
    assigned_label = st.selectbox("Assigned Owner", list(assign_options.keys()))
    selected_tags = st.multiselect("Tags", tag_options)
    additional_tags = st.text_input("Additional Tags (comma separated)")

    steps_to_reproduce = st.text_area("Steps to Reproduce", height=110)
    expected_result = st.text_area("Expected Result", height=80)
    actual_result = st.text_area("Actual Result", height=80)
    business_impact = st.text_area("Business Impact", height=100)

    attachments = st.file_uploader(
        "Attachments",
        accept_multiple_files=True,
        help="Allowed types configured in .env via ALLOWED_EXTENSIONS.",
    )

    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        check_similar_clicked = st.form_submit_button("Check Similar Issues", use_container_width=True)
    with btn_col2:
        submit_clicked = st.form_submit_button("Submit Issue", type="primary", use_container_width=True)

all_tags = [tag.strip() for tag in selected_tags]
if additional_tags.strip():
    all_tags.extend([item.strip() for item in additional_tags.split(",") if item.strip()])

payload = IssueSubmissionInput(
    title=title.strip(),
    description=description.strip(),
    module_name=module_name.strip(),
    environment=environment.strip(),
    severity=severity,
    priority=priority,
    category_id=category_options.get(category_name, 0),
    error_code=error_code.strip() or None,
    steps_to_reproduce=steps_to_reproduce.strip() or None,
    expected_result=expected_result.strip() or None,
    actual_result=actual_result.strip() or None,
    business_impact=business_impact.strip() or None,
    release_id=release_options.get(release_name),
    assigned_to=assign_options.get(assigned_label),
    tags=all_tags,
)

if check_similar_clicked:
    try:
        similar = issue_service.preview_similar_issues(payload)
        st.markdown("### Top Similar Issues")
        if not similar:
            st.info("No similar issues found in current history.")
        else:
            st.dataframe(similar, use_container_width=True, hide_index=True)
    except IssueVaultError as exc:
        st.error(str(exc))
    except Exception as exc:  # pragma: no cover - runtime safety
        st.error(f"Could not run similarity check: {exc}")

if submit_clicked:
    try:
        result = issue_service.submit_issue(payload, reporter_user=current_user, uploaded_files=attachments)
        st.success(f"Issue #{result['issue_id']} submitted successfully.")
        if result["attachments"]:
            st.caption(f"Saved {len(result['attachments'])} attachment(s).")
    except IssueVaultError as exc:
        st.error(str(exc))
    except Exception as exc:  # pragma: no cover - runtime safety
        st.error(f"Could not submit issue: {exc}")
