"""
Public Portfolio Page (Read-Only)
Displays hero, about, skills, projects, certifications, CV download/preview, and contact sections.
"""

import streamlit as st
import logging
from utils import db, styles

logger = logging.getLogger(__name__)


def render_portfolio():
    try:
        profile = db.get_profile(for_admin=False)
        contact = db.get_contact(for_admin=False)
        experiences = db.get_experiences(for_admin=False)
        skills = db.get_skills(for_admin=False)
        projects = db.get_projects(for_admin=False)
        certifications = db.get_certifications(for_admin=False)
        cv_doc = db.get_active_cv(for_admin=False)
    except Exception as e:
        logger.error(f"Error loading portfolio data: {e}")
        st.error("Unable to load portfolio details at this time. Please try again later.")
        return

    name = profile.get("name") or "Muhammad Yaseen"
    tagline = profile.get("tagline") or ""
    bio = profile.get("bio") or ""
    photo_url = profile.get("photo_url") or profile.get("avatar_url") or ""
    github_url = profile.get("github") or profile.get("github_url") or ""
    linkedin_url = profile.get("linkedin") or profile.get("linkedin_url") or ""
    specialization = profile.get("specialization") or ""

    # Contact details prioritize contact table, fallback to profile
    email = contact.get("email") or profile.get("email") or ""
    phone = contact.get("phone") or profile.get("phone") or ""
    location = contact.get("location") or profile.get("location") or ""

    # ==========================================================================
    # 1. HERO SECTION
    # ==========================================================================
    social_buttons = []
    if github_url:
        social_buttons.append(f'<a href="{github_url}" target="_blank" rel="noopener noreferrer" class="social-btn"><span>🐙</span> GitHub</a>')
    if linkedin_url:
        social_buttons.append(f'<a href="{linkedin_url}" target="_blank" rel="noopener noreferrer" class="social-btn"><span>💼</span> LinkedIn</a>')
    if email:
        social_buttons.append(f'<a href="mailto:{email}" class="social-btn"><span>✉️</span> Get in Touch</a>')

    social_buttons_html = f'<div class="social-links">{" ".join(social_buttons)}</div>' if social_buttons else ""
    avatar_html = f'<img src="{photo_url}" alt="{name}" class="hero-avatar" />' if photo_url else ''
    tagline_html = f'<p class="hero-tagline">{tagline}</p>' if tagline else ''
    location_html = f'<p style="color: #64748B; font-size: 0.9rem; margin-top: -0.5rem;">📍 {location}</p>' if location else ''

    hero_html = f"""
    <div class="hero-container">
        {avatar_html}
        <div class="status-badge">
            <span class="status-dot"></span>
            Available for Select Projects & Leadership Roles
        </div>
        <h1 class="hero-name">{name}</h1>
        {tagline_html}
        {location_html}
        {social_buttons_html}
    </div>
    """
    styles.render_html(hero_html)

    # Dynamic Sub-Navigation (only shows sections with actual data)
    nav_links = []
    if bio:
        nav_links.append('<a href="#about" class="subnav-link">About</a>')
    if experiences:
        nav_links.append('<a href="#experience" class="subnav-link">Experience</a>')
    if skills:
        nav_links.append('<a href="#skills" class="subnav-link">Skills</a>')
    if projects:
        nav_links.append('<a href="#projects" class="subnav-link">Projects</a>')
    if certifications:
        nav_links.append('<a href="#certifications" class="subnav-link">Certifications</a>')
    if cv_doc and cv_doc.get("file_url"):
        nav_links.append('<a href="#cv-resume" class="subnav-link">CV / Resume</a>')
    nav_links.append('<a href="#contact" class="subnav-link">Contact</a>')

    if len(nav_links) > 1:
        styles.render_html(f'<div class="subnav-bar">{" ".join(nav_links)}</div>')

    # ==========================================================================
    # 2. ABOUT ME SECTION (Rendered only when bio exists)
    # ==========================================================================
    if bio:
        # Section header — no hardcoded subtitle
        styles.render_html('<div id="about" class="section-header"><div class="section-title"><span>👤</span> About Me</div></div>')

        # Build bio HTML: convert newlines to paragraph tags for proper spacing
        bio_paragraphs = "".join(
            f"<p>{para.strip()}</p>"
            for para in bio.split("\n")
            if para.strip()
        )
        bio_html = f'<div class="about-bio-text">{bio_paragraphs}</div>'

        # Full-width bio container without Direct Contact card
        styles.render_html(f"""
        <div class="glass-card" style="width: 100%;">
            {bio_html}
        </div>
        """)

    # ==========================================================================
    # 3. EXPERIENCE SECTION (Rendered only when experiences exist)
    # ==========================================================================
    if experiences:
        styles.render_html('<div id="experience" class="section-header"><div class="section-title"><span>💼</span> Experience</div></div>')

        timeline_items = []
        for exp in experiences:
            job_title = exp.get("job_title", "").strip() if exp.get("job_title") else ""
            company = exp.get("company", "").strip() if exp.get("company") else ""
            job_type = exp.get("job_type", "").strip() if exp.get("job_type") else ""
            start_date = exp.get("start_date", "").strip() if exp.get("start_date") else ""
            end_date = exp.get("end_date", "").strip() if exp.get("end_date") else ""
            is_current = bool(exp.get("is_current"))
            description = exp.get("description", "").strip() if exp.get("description") else ""

            # Title & Company
            title_parts = []
            if job_title:
                title_parts.append(job_title)
            if company:
                title_parts.append(f'<span class="timeline-company">@ {company}</span>')
            title_html = f'<h4 class="timeline-title">{" ".join(title_parts)}</h4>' if title_parts else ""

            # Date formatting
            if is_current:
                date_text = f"{start_date} – Present" if start_date else "Present"
                current_badge = '<span class="status-badge" style="padding: 0.15rem 0.55rem; font-size: 0.75rem; margin: 0;"><span class="status-dot" style="width: 6px; height: 6px;"></span> Current</span>'
            elif start_date and end_date:
                date_text = f"{start_date} – {end_date}"
                current_badge = ""
            elif start_date:
                date_text = start_date
                current_badge = ""
            elif end_date:
                date_text = end_date
                current_badge = ""
            else:
                date_text = ""
                current_badge = ""

            meta_parts = []
            if date_text:
                meta_parts.append(f'<span class="timeline-date">🗓️ {date_text}</span>')
            if current_badge:
                meta_parts.append(current_badge)
            if job_type:
                meta_parts.append(f'<span class="tech-pill" style="margin: 0; font-size: 0.75rem;">{job_type}</span>')

            meta_html = f'<div class="timeline-meta">{" ".join(meta_parts)}</div>' if meta_parts else ""

            desc_html = ""
            if description:
                desc_paragraphs = "".join(
                    f"<p style='color: #CBD5E1; font-size: 0.95rem; line-height: 1.6; margin-top: 0.75rem; margin-bottom: 0;'>{p.strip()}</p>"
                    for p in description.split("\n")
                    if p.strip()
                )
                desc_html = f'<div class="timeline-desc">{desc_paragraphs}</div>'

            timeline_items.append(
                f"""
                <div class="timeline-item">
                    <div class="timeline-dot"></div>
                    <div class="timeline-card">
                        {title_html}
                        {meta_html}
                        {desc_html}
                    </div>
                </div>
                """
            )

        styles.render_html(
            f"""
            <div class="timeline-container">
                {''.join(timeline_items)}
            </div>
            """
        )

    # ==========================================================================
    # 3. SKILLS SECTION (Rendered only when skills exist)
    # ==========================================================================
    if skills:
        styles.render_html('<div id="skills" class="section-header"><div class="section-title"><span>⚡</span> Technical Skills</div><div class="section-subtitle">Categorized competencies and proficiency ratings</div></div>')

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
    # 4. PROJECTS SECTION (Rendered only when projects exist)
    # ==========================================================================
    if projects:
        styles.render_html('<div id="projects" class="section-header"><div class="section-title"><span>🚀</span> Featured Projects</div><div class="section-subtitle">Production platforms, applications, and tools</div></div>')

        p_cols = st.columns(2)
        for idx, proj in enumerate(projects):
            with p_cols[idx % 2]:
                pid = proj.get("id")
                title = proj.get("title", "")
                desc = proj.get("description", "")
                tech_stack = proj.get("tech") or proj.get("tech_stack", "")
                cover_url = proj.get("cover_url") or proj.get("cover_image_url") or ""
                live_url = proj.get("live_url", "")
                gh_url = proj.get("github_url", "")

                tech_pills_html = "".join(
                    [f'<span class="tech-pill">{t.strip()}</span>' for t in str(tech_stack).split(",") if t.strip()]
                )

                img_html = f'''<img src="{cover_url}" alt="{title}" class="project-img" onerror="this.style.display='none'" />''' if cover_url else ""

                styles.render_html(
                    f"""
                    <div class="project-card">
                        {img_html}
                        <div class="project-body">
                            <div class="project-title">{title}</div>
                            {f'<div style="margin-top: 0.5rem; margin-bottom: 1rem;">{tech_pills_html}</div>' if tech_pills_html else ''}
                        </div>
                    </div>
                    """
                )

                if live_url or gh_url:
                    if live_url and gh_url:
                        link_col1, link_col2 = st.columns(2)
                        with link_col1:
                            st.link_button("🌐 Live App", live_url)
                        with link_col2:
                            st.link_button("💻 GitHub", gh_url)
                    elif live_url:
                        st.link_button("🌐 Live App", live_url)
                    elif gh_url:
                        st.link_button("💻 GitHub", gh_url)

                gallery_images = db.get_project_images(pid)
                if desc or gallery_images:
                    with st.expander(f"📖 Project Details & Gallery: {title}", expanded=False):
                        if desc:
                            st.markdown("**Overview**")
                            st.write(desc)

                        if gallery_images:
                            st.markdown("**Project Gallery**")
                            g_cols = st.columns(len(gallery_images) if len(gallery_images) <= 3 else 3)
                            for g_idx, g_img in enumerate(gallery_images):
                                with g_cols[g_idx % 3]:
                                    st.image(
                                        g_img.get("image_url", ""),
                                        caption=f"{title} - Screenshot {g_idx+1}",
                                        width=240
                                    )

                styles.render_html("<div style='margin-bottom: 1.5rem;'></div>")

    # ==========================================================================
    # 5. CERTIFICATIONS SECTION (Rendered only when certifications exist)
    # ==========================================================================
    if certifications:
        styles.render_html('<div id="certifications" class="section-header"><div class="section-title"><span>🎓</span> Certifications & Credentials</div><div class="section-subtitle">Verified professional credentials and specializations</div></div>')

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

                if cred_url and file_url:
                    btn_col1, btn_col2 = st.columns(2)
                    with btn_col1:
                        st.link_button("Verify ↗", cred_url)
                    with btn_col2:
                        if file_url.lower().endswith(".pdf"):
                            st.link_button("View PDF 📄", file_url)
                        else:
                            with st.popover("Preview 🖼️"):
                                st.image(file_url, caption=f"{title} - {issuer}")
                elif cred_url:
                    st.link_button("Verify ↗", cred_url)
                elif file_url:
                    if file_url.lower().endswith(".pdf"):
                        st.link_button("View PDF 📄", file_url)
                    else:
                        with st.popover("Preview 🖼️"):
                            st.image(file_url, caption=f"{title} - {issuer}")

    # ==========================================================================
    # 6. CV & RESUME SECTION (Rendered only when CV file exists)
    # ==========================================================================
    if cv_doc and cv_doc.get("file_url"):
        cv_url = cv_doc.get("file_url", "")

        styles.render_html(
            """
            <div id="cv-resume" class="section-header">
                <div class="section-title"><span>📄</span> Curriculum Vitae</div>
                <div class="section-subtitle">Career history, accomplishments, and skills</div>
            </div>
            <div class="cv-banner">
                <h3 style="color: #F8FAFC; margin-bottom: 0.5rem; font-weight: 700;">Curriculum Vitae</h3>
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
                        st.iframe(cv_url, height=600)
                    else:
                        st.info("PDF preview available via download.")

    # ==========================================================================
    # 7. CONTACT SECTION
    # ==========================================================================
    # Section header — no hardcoded subtitle
    styles.render_html('<div id="contact" class="section-header"><div class="section-title"><span>📬</span> Contact & Inquiries</div></div>')

    contact_items = []
    if email:
        contact_items.append(f"""
        <div style="display: flex; align-items: center; gap: 0.75rem; color: #E2E8F0;">
            <span style="font-size: 1.1rem;">✉️</span>
            <a href="mailto:{email}" style="color: #60A5FA; text-decoration: none; word-break: break-all;">{email}</a>
        </div>
        """)
    if phone:
        contact_items.append(f"""
        <div style="display: flex; align-items: center; gap: 0.75rem; color: #E2E8F0;">
            <span style="font-size: 1.1rem;">📞</span>
            <a href="tel:{phone}" style="color: #60A5FA; text-decoration: none;">{phone}</a>
        </div>
        """)
    if location:
        contact_items.append(f"""
        <div style="display: flex; align-items: center; gap: 0.75rem; color: #E2E8F0;">
            <span style="font-size: 1.1rem;">📍</span>
            <span style="color: #CBD5E1;">{location}</span>
        </div>
        """)

    def render_contact_form():
        with st.form("contact_form", clear_on_submit=True):
            st.markdown("<h4 style='color: #F8FAFC; margin-bottom: 0.5rem;'>Send a Message</h4>", unsafe_allow_html=True)
            sender_name = st.text_input("Your Name", placeholder="Your Name")
            sender_email = st.text_input("Your Email", placeholder="you@example.com")
            message = st.text_area("Message", placeholder="Write your message here...")
            submitted = st.form_submit_button("Send Message 🚀")

            if submitted:
                if not sender_name or not sender_email or not message:
                    st.error("Please fill in all contact fields.")
                else:
                    st.success("Thank you! Your message has been sent successfully.")

    if contact_items:
        c_col1, c_col2 = st.columns([1, 1])
        with c_col1:
            styles.render_html(
                f"""
                <div class="glass-card" style="height: 100%;">
                    <h4 style="color: #F8FAFC; margin-bottom: 1.25rem; font-weight: 700;">Let's Connect</h4>
                    <div style="display: flex; flex-direction: column; gap: 1rem;">
                        {''.join(contact_items)}
                    </div>
                </div>
                """
            )
        with c_col2:
            render_contact_form()
    else:
        render_contact_form()

    # ==========================================================================
    # 8. FOOTER
    # ==========================================================================
    styles.render_html(
        """
        <div class="footer">
            <div>© 2026 Muhammad Yaseen. All rights reserved.</div>
        </div>
        """
    )


if __name__ == "__main__" or True:
    render_portfolio()
