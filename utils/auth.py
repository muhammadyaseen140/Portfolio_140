"""
Authentication and Session Management for Admin Panel
Supabase Auth is the SOLE authentication provider for administrator login.
"""

import streamlit as st
import logging
import textwrap

logger = logging.getLogger(__name__)


def is_authenticated() -> bool:
    """Check if the current session is authenticated as admin."""
    return bool(st.session_state.get("admin_user"))


def get_current_admin() -> str:
    """Get the email of the currently authenticated admin."""
    user = st.session_state.get("admin_user")
    if isinstance(user, dict):
        return user.get("email", "")
    return str(user or "")


def login_admin(email: str, password: str, db_client=None) -> tuple[bool, str]:
    """
    Authenticate the admin strictly via Supabase Auth.
    On success: sets st.session_state.admin_user and session tokens.
    """
    if not email or not password:
        return False, "Please enter both email and password."

    cleaned_email = email.strip().lower()

    if db_client is None:
        from utils import db
        db_client = db.get_supabase_client()

    if db_client is None:
        return False, "Supabase client is not configured. Check SUPABASE_URL and SUPABASE_KEY."

    try:
        auth_response = db_client.auth.sign_in_with_password({
            "email": cleaned_email,
            "password": password
        })
        if auth_response and auth_response.user:
            # Set st.session_state.admin_user as requested
            st.session_state.admin_user = auth_response.user.email
            st.session_state["admin_user"] = auth_response.user.email
            st.session_state["is_admin_authenticated"] = True
            st.session_state["admin_user_id"] = auth_response.user.id
            if hasattr(auth_response, "session") and auth_response.session:
                st.session_state["admin_jwt_token"] = auth_response.session.access_token
            return True, "Login successful via Supabase Auth."
    except Exception as e:
        err_msg = str(e)
        logger.warning(f"Supabase auth attempt failed: {err_msg}")
        return False, f"Login failed: {err_msg}"

    return False, "Invalid credentials. Please verify your email and password."


def logout_admin(db_client=None):
    """Log out the admin user from Supabase and clear session state."""
    if db_client is None:
        from utils import db
        db_client = db.get_supabase_client()

    if db_client:
        try:
            db_client.auth.sign_out()
        except Exception as e:
            logger.warning(f"Error signing out of Supabase: {e}")

    # Clear admin user session states
    st.session_state.pop("admin_user", None)
    st.session_state.pop("is_admin_authenticated", None)
    st.session_state.pop("admin_jwt_token", None)
    st.session_state.pop("admin_user_id", None)
    st.session_state.pop("show_admin", None)


def require_auth():
    """
    Block execution of the current page if user is not authenticated.
    Redirects to the login form if admin_user is missing.
    """
    if not is_authenticated():
        st.query_params["admin"] = "login"
        st.session_state["show_admin"] = True
        st.rerun()
