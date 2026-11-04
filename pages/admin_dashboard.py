"""
Admin Control Center
Secure management panel for Profile (upsert id=1), Skills, Projects (with gallery),
Certifications, and CV upload (PDF, upsert id=1).
"""

import streamlit as st
from utils import auth, db, styles

# Block unauthenticated visitors immediately
auth.require_auth()


def render_dashboard():
    current_admin = auth.get_current_admin()

    # Header Bar
    header_col1, header_col2 = st.columns([3, 1])
    with header_col1:
        styles.render_html(
            f"""
            <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                <span class="admin-badge">Admin Dashboard</span>
                <h2 style="margin: 0; color: #FFFFFF;">Portfolio Control Center</h2>
            </div>
            <p style="color: #94A3B8; margin-top: -0.6rem;">Logged in as: <strong style="color: #93C5FD;">{current_admin}</strong></p>
            """
        )

    with header_col2:
        btn_c1, btn_c2 = st.columns(2)
        with btn_c1:
            if st.button("🌐 Live Preview"):
                st.query_params["view"] = "portfolio"
                st.rerun()
        with btn_c2:
            if st.button("🚪 Logout"):
                auth.logout_admin()
                st.query_params.clear()
                st.rerun()

    # 5 Management Tabs
    tab_about, tab_skills, tab_projects, tab_certs, tab_cv = st.tabs([
        "👤 About Me",
        "⚡ Skills",
        "🚀 Projects",
        "🎓 Certifications",
        "📄 CV / Resume"
    ])

    # ==========================================================================
    # TAB 1: ABOUT ME (UPSERT ID=1)
    # ==========================================================================
    with tab_about:
        st.subheader("Manage About Me (Profile: upsert id=1)")
        # In admin mode: returns real DB record or empty dict if DB is empty
        profile = db.get_profile(for_admin=True)

        col_photo, col_fields = st.columns([1, 2])
        current_photo = profile.get("photo_url", "")

        with col_photo:
            st.markdown("**Profile Photo**")
            if current_photo:
                st.image(current_photo, width=160)
            else:
                st.info("No profile photo configured.")

            uploaded_photo = st.file_uploader(
                "Upload Photo (JPG, PNG, WEBP)",
                type=["jpg", "jpeg", "png", "webp"],
                key="admin_photo_upload"
            )
            photo_url_val = current_photo
            if uploaded_photo:
                val_ok, val_err = db.validate_image_file(uploaded_photo)
                if not val_ok:
                    st.error(val_err)
                else:
                    if st.button("Upload to 'images' Bucket 📤", key="btn_upload_photo"):
                        with st.spinner("Uploading to Supabase Storage..."):
                            up_ok, up_res = db.upload_asset_file(uploaded_photo, bucket_name="images")
                            if up_ok:
                                st.session_state["temp_uploaded_photo"] = up_res
                                st.success("Photo uploaded successfully! Save profile to confirm.")
                                photo_url_val = up_res
                                st.rerun()
                            else:
                                st.error(up_res)

            # Use recently uploaded photo if exists in session
            if "temp_uploaded_photo" in st.session_state:
                photo_url_val = st.session_state["temp_uploaded_photo"]

        with col_fields:
            with st.form("form_profile_upsert"):
                f_name = st.text_input("Full Name *", value=profile.get("name", ""), placeholder="e.g. Alex Rivers")
                f_tagline = st.text_input("Tagline / Headline *", value=profile.get("tagline", ""), placeholder="e.g. Senior Software Architect")
                f_bio = st.text_area("Biography / Bio *", value=profile.get("bio", ""), height=130, placeholder="Brief narrative about your technical background...")
                f_email = st.text_input("Contact Email", value=profile.get("email", ""), placeholder="you@example.com")
                
                c_soc1, c_soc2 = st.columns(2)
                with c_soc1:
                    f_github = st.text_input("GitHub URL", value=profile.get("github", ""), placeholder="https://github.com/yourhandle")
                with c_soc2:
                    f_linkedin = st.text_input("LinkedIn URL", value=profile.get("linkedin", ""), placeholder="https://linkedin.com/in/yourhandle")

                f_photo_url = st.text_input("Profile Photo URL", value=photo_url_val, placeholder="https://... or uploaded above")

                submit_profile = st.form_submit_button("Save Profile (Upsert id=1) 💾", type="primary")

                if submit_profile:
                    if not f_name or not f_tagline or not f_bio:
                        st.error("Please fill in Name, Tagline, and Bio.")
                    else:
                        with st.spinner("Saving to Supabase..."):
                            ok, msg = db.upsert_profile(
                                name=f_name,
                                tagline=f_tagline,
                                bio=f_bio,
                                photo_url=f_photo_url,
                                email=f_email,
                                github=f_github,
                                linkedin=f_linkedin
                            )
                            if ok:
                                st.session_state.pop("temp_uploaded_photo", None)
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)

    # ==========================================================================
    # TAB 2: SKILLS (ADD / EDIT / DELETE)
    # ==========================================================================
    with tab_skills:
        st.subheader("Manage Skills")
        s_tab_add, s_tab_edit = st.tabs(["➕ Add Skill", "📝 Edit / Delete Skill"])

        # Add Skill Form
        with s_tab_add:
            with st.form("form_add_skill", clear_on_submit=True):
                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    new_s_name = st.text_input("Skill Name *", placeholder="e.g. Python, Docker, React")
                    new_s_cat = st.selectbox("Category *", ["Backend & APIs", "Frontend & UI", "Cloud & DevOps", "AI & Machine Learning", "Databases", "Tools & Systems"])
                with col_s2:
                    new_s_lvl = st.slider("Proficiency Level (%)", min_value=1, max_value=100, value=85)

                btn_add_skill = st.form_submit_button("Save Skill to Supabase ➕", type="primary")
                if btn_add_skill:
                    if not new_s_name:
                        st.error("Please enter a skill name.")
                    else:
                        with st.spinner("Saving skill..."):
                            ok, msg = db.add_skill(name=new_s_name, category=new_s_cat, level=new_s_lvl)
                            if ok:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)

        # Edit / Delete Skill Form
        with s_tab_edit:
            current_skills = db.get_skills(for_admin=True)
            if not current_skills:
                st.info("No skills found in database yet. Fill in the 'Add Skill' form above.")
            else:
                skill_map = {f"{s.get('name')} ({s.get('category')}) - Level: {s.get('level')}% [ID: {s.get('id')}]": s for s in current_skills}
                chosen_skill_key = st.selectbox("Select Skill to Edit or Delete", list(skill_map.keys()))
                chosen_skill = skill_map[chosen_skill_key]
                skill_id = chosen_skill.get("id")

                with st.form("form_edit_skill"):
                    e_s_name = st.text_input("Skill Name", value=chosen_skill.get("name", ""))
                    e_s_cat = st.text_input("Category", value=chosen_skill.get("category", ""))
                    e_s_lvl = st.slider("Level (%)", 1, 100, int(chosen_skill.get("level", 80)))

                    btn_update_skill = st.form_submit_button("Update Skill 💾", type="primary")
                    if btn_update_skill:
                        with st.spinner("Updating skill..."):
                            ok, msg = db.update_skill(skill_id=skill_id, name=e_s_name, category=e_s_cat, level=e_s_lvl)
                            if ok:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)

                if st.button("🗑️ Delete This Skill", type="secondary", key=f"del_sk_{skill_id}"):
                    with st.spinner("Deleting skill..."):
                        ok, msg = db.delete_skill(skill_id)
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)

    # ==========================================================================
    # TAB 3: PROJECTS (ADD / EDIT / DELETE & COVER / GALLERY UPLOADS)
    # ==========================================================================
    with tab_projects:
        st.subheader("Manage Projects & Gallery")
        p_tab_add, p_tab_edit = st.tabs(["➕ Add Project", "📝 Edit / Delete Project & Gallery"])

        # Add Project Form
        with p_tab_add:
            with st.form("form_add_project"):
                np_title = st.text_input("Project Title *", placeholder="e.g. Distributed Telemetry Pipeline")
                np_desc = st.text_area("Full Description *", height=120, placeholder="Detailed architecture and outcomes...")
                np_tech = st.text_input("Tech Stack *", placeholder="e.g. Python, FastAPI, Supabase, Redis")
                
                c_p1, c_p2 = st.columns(2)
                with c_p1:
                    np_live = st.text_input("Live Demo URL", placeholder="https://...")
                with c_p2:
                    np_gh = st.text_input("GitHub URL", placeholder="https://github.com/...")

                np_cover = st.text_input("Cover Image URL (Direct link or upload in Edit tab)", placeholder="https://images.unsplash.com/...")

                btn_add_proj = st.form_submit_button("Save Project to Supabase 🚀", type="primary")
                if btn_add_proj:
                    if not np_title or not np_desc or not np_tech:
                        st.error("Please fill in Title, Description, and Tech Stack.")
                    else:
                        with st.spinner("Saving project..."):
                            ok, msg, new_id = db.add_project(
                                title=np_title,
                                description=np_desc,
                                tech=np_tech,
                                cover_url=np_cover,
                                live_url=np_live,
                                github_url=np_gh
                            )
                            if ok:
                                st.success(f"{msg} You can now upload cover and gallery images in the Edit tab.")
                                st.rerun()
                            else:
                                st.error(msg)

        # Edit / Delete Project Form
        with p_tab_edit:
            current_projects = db.get_projects(for_admin=True)
            if not current_projects:
                st.info("No projects found in database yet. Add your first project in the 'Add Project' tab.")
            else:
                proj_map = {f"{p.get('title')} [ID: {p.get('id')}]": p for p in current_projects}
                chosen_proj_key = st.selectbox("Select Project to Manage", list(proj_map.keys()))
                chosen_proj = proj_map[chosen_proj_key]
                p_id = chosen_proj.get("id")

                # Project Details Form
                with st.form("form_edit_project"):
                    ep_title = st.text_input("Title", value=chosen_proj.get("title", ""))
                    ep_desc = st.text_area("Description", value=chosen_proj.get("description", ""), height=130)
                    ep_tech = st.text_input("Tech Stack", value=chosen_proj.get("tech", ""))
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        ep_live = st.text_input("Live URL", value=chosen_proj.get("live_url", ""))
                    with c2:
                        ep_gh = st.text_input("GitHub URL", value=chosen_proj.get("github_url", ""))

                    ep_cover = st.text_input("Cover Image URL", value=chosen_proj.get("cover_url", ""))

                    btn_upd_proj = st.form_submit_button("Update Project Details 💾", type="primary")
                    if btn_upd_proj:
                        with st.spinner("Updating project..."):
                            ok, msg = db.update_project(
                                project_id=p_id,
                                title=ep_title,
                                description=ep_desc,
                                tech=ep_tech,
                                cover_url=ep_cover,
                                live_url=ep_live,
                                github_url=ep_gh
                            )
                            if ok:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)

                # Cover Image Upload to 'images' bucket
                with st.expander("🖼️ Upload Cover Image to 'images' Bucket"):
                    proj_cover_file = st.file_uploader(
                        "Upload Cover (JPG, PNG, WEBP)",
                        type=["jpg", "png", "jpeg", "webp"],
                        key=f"cover_upload_{p_id}"
                    )
                    if proj_cover_file:
                        v_ok, v_err = db.validate_image_file(proj_cover_file)
                        if not v_ok:
                            st.error(v_err)
                        else:
                            if st.button("Upload & Attach as Cover 📤", key=f"btn_cov_{p_id}"):
                                with st.spinner("Uploading cover to Supabase Storage bucket 'images'..."):
                                    up_ok, cov_url = db.upload_asset_file(proj_cover_file, bucket_name="images")
                                    if up_ok:
                                        db.update_project(
                                            project_id=p_id,
                                            title=chosen_proj.get("title"),
                                            description=chosen_proj.get("description"),
                                            tech=chosen_proj.get("tech"),
                                            cover_url=cov_url,
                                            live_url=chosen_proj.get("live_url"),
                                            github_url=chosen_proj.get("github_url")
                                        )
                                        st.success(f"Cover image uploaded and updated! URL: {cov_url}")
                                        st.rerun()
                                    else:
                                        st.error(cov_url)

                # Multi-Image Gallery Upload to 'images' bucket
                with st.expander("📸 Project Gallery Uploads"):
                    gallery = db.get_project_images(p_id)
                    if gallery:
                        st.markdown("**Current Gallery Screenshots**")
                        g_cols = st.columns(len(gallery) if len(gallery) <= 3 else 3)
                        for g_idx, g_item in enumerate(gallery):
                            with g_cols[g_idx % 3]:
                                st.image(g_item.get("image_url"), width=180)
                                if st.button("🗑️ Remove", key=f"del_g_{g_item.get('id')}"):
                                    db.delete_project_image(g_item.get("id"))
                                    st.success("Gallery image removed.")
                                    st.rerun()
                    else:
                        st.caption("No gallery images attached to this project yet.")

                    gallery_file = st.file_uploader(
                        "Upload New Screenshot (JPG, PNG, WEBP)",
                        type=["jpg", "png", "jpeg", "webp"],
                        key=f"gallery_uploader_{p_id}"
                    )
                    if gallery_file:
                        gv_ok, gv_err = db.validate_image_file(gallery_file)
                        if not gv_ok:
                            st.error(gv_err)
                        else:
                            if st.button("Upload to 'images' Bucket & Add to Gallery ➕", key=f"btn_g_add_{p_id}"):
                                with st.spinner("Uploading screenshot to Supabase Storage 'images'..."):
                                    up_ok, g_img_url = db.upload_asset_file(gallery_file, bucket_name="images")
                                    if up_ok:
                                        ok, msg = db.add_project_image(p_id, g_img_url)
                                        if ok:
                                            st.success("Screenshot added to project gallery!")
                                            st.rerun()
                                        else:
                                            st.error(msg)
                                    else:
                                        st.error(g_img_url)

                # Delete Project
                st.divider()
                if st.button("🗑️ Delete Entire Project", type="secondary", key=f"del_proj_{p_id}"):
                    with st.spinner("Deleting project..."):
                        ok, msg = db.delete_project(p_id)
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)

    # ==========================================================================
    # TAB 4: CERTIFICATIONS (ADD / EDIT / DELETE & FILE UPLOADS)
    # ==========================================================================
    with tab_certs:
        st.subheader("Manage Certifications")
        c_tab_add, c_tab_edit = st.tabs(["➕ Add Certification", "📝 Edit / Delete Certification"])

        # Add Certification Form
        with c_tab_add:
            with st.form("form_add_cert"):
                nc_title = st.text_input("Certification Title *", placeholder="e.g. AWS Certified Solutions Architect")
                nc_issuer = st.text_input("Issuing Organization *", placeholder="e.g. Amazon Web Services (AWS)")
                nc_cred = st.text_input("Credential Verification URL", placeholder="https://aws.amazon.com/...")
                nc_file = st.text_input("Credential Asset / File URL (Direct link or upload in Edit tab)")

                btn_add_cert = st.form_submit_button("Save Certification to Supabase ➕", type="primary")
                if btn_add_cert:
                    if not nc_title or not nc_issuer:
                        st.error("Please fill in Title and Issuer.")
                    else:
                        with st.spinner("Saving certification..."):
                            ok, msg = db.add_certification(
                                title=nc_title,
                                issuer=nc_issuer,
                                credential_url=nc_cred,
                                file_url=nc_file
                            )
                            if ok:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)

        # Edit / Delete Certification Form
        with c_tab_edit:
            current_certs = db.get_certifications(for_admin=True)
            if not current_certs:
                st.info("No certifications found in database yet. Add your first certification in the 'Add Certification' tab.")
            else:
                cert_map = {f"{c.get('title')} - {c.get('issuer')} [ID: {c.get('id')}]": c for c in current_certs}
                chosen_cert_key = st.selectbox("Select Certification to Manage", list(cert_map.keys()))
                chosen_cert = cert_map[chosen_cert_key]
                cert_id = chosen_cert.get("id")

                with st.form("form_edit_cert"):
                    ec_title = st.text_input("Title", value=chosen_cert.get("title", ""))
                    ec_issuer = st.text_input("Issuer", value=chosen_cert.get("issuer", ""))
                    ec_cred = st.text_input("Credential URL", value=chosen_cert.get("credential_url", ""))
                    ec_file = st.text_input("File URL", value=chosen_cert.get("file_url", ""))

                    btn_upd_cert = st.form_submit_button("Update Certification 💾", type="primary")
                    if btn_upd_cert:
                        with st.spinner("Updating certification..."):
                            ok, msg = db.update_certification(
                                cert_id=cert_id,
                                title=ec_title,
                                issuer=ec_issuer,
                                credential_url=ec_cred,
                                file_url=ec_file
                            )
                            if ok:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)

                # Upload Image / PDF for this certificate
                with st.expander("📤 Upload Certificate Asset (Image or PDF)"):
                    cert_file = st.file_uploader(
                        "Upload Badge or Certificate (JPG, PNG, PDF)",
                        type=["jpg", "png", "jpeg", "webp", "pdf"],
                        key=f"cert_upload_{cert_id}"
                    )
                    if cert_file:
                        is_pdf = cert_file.name.lower().endswith(".pdf")
                        val_ok, val_err = db.validate_pdf_file(cert_file) if is_pdf else db.validate_image_file(cert_file)
                        if not val_ok:
                            st.error(val_err)
                        else:
                            bucket_target = "documents" if is_pdf else "images"
                            if st.button("Upload to Bucket & Save to Certification 📤", key=f"btn_c_up_{cert_id}"):
                                with st.spinner(f"Uploading to Supabase Storage '{bucket_target}'..."):
                                    up_ok, pub_url = db.upload_asset_file(cert_file, bucket_name=bucket_target)
                                    if up_ok:
                                        db.update_certification(
                                            cert_id=cert_id,
                                            title=chosen_cert.get("title"),
                                            issuer=chosen_cert.get("issuer"),
                                            credential_url=chosen_cert.get("credential_url"),
                                            file_url=pub_url
                                        )
                                        st.success(f"Certificate asset uploaded and attached! URL: {pub_url}")
                                        st.rerun()
                                    else:
                                        st.error(pub_url)

                st.divider()
                if st.button("🗑️ Delete Certification", type="secondary", key=f"del_c_{cert_id}"):
                    with st.spinner("Deleting certification..."):
                        ok, msg = db.delete_certification(cert_id)
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)

    # ==========================================================================
    # TAB 5: CV / RESUME UPLOAD (PDF, UPSERT ID=1)
    # ==========================================================================
    with tab_cv:
        st.subheader("Manage Curriculum Vitae (PDF, upsert id=1)")
        active_cv = db.get_active_cv(for_admin=True)

        col_cv_info, col_cv_upload = st.columns([1, 1])

        with col_cv_info:
            st.markdown("#### Current Published CV")
            if active_cv and active_cv.get("file_url"):
                st.markdown(f"**Published File URL:** `{active_cv.get('file_url')}`")
                st.link_button("Download / Preview Current CV 📥", active_cv.get("file_url"))
            else:
                st.info("No CV document published in database yet.")

        with col_cv_upload:
            st.markdown("#### Upload & Publish New CV (PDF)")
            st.caption("Uploaded PDF will be saved to the 'documents' bucket and upserted with id=1.")

            cv_pdf_file = st.file_uploader(
                "Upload Resume PDF Document (Max 10MB)",
                type=["pdf"],
                key="admin_cv_pdf_uploader"
            )

            if cv_pdf_file:
                is_valid_pdf, pdf_err = db.validate_pdf_file(cv_pdf_file)
                if not is_valid_pdf:
                    st.error(pdf_err)
                else:
                    st.success("Valid PDF document ready for upload.")
                    if st.button("Publish CV to 'documents' Bucket (Upsert id=1) 📄", type="primary"):
                        with st.spinner("Uploading to Supabase Storage 'documents' bucket..."):
                            up_ok, public_pdf_url = db.upload_asset_file(cv_pdf_file, bucket_name="documents")
                            if up_ok:
                                # Requirement 2: upsert id=1
                                db_ok, db_msg = db.upsert_cv(public_pdf_url)
                                if db_ok:
                                    st.success(db_msg)
                                    st.rerun()
                                else:
                                    st.error(db_msg)
                            else:
                                st.error(public_pdf_url)


if __name__ == "__main__" or True:
    render_dashboard()
