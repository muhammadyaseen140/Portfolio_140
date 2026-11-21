"""
Database & Supabase Storage Client
Handles read/write operations with Supabase Auth, caching, and conditional demo data.
"""

import os
import re
import uuid
import logging
from typing import Optional, List, Dict, Any
from PIL import Image
import streamlit as st

logger = logging.getLogger(__name__)

# Constants for file validation
MAX_IMAGE_SIZE_MB = 5
MAX_PDF_SIZE_MB = 10
ALLOWED_IMAGE_TYPES = {"image/png", "image/jpeg", "image/jpg", "image/webp"}
ALLOWED_PDF_TYPES = {"application/pdf"}


def get_supabase_credentials():
    """Extract Supabase credentials (URL and publishable/anon key) from st.secrets."""
    url = None
    key = None
    try:
        if "SUPABASE_URL" in st.secrets:
            url = str(st.secrets["SUPABASE_URL"]).strip()
        if "SUPABASE_KEY" in st.secrets:
            key = str(st.secrets["SUPABASE_KEY"]).strip()
    except Exception:
        pass
    return url, key


def get_supabase_client():
    """
    Initialize Supabase client per session.
    Maintains Supabase Auth session per visitor/admin.
    """
    url, anon_key = get_supabase_credentials()
    if not url or not anon_key:
        return None

    if "supabase_client" not in st.session_state:
        try:
            from supabase import create_client
            st.session_state["supabase_client"] = create_client(url, anon_key)
        except Exception as e:
            logger.error(f"Error creating Supabase client: {e}")
            return None

    client = st.session_state.get("supabase_client")
    # Ensure PostgREST and Storage carry the user's access token if authenticated
    token = st.session_state.get("admin_jwt_token")
    if client and token:
        try:
            client.postgrest.auth(token)
        except Exception:
            pass

    return client


def is_supabase_configured() -> bool:
    """Check if valid Supabase credentials exist."""
    url, anon_key = get_supabase_credentials()
    return bool(url and anon_key)


def clear_portfolio_cache():
    """Clear all cached queries after admin modifications."""
    st.cache_data.clear()


# ==============================================================================
# FILE VALIDATION & STORAGE OPERATIONS
# ==============================================================================

def validate_image_file(uploaded_file) -> tuple[bool, str]:
    """Validate uploaded image by size, MIME type, and binary integrity."""
    if uploaded_file is None:
        return False, "No file provided."

    file_size_mb = uploaded_file.size / (1024 * 1024)
    if file_size_mb > MAX_IMAGE_SIZE_MB:
        return False, f"Image size ({file_size_mb:.1f} MB) exceeds maximum allowed limit of {MAX_IMAGE_SIZE_MB} MB."

    if uploaded_file.type not in ALLOWED_IMAGE_TYPES:
        return False, f"Unsupported file type '{uploaded_file.type}'. Allowed: JPG, PNG, WEBP."

    try:
        uploaded_file.seek(0)
        img = Image.open(uploaded_file)
        img.verify()
        uploaded_file.seek(0)
    except Exception as e:
        return False, f"Invalid or corrupted image file: {e}"

    return True, "Valid image."


def validate_pdf_file(uploaded_file) -> tuple[bool, str]:
    """Validate uploaded PDF by size, MIME type, and magic bytes."""
    if uploaded_file is None:
        return False, "No file provided."

    file_size_mb = uploaded_file.size / (1024 * 1024)
    if file_size_mb > MAX_PDF_SIZE_MB:
        return False, f"PDF size ({file_size_mb:.1f} MB) exceeds maximum allowed limit of {MAX_PDF_SIZE_MB} MB."

    if uploaded_file.type not in ALLOWED_PDF_TYPES and not uploaded_file.name.lower().endswith(".pdf"):
        return False, "Uploaded file is not a valid PDF document."

    try:
        uploaded_file.seek(0)
        header = uploaded_file.read(5)
        uploaded_file.seek(0)
        if not header.startswith(b"%PDF"):
            return False, "The file does not appear to be a valid PDF format."
    except Exception as e:
        return False, f"Error validating PDF: {e}"

    return True, "Valid PDF document."


