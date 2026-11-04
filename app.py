"""
Personal Portfolio Web Application with Private Admin Panel
Deployable on Streamlit Community Cloud with Supabase backend.
"""

import streamlit as st
from utils import auth, db, styles

# Set global page configuration (must be first Streamlit command)
st.set_page_config(
    page_title="Portfolio | Control Center",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply global styling
styles.render_html(styles.get_custom_css())


def main():
    # Define pages
    page_portfolio = st.Page(
        "pages/portfolio.py",
        title="Portfolio",
        icon="👤"
    )
    page_login = st.Page(
        "pages/admin_login.py",
        title="Admin Login",
        icon="🔒"
    )
    page_dashboard = st.Page(
        "pages/admin_dashboard.py",
        title="Admin Dashboard",
        icon="⚙️"
    )

    admin_user = st.session_state.get("admin_user")
    query_admin = st.query_params.get("admin")
    query_view = st.query_params.get("view")

    # Routing based on authentication and URL query parameters
    if admin_user:
        # Authenticated Admin: route to dashboard by default (or live preview if requested)
        if query_view == "portfolio":
            page_portfolio.default = True
            page_dashboard.default = False
        else:
            page_dashboard.default = True
            page_portfolio.default = False

        nav = st.navigation(
            {
                "Admin Control": [page_dashboard],
                "Live Preview": [page_portfolio]
            },
            position="sidebar"
        )
    elif query_admin in ["login", "dashboard", "true", "1"] or st.session_state.get("show_admin"):
        # Requirement 3: If admin_user is missing, redirect to the login form instead of the public page
        page_login.default = True
        nav = st.navigation([page_login], position="hidden")
    else:
        # Public visitor view
        page_portfolio.default = True
        nav = st.navigation([page_portfolio], position="hidden")

    nav.run()


if __name__ == "__main__":
    main()
