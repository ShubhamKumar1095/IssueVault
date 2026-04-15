"""ResolveHub Streamlit entrypoint and login page."""

from __future__ import annotations

from dataclasses import asdict

import streamlit as st

from config import get_settings
from services.auth_service import AuthService
from services.issue_service import IssueService
from utils.exceptions import ResolveHubError
from utils.session import clear_current_user, get_current_user, set_current_user


@st.cache_data(ttl=get_settings().query_cache_ttl_sec, show_spinner=False)
def _home_my_issues_cached(user_id: int, role_name: str) -> list[dict[str, object]]:
    """Cache home-page snapshot query."""
    return IssueService().list_my_issues({"user_id": user_id, "role_name": role_name})


def _render_login(auth_service: AuthService) -> None:
    """Render login form when no user is authenticated."""
    st.subheader("Login")
    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Username", placeholder="support_1")
        password = st.text_input("Password", type="password", placeholder="Password@123")
        submitted = st.form_submit_button("Sign In")

    if submitted:
        try:
            user = auth_service.authenticate(username=username.strip(), password=password)
            set_current_user(asdict(user))
            st.success(f"Welcome, {user.full_name}.")
            st.rerun()
        except ResolveHubError as exc:
            st.error(str(exc))
        except Exception as exc:  # pragma: no cover - runtime safety
            st.error(f"Unable to login: {exc}")

    st.caption(
        "Seed users: end_user_1, support_1, consultant_1, manager_1, admin_1 | "
        "Password: Password@123"
    )


def _render_home(current_user: dict[str, object]) -> None:
    """Render home page content for authenticated user."""
    st.subheader("Workspace")
    st.write(
        "Use the **Pages** menu in the sidebar to navigate:\n"
        "- Submit Issue\n"
        "- Search Issues\n"
        "- My Issues\n"
        "- Support Desk\n"
        "- Dashboard\n"
        "- Admin"
    )

    try:
        my_issues = _home_my_issues_cached(
            user_id=int(current_user["user_id"]),
            role_name=str(current_user["role_name"]),
        )
    except Exception as exc:  # pragma: no cover - runtime safety
        st.warning(f"Could not load your issues: {exc}")
        my_issues = []

    st.markdown("### Quick Snapshot")
    st.metric("My Issue Count", len(my_issues))
    if my_issues:
        st.dataframe(my_issues[:10], use_container_width=True, hide_index=True)
    else:
        st.info("No issues found in your current scope.")


def main() -> None:
    """Render ResolveHub app home."""
    settings = get_settings()
    st.set_page_config(page_title=settings.app_name, page_icon=":bookmark_tabs:", layout="wide")

    st.title(settings.app_name)
    st.caption("Issue intelligence platform for reusable issue resolution memory.")

    auth_service = AuthService()
    current_user = get_current_user()

    with st.sidebar:
        st.markdown("### Session")
        if current_user:
            st.write(f"**User:** {current_user.get('full_name')}")
            st.write(f"**Role:** {current_user.get('role_name')}")
            if st.button("Logout", type="secondary"):
                clear_current_user()
                st.rerun()
        else:
            st.write("Not logged in")

    if not current_user:
        _render_login(auth_service)
        return

    _render_home(current_user)


if __name__ == "__main__":
    main()
