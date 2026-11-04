"""
Hidden Admin Login Page
Strictly authenticated via Supabase Auth.
"""

import streamlit as st
from utils import auth, db, styles


def render_login():
    # If already authenticated, redirect to dashboard
    if auth.is_authenticated():
        current_email = auth.get_current_admin()
        st.success(f"✅ Authenticated as **{current_email}**.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⚙️ Open Admin Dashboard", type="primary"):
                st.query_params["admin"] = "dashboard"
                st.rerun()
        with col2:
            if st.button("🚪 Log Out"):
                auth.logout_admin()
                st.query_params.clear()
                st.rerun()
        return

    styles.render_html(
        """
        <div style="max-width: 480px; margin: 3rem auto 1.5rem auto; text-align: center;">
            <div style="display: inline-block; padding: 0.8rem 1.2rem; background: rgba(59, 130, 246, 0.1); border-radius: 50%; font-size: 2.2rem; margin-bottom: 1rem; border: 1px solid rgba(59, 130, 246, 0.3);">
                🔐
            </div>
            <h2 style="color: #FFFFFF; font-weight: 800; letter-spacing: -0.02em; margin-bottom: 0.3rem;">
                Admin Portal
            </h2>
            <p style="color: #94A3B8; font-size: 0.95rem;">
                Sign in with your Supabase Auth administrator credentials.
            </p>
        </div>
        """
    )

    login_box = st.container()
    with login_box:
        styles.render_html('<div class="glass-card" style="max-width: 480px; margin: 0 auto 1.5rem auto;">')

        with st.form("admin_login_form"):
            email = st.text_input("Supabase Admin Email", placeholder="admin@example.com")
            password = st.text_input("Password", type="password", placeholder="••••••••••••")
            submit = st.form_submit_button("Sign In with Supabase 🚀", type="primary")

            if submit:
                db_client = db.get_supabase_client()
                success, msg = auth.login_admin(email, password, db_client=db_client)
                if success:
                    # Requirement 1: Set st.session_state.admin_user and route to admin dashboard in same session
                    st.session_state.admin_user = email.strip().lower()
                    st.session_state["admin_user"] = email.strip().lower()
                    st.query_params["admin"] = "dashboard"
                    st.rerun()
                else:
                    st.error(msg)

        styles.render_html('</div>')

    with st.expander("ℹ️ How to create your Admin Account in Supabase", expanded=False):
        st.markdown(
            """
            1. Open your **[Supabase Dashboard](https://supabase.com/dashboard)**.
            2. Go to **Authentication** $\\rightarrow$ **Users**.
            3. Click **Add User** $\\rightarrow$ **Create User**.
            4. Enter your administrator email and a secure password.
            5. Toggle **Auto Confirm User?** to `ON`, then click **Create User**.
            6. Return here and sign in with those exact credentials!
            """
        )

    styles.render_html("<div style='text-align: center; margin-top: 1rem;'></div>")
    if st.button("⬅️ Back to Public Portfolio"):
        st.session_state.pop("admin_user", None)
        st.query_params.clear()
        st.rerun()


if __name__ == "__main__" or True:
    render_login()
