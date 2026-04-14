"""Streamlit page: Admin."""

from __future__ import annotations

import streamlit as st

from models.enums import RoleEnum
from services.admin_service import AdminService
from utils.exceptions import IssueVaultError
from utils.session import require_login


st.set_page_config(page_title="Admin - IssueVault", layout="wide")
st.title("Admin")
st.caption("Manage users, categories, and baseline configuration for the MVP.")

require_login({RoleEnum.ADMIN.value})
admin_service = AdminService()

try:
    data = admin_service.get_admin_reference_data()
except Exception as exc:  # pragma: no cover - runtime safety
    st.error(f"Could not load admin data: {exc}")
    st.stop()

tab_users, tab_categories = st.tabs(["Users", "Categories"])

with tab_users:
    st.markdown("### Existing Users")
    st.dataframe(data["users"], use_container_width=True, hide_index=True)

    role_names = [str(row["role_name"]) for row in data["roles"]]
    team_options = {"No Team": None}
    for team in data["teams"]:
        team_options[str(team["team_name"])] = int(team["team_id"])

    st.markdown("### Create User")
    with st.form("admin_create_user_form"):
        username = st.text_input("Username *")
        full_name = st.text_input("Full Name *")
        email = st.text_input("Email *")
        password = st.text_input("Password *", type="password")
        role_name = st.selectbox("Role *", role_names)
        team_name = st.selectbox("Team", list(team_options.keys()))
        create_user_clicked = st.form_submit_button("Create User", type="primary")

    if create_user_clicked:
        try:
            new_user_id = admin_service.create_user(
                username=username,
                full_name=full_name,
                email=email,
                password=password,
                role_name=role_name,
                team_id=team_options.get(team_name),
            )
            st.success(f"User created with ID {new_user_id}.")
            st.rerun()
        except IssueVaultError as exc:
            st.error(str(exc))
        except Exception as exc:  # pragma: no cover - runtime safety
            st.error(f"Could not create user: {exc}")

with tab_categories:
    st.markdown("### Existing Categories")
    st.dataframe(data["categories"], use_container_width=True, hide_index=True)

    st.markdown("### Add Category")
    with st.form("admin_create_category_form"):
        category_name = st.text_input("Category Name *")
        category_description = st.text_area("Description")
        create_category_clicked = st.form_submit_button("Add Category")

    if create_category_clicked:
        try:
            category_id = admin_service.create_category(category_name, category_description)
            st.success(f"Category created with ID {category_id}.")
            st.rerun()
        except IssueVaultError as exc:
            st.error(str(exc))
        except Exception as exc:  # pragma: no cover - runtime safety
            st.error(f"Could not create category: {exc}")
