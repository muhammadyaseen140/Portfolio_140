"""
Hidden Admin Login Page
Strictly authenticated via Supabase Auth.
"""

import streamlit as st
from utils import auth, db, styles


def render_login():
    # Login Card Styling
    styles.render_html(
        """
        <style>
        /* Card container styling */
        div[data-testid="stForm"] {
            background: rgba(30, 41, 59, 0.75) !important;
            backdrop-filter: blur(12px) !important;
            -webkit-backdrop-filter: blur(12px) !important;
            border: 1px solid rgba(148, 163, 184, 0.15) !important;
            border-radius: 16px !important;
            padding: 1.75rem 1.75rem 1.5rem 1.75rem !important;
            box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.35), 0 0 15px rgba(59, 130, 246, 0.08) !important;
        }

        /* Form input labels */
        div[data-testid="stForm"] label {
            font-weight: 500 !important;
            color: #E2E8F0 !important;
            font-size: 0.875rem !important;
        }

        /* Subtle Back to portfolio link */
        button[kind="tertiary"] {
            color: #64748B !important;
            background: transparent !important;
            border: none !important;
            font-size: 0.85rem !important;
            font-weight: 500 !important;
            box-shadow: none !important;
            padding: 0.25rem 0.5rem !important;
            transition: color 0.2s ease !important;
        }
        button[kind="tertiary"]:hover {
            color: #94A3B8 !important;
            background: transparent !important;
            border: none !important;
            transform: none !important;
        }
        </style>
        """
    )

    # Center column layout (approx 420px max-width on 1120px container)
    col_left, col_center, col_right = st.columns([1, 1.2, 1])

    with col_center:
        # If already authenticated, show status and direct navigation
        if auth.is_authenticated():
            current_email = auth.get_current_admin()
            st.success(f"Authenticated as **{current_email}**.")
            col_dash, col_out = st.columns(2)
            with col_dash:
                if st.button("⚙️ Admin Dashboard", type="primary", use_container_width=True):
                    st.query_params["admin"] = "dashboard"
                    st.rerun()
            with col_out:
                if st.button("🚪 Log Out", use_container_width=True):
                    auth.logout_admin()
                    st.query_params.clear()
                    st.rerun()
            return

        # Clean, centered header
        styles.render_html(
            """
            <div style="text-align: center; margin-top: 1.5rem; margin-bottom: 1.5rem;">
                <div style="display: inline-flex; align-items: center; justify-content: center; width: 44px; height: 44px; background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.25); border-radius: 12px; font-size: 1.25rem; margin-bottom: 0.75rem;">
                    🔒
                </div>
                <h2 style="font-size: 1.5rem; font-weight: 700; color: #F8FAFC; letter-spacing: -0.02em; margin: 0 0 0.35rem 0;">
                    Admin Login
                </h2>
                <p style="color: #94A3B8; font-size: 0.875rem; margin: 0; font-weight: 400;">
                    Sign in to manage your portfolio
                </p>
            </div>
            """
        )

        with st.form("admin_login_form"):
            email = st.text_input("Email", placeholder="you@example.com")
            password = st.text_input("Password", type="password", placeholder="••••••••••••")
            submit = st.form_submit_button("Sign In", type="primary", use_container_width=True)

            if submit:
                if not email.strip() or not password:
                    st.error("Invalid email or password.")
                else:
                    with st.spinner("Signing in..."):
                        db_client = db.get_supabase_client()
                        success, _ = auth.login_admin(email, password, db_client=db_client)
                        if success:
                            st.session_state.admin_user = email.strip().lower()
                            st.session_state["admin_user"] = email.strip().lower()
                            st.query_params["admin"] = "dashboard"
                            st.rerun()
                        else:
                            st.error("Invalid email or password.")

        # Subtle back link below the card
        if st.button("← Back to portfolio", key="back_to_portfolio", type="tertiary", use_container_width=True):
            st.session_state.pop("admin_user", None)
            st.session_state.pop("show_admin", None)
            st.query_params.clear()
            st.rerun()


if __name__ == "__main__" or True:
    render_login()
