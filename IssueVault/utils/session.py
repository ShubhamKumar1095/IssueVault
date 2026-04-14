"""Streamlit session helpers for authentication state."""

from __future__ import annotations

from typing import Any

import streamlit as st


SESSION_USER_KEY = "issuevault_current_user"


def set_current_user(user_payload: dict[str, Any]) -> None:
    """Persist authenticated user in Streamlit session."""
    st.session_state[SESSION_USER_KEY] = user_payload


def get_current_user() -> dict[str, Any] | None:
    """Return current session user if available."""
    return st.session_state.get(SESSION_USER_KEY)


def clear_current_user() -> None:
    """Clear authenticated user from session."""
    if SESSION_USER_KEY in st.session_state:
        del st.session_state[SESSION_USER_KEY]


def require_login(required_roles: set[str] | None = None) -> dict[str, Any]:
    """
    Stop page execution if user is not authenticated or lacks required role.

    Returns current user payload when checks pass.
    """
    user = get_current_user()
    if not user:
        st.warning("Please log in from the Home page first.")
        st.stop()

    if required_roles and user.get("role_name") not in required_roles:
        st.error("You do not have permission to access this page.")
        st.stop()

    return user