def upload_asset_file(uploaded_file, bucket_name: str = "images") -> tuple[bool, str]:
    """
    Upload a file to Supabase Storage bucket ('images' or 'documents').
    Uses the authenticated client session.
    """
    if uploaded_file is None:
        return False, "No file provided."

    client = get_supabase_client()
    if not client:
        return False, "Supabase client not initialized."

    clean_name = os.path.basename(uploaded_file.name).replace(" ", "_")
    unique_filename = f"{uuid.uuid4().hex[:8]}_{clean_name}"

    try:
        uploaded_file.seek(0)
        file_bytes = uploaded_file.read()
        uploaded_file.seek(0)

        # Upload to bucket
        client.storage.from_(bucket_name).upload(
            path=unique_filename,
            file=file_bytes,
            file_options={"content-type": uploaded_file.type, "upsert": "true"}
        )

        public_url = client.storage.from_(bucket_name).get_public_url(unique_filename)
        return True, public_url
    except Exception as e:
        err_msg = str(e)
        logger.error(f"Storage upload error: {err_msg}")
        return False, f"Upload error: {err_msg}"


# ==============================================================================
# DATA ACCESS FUNCTIONS
# ==============================================================================

def get_profile(for_admin: bool = False) -> Dict[str, Any]:
    """
    Retrieve profile details from Supabase.
    """
    client = get_supabase_client()
    if client:
        try:
            res = client.table("profile").select("*").limit(1).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
        except Exception as e:
            logger.error(f"Error reading profile from Supabase: {e}")

    if for_admin or bool(st.session_state.get("admin_user")):
        return {}
    return {
        "id": 1,
        "name": "Muhammad Yaseen",
        "tagline": "Automation Engineer",
        "bio": "",
        "photo_url": "",
        "email": "",
        "github": "",
        "linkedin": "",
        "location": "",
        "specialization": ""
    }


def get_skills(for_admin: bool = False) -> List[Dict[str, Any]]:
    """Retrieve categorized skills from database."""
    client = get_supabase_client()
    if client:
        try:
            res = client.table("skills").select("*").execute()
            if res.data is not None and len(res.data) > 0:
                return res.data
        except Exception as e:
            logger.error(f"Error reading skills from Supabase: {e}")

    return []


def get_projects(for_admin: bool = False) -> List[Dict[str, Any]]:
    """Retrieve all projects from database."""
    client = get_supabase_client()
    if client:
        try:
            res = client.table("projects").select("*").execute()
            if res.data is not None and len(res.data) > 0:
                return res.data
        except Exception as e:
            logger.error(f"Error reading projects from Supabase: {e}")

    return []


def get_project_images(project_id) -> List[Dict[str, Any]]:
    """Retrieve gallery images for a specific project."""
    client = get_supabase_client()
    if client:
        try:
            res = client.table("project_images").select("*").eq("project_id", project_id).execute()
            if res.data is not None:
                return res.data
        except Exception as e:
            logger.error(f"Error reading project images: {e}")

    return []


def get_certifications(for_admin: bool = False) -> List[Dict[str, Any]]:
    """Retrieve all certifications from database."""
    client = get_supabase_client()
    if client:
        try:
            res = client.table("certifications").select("*").execute()
            if res.data is not None and len(res.data) > 0:
                return res.data
        except Exception as e:
            logger.error(f"Error reading certifications: {e}")

    return []


def get_active_cv(for_admin: bool = False) -> Optional[Dict[str, Any]]:
    """Retrieve the currently active CV from database."""
    client = get_supabase_client()
    if client:
        try:
            res = client.table("cv").select("*").limit(1).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
        except Exception as e:
            logger.error(f"Error reading CV: {e}")

    return None


def get_contact(for_admin: bool = False) -> Dict[str, Any]:
    """Retrieve contact details (email, phone, location) from Supabase."""
    client = get_supabase_client()
    if client:
        try:
            res = client.table("contact").select("*").eq("id", 1).limit(1).execute()
            if res.data and len(res.data) > 0:
                row = res.data[0]
                return {
                    "id": row.get("id", 1),
                    "email": row.get("email") or "",
                    "phone": row.get("phone") or "",
                    "location": row.get("location") or ""
                }
        except Exception as e:
            logger.warning(f"Note on contact table read: {e}")

        # Fallback to profile table if contact table not yet created or empty
        try:
            p_res = client.table("profile").select("*").eq("id", 1).limit(1).execute()
            if p_res.data and len(p_res.data) > 0:
                p_row = p_res.data[0]
                return {
                    "id": 1,
                    "email": p_row.get("email") or "",
                    "phone": p_row.get("phone") or "",
                    "location": p_row.get("location") or ""
                }
        except Exception:
            pass

    return {}


