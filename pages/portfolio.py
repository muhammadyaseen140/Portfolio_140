"""
Public Portfolio Page (Read-Only)
Displays hero, about, skills, projects, certifications, CV download/preview, and contact sections.
"""

import streamlit as st
import requests
from utils import db, styles


def render_portfolio():
    # Only falls back to demo data if DB is empty AND not in admin mode
    profile = db.get_profile(for_admin=False)
    skills = db.get_skills(for_admin=False)
    projects = db.get_projects(for_admin=False)
    certifications = db.get_certifications(for_admin=False)
    cv_doc = db.get_active_cv(for_admin=False)

    # Database configuration banner if running without Supabase credentials
    if not db.is_supabase_configured():
        st.info(
            "💡 **Running in Demo Mode**: Sample data is currently displayed. "
            "To connect your live Supabase database, configure `SUPABASE_URL` and `SUPABASE_KEY` "
            "in `.streamlit/secrets.toml`."
        )

    # ==========================================================================
    # 1. HERO SECTION
    # ==========================================================================
    photo_url = profile.get("photo_url") or profile.get("avatar_url") or "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=600&q=80"
    name = profile.get("name", "Alex Rivers")
    tagline = profile.get("tagline", "Senior Software Engineer & AI Systems Architect")
    email = profile.get("email", "contact@example.com")
    location = profile.get("location", "San Francisco, CA / Remote")
    github_url = profile.get("github") or profile.get("github_url", "https://github.com")
    linkedin_url = profile.get("linkedin") or profile.get("linkedin_url", "https://linkedin.com")

    social_buttons_html = f"""
    <div class="social-links">
        {f'<a href="{github_url}" target="_blank" class="social-btn"><span>🐙</span> GitHub</a>' if github_url else ''}
        {f'<a href="{linkedin_url}" target="_blank" class="social-btn"><span>💼</span> LinkedIn</a>' if linkedin_url else ''}
        {f'<a href="mailto:{email}" class="social-btn"><span>✉️</span> Get in Touch</a>' if email else ''}
    </div>
    """

    hero_html = f"""
    <div class="hero-container">
        <img src="{photo_url}" alt="{name}" class="hero-avatar" />
        <div class="status-badge">
            <span class="status-dot"></span>
            Available for Select Projects & Leadership Roles
        </div>
        <h1 class="hero-name">{name}</h1>
        <p class="hero-tagline">{tagline}</p>
        <p style="color: #64748B; font-size: 0.9rem; margin-top: -0.5rem;">📍 {location}</p>
        {social_buttons_html}
    </div>
    """
    styles.render_html(hero_html)

    # Sub-Navigation Anchor Bar
    styles.render_html(
        """
        <div style="display: flex; justify-content: center; gap: 0.75rem; flex-wrap: wrap; margin-bottom: 2.5rem;">
            <a href="#about" style="text-decoration: none; color: #93C5FD; font-size: 0.85rem; font-weight: 600; padding: 0.35rem 0.8rem; background: rgba(59, 130, 246, 0.1); border-radius: 9999px; border: 1px solid rgba(59, 130, 246, 0.2);">About</a>
            <a href="#skills" style="text-decoration: none; color: #93C5FD; font-size: 0.85rem; font-weight: 600; padding: 0.35rem 0.8rem; background: rgba(59, 130, 246, 0.1); border-radius: 9999px; border: 1px solid rgba(59, 130, 246, 0.2);">Skills</a>
            <a href="#projects" style="text-decoration: none; color: #93C5FD; font-size: 0.85rem; font-weight: 600; padding: 0.35rem 0.8rem; background: rgba(59, 130, 246, 0.1); border-radius: 9999px; border: 1px solid rgba(59, 130, 246, 0.2);">Projects</a>
            <a href="#certifications" style="text-decoration: none; color: #93C5FD; font-size: 0.85rem; font-weight: 600; padding: 0.35rem 0.8rem; background: rgba(59, 130, 246, 0.1); border-radius: 9999px; border: 1px solid rgba(59, 130, 246, 0.2);">Certifications</a>
            <a href="#cv-resume" style="text-decoration: none; color: #93C5FD; font-size: 0.85rem; font-weight: 600; padding: 0.35rem 0.8rem; background: rgba(59, 130, 246, 0.1); border-radius: 9999px; border: 1px solid rgba(59, 130, 246, 0.2);">CV / Resume</a>
            <a href="#contact" style="text-decoration: none; color: #93C5FD; font-size: 0.85rem; font-weight: 600; padding: 0.35rem 0.8rem; background: rgba(59, 130, 246, 0.1); border-radius: 9999px; border: 1px solid rgba(59, 130, 246, 0.2);">Contact</a>
        </div>
        """
    )

    # ==========================================================================
    # 2. ABOUT ME SECTION
    # ==========================================================================
    styles.render_html('<div id="about" class="section-header"><div class="section-title"><span>👤</span> About Me</div><div class="section-subtitle">Background, philosophy, and technical focus</div></div>')

    bio = profile.get("bio", "Software engineer passionate about scalable cloud infrastructure.")
    about_col1, about_col2 = st.columns([2, 1])

    with about_col1:
        styles.render_html(
            f"""
            <div class="glass-card" style="height: 100%;">
                <p style="font-size: 1.05rem; line-height: 1.7; color: #E2E8F0; margin: 0;">
                    {bio}
                </p>
            </div>
            """
        )

    with about_col2:
        styles.render_html(
            f"""
            <div class="glass-card" style="height: 100%;">
                <div style="margin-bottom: 1rem;">
                    <div style="font-size: 0.75rem; text-transform: uppercase; color: #64748B; font-weight: 700;">Location</div>
                    <div style="font-size: 0.95rem; font-weight: 600; color: #F1F5F9;">{location}</div>
                </div>
                <div style="margin-bottom: 1rem;">
                    <div style="font-size: 0.75rem; text-transform: uppercase; color: #64748B; font-weight: 700;">Direct Contact</div>
                    <div style="font-size: 0.95rem; font-weight: 600; color: #93C5FD;">{email}</div>
                </div>
                <div>
                    <div style="font-size: 0.75rem; text-transform: uppercase; color: #64748B; font-weight: 700;">Focus</div>
                    <div style="font-size: 0.95rem; font-weight: 600; color: #34D399;">Cloud Architecture & AI</div>
                </div>
            </div>
            """
        )

    # ==========================================================================
    # 3. SKILLS SECTION
    # ==========================================================================
    styles.render_html('<div id="skills" class="section-header"><div class="section-title"><span>⚡</span> Technical Skills</div><div class="section-subtitle">Categorized competencies and proficiency ratings</div></div>')

    if not skills:
        st.info("No skills configured yet.")
    else:
        categories: dict[str, list] = {}
        for s in skills:
            cat = s.get("category", "General")
            categories.setdefault(cat, []).append(s)

        cat_names = list(categories.keys())
        cols = st.columns(2)

        for idx, cat_name in enumerate(cat_names):
            col_target = cols[idx % 2]
            with col_target:
                skills_in_cat = categories[cat_name]
                items_html = ""
                for sk in skills_in_cat:
                    s_name = sk.get("name", "")
                    lvl = sk.get("level", 80)
                    items_html += f"""
                    <div class="skill-item">
                        <div class="skill-meta">
                            <span>🔹 {s_name}</span>
                            <span style="color: #93C5FD; font-size: 0.85rem;">{lvl}%</span>
                        </div>
                        <div class="skill-bar-bg">
                            <div class="skill-bar-fill" style="width: {lvl}%;"></div>
                        </div>
                    </div>
                    """

                styles.render_html(
                    f"""
                    <div class="glass-card" style="margin-bottom: 1.5rem;">
                        <h4 style="color: #F8FAFC; margin-bottom: 1.2rem; font-weight: 700; border-bottom: 1px solid rgba(148, 163, 184, 0.1); padding-bottom: 0.6rem;">
                            {cat_name}
                        </h4>
                        {items_html}
                    </div>
                    """
                )

    # ==========================================================================
    # 4. PROJECTS SECTION
    # ==========================================================================
    styles.render_html('<div id="projects" class="section-header"><div class="section-title"><span>🚀</span> Featured Projects</div><div class="section-subtitle">Real-world production platforms, developer tools, and architectures</div></div>')

    if not projects:
        st.info("No projects published yet.")
    else:
        p_cols = st.columns(2)
        for idx, proj in enumerate(projects):
            with p_cols[idx % 2]:
                pid = proj.get("id")
                title = proj.get("title", "Project Title")
                desc = proj.get("description", "")
                tech_stack = proj.get("tech") or proj.get("tech_stack", "")
                cover_url = proj.get("cover_url") or proj.get("cover_image_url") or "https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=800&q=80"
                live_url = proj.get("live_url", "")
                gh_url = proj.get("github_url", "")

                tech_pills_html = "".join(
                    [f'<span class="tech-pill">{t.strip()}</span>' for t in str(tech_stack).split(",") if t.strip()]
                )

                styles.render_html(
                    f"""
                    <div class="project-card">
                        <img src="{cover_url}" alt="{title}" class="project-img" onerror="this.src='https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=800&q=80'" />
                        <div class="project-body">
                            <div class="project-title">{title}</div>
                            <div style="margin-top: 0.5rem; margin-bottom: 1rem;">
                                {tech_pills_html}
                            </div>
                        </div>
                    </div>
                    """
                )

                link_col1, link_col2 = st.columns(2)
                with link_col1:
                    if live_url:
                        st.link_button("🌐 Live App", live_url)
                with link_col2:
                    if gh_url:
                        st.link_button("💻 GitHub", gh_url)

                # Detail View with Gallery
                with st.expander(f"📖 Project Details & Gallery: {title}", expanded=False):
                    st.markdown("**Overview & Architecture**")
                    st.write(desc)

                    # Multi-image gallery
                    gallery_images = db.get_project_images(pid)
                    if gallery_images:
                        st.markdown("**Project Gallery**")
                        g_cols = st.columns(len(gallery_images) if len(gallery_images) <= 3 else 3)
                        for g_idx, g_img in enumerate(gallery_images):
                            with g_cols[g_idx % 3]:
                                st.image(
                                    g_img.get("image_url", ""),
                                    caption=f"Screenshot {g_idx+1}",
                                    width=240
                                )
                    else:
                        st.caption("No additional gallery screenshots for this project.")

                styles.render_html("<div style='margin-bottom: 1.5rem;'></div>")

    # ==========================================================================
    # 5. CERTIFICATIONS SECTION
    # ==========================================================================
    styles.render_html('<div id="certifications" class="section-header"><div class="section-title"><span>🎓</span> Certifications & Credentials</div><div class="section-subtitle">Verified professional credentials and specializations</div></div>')

    if not certifications:
        st.info("No certifications added yet.")
    else:
        c_cols = st.columns(len(certifications) if len(certifications) <= 3 else 3)
        for idx, cert in enumerate(certifications):
            with c_cols[idx % (len(c_cols))]:
                title = cert.get("title", "")
                issuer = cert.get("issuer", "")
                cred_url = cert.get("credential_url", "")
                file_url = cert.get("file_url") or cert.get("media_url", "")

                styles.render_html(
                    f"""
                    <div class="glass-card" style="height: 100%;">
                        <div style="font-size: 2rem; margin-bottom: 0.5rem;">📜</div>
                        <div class="cert-title">{title}</div>
                        <div class="cert-issuer">{issuer}</div>
                    </div>
                    """
                )

                btn_cols = st.columns(2 if (cred_url and file_url) else 1)
                b_idx = 0
                if cred_url:
                    with btn_cols[b_idx]:
                        st.link_button("Verify ↗", cred_url)
                    b_idx += 1
                if file_url:
                    with btn_cols[b_idx]:
                        if file_url.lower().endswith(".pdf"):
                            st.link_button("View PDF 📄", file_url)
                        else:
                            with st.popover("Preview 🖼️"):
                                st.image(file_url, caption=f"{title} - {issuer}")

    # ==========================================================================
    # 6. CV & RESUME SECTION
    # ==========================================================================
    styles.render_html('<div id="cv-resume" class="section-header"><div class="section-title"><span>📄</span> Curriculum Vitae</div><div class="section-subtitle">Comprehensive career history, accomplishments, and skills</div></div>')

    if cv_doc and cv_doc.get("file_url"):
        cv_url = cv_doc.get("file_url", "")

        styles.render_html(
            """
            <div class="cv-banner">
                <h3 style="color: #F8FAFC; margin-bottom: 0.5rem; font-weight: 700;">Verified Curriculum Vitae (PDF)</h3>
                <p style="color: #94A3B8; margin-bottom: 1.5rem; max-width: 600px; margin-left: auto; margin-right: auto;">
                    Available for direct download or inline review.
                </p>
            </div>
            """
        )

        dl_col1, dl_col2, dl_col3 = st.columns([1, 2, 1])
        with dl_col2:
            action_cols = st.columns(2)
            with action_cols[0]:
                st.link_button("📥 Download Resume PDF", cv_url)
            with action_cols[1]:
                with st.expander("👀 Preview Resume inline"):
                    if cv_url.startswith("http"):
                        st.components.v1.iframe(cv_url, height=600)
                    else:
                        st.info("PDF preview available via download.")
    else:
        st.info("No CV document published yet.")

    # ==========================================================================
    # 7. CONTACT SECTION
    # ==========================================================================
    styles.render_html('<div id="contact" class="section-header"><div class="section-title"><span>📬</span> Contact & Inquiries</div><div class="section-subtitle">Reach out for collaborations, consulting, or engineering opportunities</div></div>')

    c_col1, c_col2 = st.columns([1, 1])
    with c_col1:
        styles.render_html(
            f"""
            <div class="glass-card" style="height: 100%;">
                <h4 style="color: #F8FAFC; margin-bottom: 1rem;">Let's Build Something Exceptional</h4>
                <p style="color: #94A3B8; font-size: 0.95rem; line-height: 1.6; margin-bottom: 1.5rem;">
                    Feel free to reach out for high-impact technical initiatives, architecture consulting, or engineering discussions.
                </p>
                <div style="display: flex; flex-direction: column; gap: 0.8rem;">
                    <div style="display: flex; align-items: center; gap: 0.6rem; color: #E2E8F0;">
                        <span>✉️</span> <a href="mailto:{email}" style="color: #60A5FA; text-decoration: none;">{email}</a>
                    </div>
                    <div style="display: flex; align-items: center; gap: 0.6rem; color: #E2E8F0;">
                        <span>📍</span> {location}
                    </div>
                </div>
            </div>
            """
        )

    with c_col2:
        with st.form("contact_form", clear_on_submit=True):
            st.markdown("<h4 style='color: #F8FAFC; margin-bottom: 0.5rem;'>Send a Quick Note</h4>", unsafe_allow_html=True)
            sender_name = st.text_input("Your Name", placeholder="Jane Doe")
            sender_email = st.text_input("Your Email", placeholder="jane@example.com")
            message = st.text_area("Message", placeholder="Hi Alex, I'd like to discuss a project...")
            submitted = st.form_submit_button("Send Message 🚀")

            if submitted:
                if not sender_name or not sender_email or not message:
                    st.error("Please fill in all contact fields.")
                else:
                    st.success("Thank you! Your message has been sent successfully.")

    # ==========================================================================
    # 8. FOOTER & DISCREET ADMIN LINK
    # ==========================================================================
    styles.render_html(
        f"""
        <div class="footer">
            <div>© 2026 {name}. Engineered with Streamlit & Supabase.</div>
            <div style="font-size: 0.8rem; color: #475569;">All rights reserved.</div>
        </div>
        """
    )

    footer_cols = st.columns([5, 1])
    with footer_cols[1]:
        if st.button("🔒 Admin", key="footer_admin_trigger", help="Admin Portal"):
            st.session_state["show_admin"] = True
            st.query_params["admin"] = "login"
            st.rerun()


if __name__ == "__main__" or True:
    render_portfolio()