def sort_experiences_newest_first(experiences: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Sort experiences with current jobs first, then newest dates/records first."""
    def extract_year(date_str: str) -> int:
        if not date_str:
            return 0
        matches = re.findall(r'\b(19\d\d|20\d\d)\b', str(date_str))
        if matches:
            return int(matches[-1])
        return 0

    def sort_key(item):
        is_curr = 1 if item.get("is_current") else 0
        end_yr = extract_year(item.get("end_date", ""))
        start_yr = extract_year(item.get("start_date", ""))
        yr = max(end_yr, start_yr)
        created = str(item.get("created_at") or "")
        return (is_curr, yr, str(item.get("start_date") or ""), created)

    return sorted(experiences, key=sort_key, reverse=True)


def get_experiences(for_admin: bool = False) -> List[Dict[str, Any]]:
    """Retrieve all experience records from database, sorted newest first."""
    client = get_supabase_client()
    if client:
        try:
            res = client.table("experience").select("*").order("created_at", desc=True).execute()
            if res.data is not None:
                return sort_experiences_newest_first(res.data)
        except Exception as e:
            logger.warning(f"Note on experience table read: {e}")

    return []


# ==============================================================================
# MUTATION FUNCTIONS (ADMIN ONLY - REAL SUPABASE SAVES WITH RLS)
# ==============================================================================

def upsert_profile(name: str, tagline: str, bio: str, photo_url: str = "",
                   email: str = "", github: str = "", linkedin: str = "",
                   specialization: str = "") -> tuple[bool, str]:
    """
    Requirement 2: About Me (upsert id=1).
    Saves to Supabase profile table with primary key id=1.
    """
    client = get_supabase_client()
    if not client:
        return False, "Supabase client not configured."

    payload = {
        "id": 1,
        "name": name.strip(),
        "tagline": tagline.strip(),
        "bio": bio.strip(),
        "photo_url": photo_url.strip(),
        "email": email.strip(),
        "github": github.strip(),
        "linkedin": linkedin.strip()
    }
    if specialization.strip():
        payload["specialization"] = specialization.strip()

    try:
        res = client.table("profile").upsert(payload).execute()
        clear_portfolio_cache()
        return True, "Profile saved successfully (upsert id=1)!"
    except Exception as e:
        err_msg = str(e)
        # If the specialization column is not yet added in Supabase schema:
        if "specialization" in err_msg.lower() and "column" in err_msg.lower():
            logger.warning("Supabase profile table missing 'specialization' column. Retrying without it.")
            payload.pop("specialization", None)
            try:
                client.table("profile").upsert(payload).execute()
                clear_portfolio_cache()
                return True, "Profile saved! (To persist Specialization, please run in Supabase SQL Editor: ALTER TABLE profile ADD COLUMN specialization TEXT;)"
            except Exception as e2:
                return False, f"Supabase error: {e2}"
        logger.error(f"Error upserting profile: {err_msg}")
        return False, f"Supabase error: {err_msg}"


def add_skill(name: str, category: str, level: int) -> tuple[bool, str]:
    """Add a new skill."""
    client = get_supabase_client()
    if not client:
        return False, "Supabase client not configured."

    payload = {
        "name": name.strip(),
        "category": category.strip(),
        "level": max(1, min(100, int(level)))
    }
    try:
        client.table("skills").insert(payload).execute()
        clear_portfolio_cache()
        return True, f"Skill '{name}' added successfully."
    except Exception as e:
        return False, f"Supabase error: {e}"


def update_skill(skill_id, name: str, category: str, level: int) -> tuple[bool, str]:
    """Update an existing skill."""
    client = get_supabase_client()
    if not client:
        return False, "Supabase client not configured."

    payload = {
        "name": name.strip(),
        "category": category.strip(),
        "level": max(1, min(100, int(level)))
    }
    try:
        client.table("skills").update(payload).eq("id", skill_id).execute()
        clear_portfolio_cache()
        return True, f"Skill '{name}' updated successfully."
    except Exception as e:
        return False, f"Supabase error: {e}"


def delete_skill(skill_id) -> tuple[bool, str]:
    """Delete a skill."""
    client = get_supabase_client()
    if not client:
        return False, "Supabase client not configured."

    try:
        client.table("skills").delete().eq("id", skill_id).execute()
        clear_portfolio_cache()
        return True, "Skill deleted successfully."
    except Exception as e:
        return False, f"Supabase error: {e}"


def add_project(title: str, description: str = "", tech: str = "",
                cover_url: str = "", live_url: str = "", github_url: str = "") -> tuple[bool, str, Optional[Any]]:
    """Create a new project."""
    client = get_supabase_client()
    if not client:
        return False, "Supabase client not configured.", None

    payload = {
        "title": title.strip(),
        "description": description.strip() if description else "",
        "tech": tech.strip() if tech else "",
        "cover_url": cover_url.strip() if cover_url else "",
        "live_url": live_url.strip() if live_url else "",
        "github_url": github_url.strip() if github_url else ""
    }
    try:
        res = client.table("projects").insert(payload).execute()
        clear_portfolio_cache()
        new_id = res.data[0]["id"] if res.data else None
        return True, f"Project '{title}' created successfully.", new_id
    except Exception as e:
        return False, f"Supabase error: {e}", None


def update_project(project_id, title: str, description: str = "", tech: str = "",
                   cover_url: str = "", live_url: str = "", github_url: str = "") -> tuple[bool, str]:
    """Update project details."""
    client = get_supabase_client()
    if not client:
        return False, "Supabase client not configured."

    payload = {
        "title": title.strip(),
        "description": description.strip() if description else "",
        "tech": tech.strip() if tech else "",
        "cover_url": cover_url.strip() if cover_url else "",
        "live_url": live_url.strip() if live_url else "",
        "github_url": github_url.strip() if github_url else ""
    }
    try:
        client.table("projects").update(payload).eq("id", project_id).execute()
        clear_portfolio_cache()
        return True, f"Project '{title}' updated successfully."
    except Exception as e:
        return False, f"Supabase error: {e}"


def delete_project(project_id) -> tuple[bool, str]:
    """Delete a project and its gallery records."""
    client = get_supabase_client()
    if not client:
        return False, "Supabase client not configured."

    try:
        # Delete gallery images first
        try:
            client.table("project_images").delete().eq("project_id", project_id).execute()
        except Exception:
            pass
        client.table("projects").delete().eq("id", project_id).execute()
        clear_portfolio_cache()
        return True, "Project deleted successfully."
    except Exception as e:
        return False, f"Supabase error: {e}"


def add_project_image(project_id, image_url: str) -> tuple[bool, str]:
    """Add a gallery image to a project."""
    client = get_supabase_client()
    if not client:
        return False, "Supabase client not configured."

    payload = {
        "project_id": project_id,
        "image_url": image_url.strip()
    }
    try:
        client.table("project_images").insert(payload).execute()
        clear_portfolio_cache()
        return True, "Gallery image added successfully."
    except Exception as e:
        return False, f"Supabase error: {e}"


def delete_project_image(image_id) -> tuple[bool, str]:
    """Delete a gallery image."""
    client = get_supabase_client()
    if not client:
        return False, "Supabase client not configured."

    try:
        client.table("project_images").delete().eq("id", image_id).execute()
        clear_portfolio_cache()
        return True, "Gallery image removed."
    except Exception as e:
        return False, f"Supabase error: {e}"


def add_certification(title: str, issuer: str, credential_url: str = "", file_url: str = "") -> tuple[bool, str]:
    """Create a certification."""
    client = get_supabase_client()
    if not client:
        return False, "Supabase client not configured."

    payload = {
        "title": title.strip(),
        "issuer": issuer.strip(),
        "credential_url": credential_url.strip(),
        "file_url": file_url.strip()
    }
    try:
        client.table("certifications").insert(payload).execute()
        clear_portfolio_cache()
        return True, f"Certification '{title}' added successfully."
    except Exception as e:
        return False, f"Supabase error: {e}"


def update_certification(cert_id, title: str, issuer: str, credential_url: str = "", file_url: str = "") -> tuple[bool, str]:
    """Update a certification."""
    client = get_supabase_client()
    if not client:
        return False, "Supabase client not configured."

    payload = {
        "title": title.strip(),
        "issuer": issuer.strip(),
        "credential_url": credential_url.strip(),
        "file_url": file_url.strip()
    }
    try:
        client.table("certifications").update(payload).eq("id", cert_id).execute()
        clear_portfolio_cache()
        return True, f"Certification '{title}' updated successfully."
    except Exception as e:
        return False, f"Supabase error: {e}"


def delete_certification(cert_id) -> tuple[bool, str]:
    """Delete a certification."""
    client = get_supabase_client()
    if not client:
        return False, "Supabase client not configured."

    try:
        client.table("certifications").delete().eq("id", cert_id).execute()
        clear_portfolio_cache()
        return True, "Certification deleted successfully."
    except Exception as e:
        return False, f"Supabase error: {e}"


def upsert_cv(file_url: str) -> tuple[bool, str]:
    """
    Requirement 2: CV upload (PDF, upsert id=1).
    Saves PDF URL to Supabase cv table with primary key id=1.
    """
    client = get_supabase_client()
    if not client:
        return False, "Supabase client not configured."

    payload = {
        "id": 1,
        "file_url": file_url.strip()
    }
    try:
        client.table("cv").upsert(payload).execute()
        clear_portfolio_cache()
        return True, "CV published successfully (upsert id=1)!"
    except Exception as e:
        return False, f"Supabase error: {e}"


def upsert_contact(email: str = "", phone: str = "", location: str = "") -> tuple[bool, str]:
    """
    Save contact details (email, phone, location) with upsert id=1.
    Saves to 'contact' table and updates profile email/location if available.
    """
    client = get_supabase_client()
    if not client:
        return False, "Supabase client not configured."

    payload = {
        "id": 1,
        "email": email.strip() if email else None,
        "phone": phone.strip() if phone else None,
        "location": location.strip() if location else None
    }
    try:
        client.table("contact").upsert(payload).execute()
        # Also sync to profile table if profile exists
        try:
            prof_payload = {"id": 1}
            if email.strip():
                prof_payload["email"] = email.strip()
            if location.strip():
                prof_payload["location"] = location.strip()
            client.table("profile").upsert(prof_payload).execute()
        except Exception:
            pass
        clear_portfolio_cache()
        st.cache_data.clear()
        return True, "Contact details saved successfully (upsert id=1)!"
    except Exception as e:
        err_msg = str(e)
        logger.error(f"Error upserting contact: {err_msg}")
        return False, f"Supabase error: {err_msg}"


def add_experience(job_title: str = "", job_type: str = "", company: str = "",
                   start_date: str = "", end_date: str = "", is_current: bool = False,
                   description: str = "") -> tuple[bool, str, Optional[Any]]:
    """Create a new experience record."""
    client = get_supabase_client()
    if not client:
        return False, "Supabase client not configured.", None

    payload = {
        "job_title": job_title.strip() if job_title else None,
        "job_type": job_type.strip() if job_type else None,
        "company": company.strip() if company else None,
        "start_date": start_date.strip() if start_date else None,
        "end_date": None if is_current else (end_date.strip() if end_date else None),
        "is_current": bool(is_current),
        "description": description.strip() if description else None
    }
    try:
        res = client.table("experience").insert(payload).execute()
        clear_portfolio_cache()
        st.cache_data.clear()
        new_id = res.data[0]["id"] if res.data else None
        return True, "Experience record added successfully.", new_id
    except Exception as e:
        err_msg = str(e)
        logger.error(f"Error adding experience: {err_msg}")
        return False, f"Supabase error: {err_msg}", None


def update_experience(exp_id, job_title: str = "", job_type: str = "", company: str = "",
                      start_date: str = "", end_date: str = "", is_current: bool = False,
                      description: str = "") -> tuple[bool, str]:
    """Update an existing experience record."""
    client = get_supabase_client()
    if not client:
        return False, "Supabase client not configured."

    payload = {
        "job_title": job_title.strip() if job_title else None,
        "job_type": job_type.strip() if job_type else None,
        "company": company.strip() if company else None,
        "start_date": start_date.strip() if start_date else None,
        "end_date": None if is_current else (end_date.strip() if end_date else None),
        "is_current": bool(is_current),
        "description": description.strip() if description else None
    }
    try:
        client.table("experience").update(payload).eq("id", exp_id).execute()
        clear_portfolio_cache()
        st.cache_data.clear()
        return True, "Experience record updated successfully."
    except Exception as e:
        err_msg = str(e)
        logger.error(f"Error updating experience: {err_msg}")
        return False, f"Supabase error: {err_msg}"


def delete_experience(exp_id) -> tuple[bool, str]:
    """Delete an experience record."""
    client = get_supabase_client()
    if not client:
        return False, "Supabase client not configured."

    try:
        client.table("experience").delete().eq("id", exp_id).execute()
        clear_portfolio_cache()
        st.cache_data.clear()
        return True, "Experience record deleted successfully."
    except Exception as e:
        err_msg = str(e)
        logger.error(f"Error deleting experience: {err_msg}")
        return False, f"Supabase error: {err_msg}"
