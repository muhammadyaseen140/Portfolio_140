"""
Modern Custom CSS and Styling System for Personal Portfolio
Designed for responsive layout, sleek typography, card hover animations, and dark/light friendliness.
"""

import textwrap
import streamlit as st


def render_html(html_str: str):
    """
    Renders HTML safely and reliably without markdown code-block interception.
    Uses st.html (Streamlit >= 1.34) or fallback to textwrap.dedent + st.markdown.
    """
    cleaned = textwrap.dedent(html_str).strip()
    if hasattr(st, "html"):
        st.html(cleaned)
    else:
        st.markdown(cleaned, unsafe_allow_html=True)


def get_custom_css() -> str:
    return """
    <style>
    /* Google Fonts Import */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    :root {
        --primary: #3B82F6;
        --primary-hover: #2563EB;
        --primary-glow: rgba(59, 130, 246, 0.25);
        --accent-purple: #8B5CF6;
        --bg-card: rgba(30, 41, 59, 0.7);
        --bg-card-hover: rgba(30, 41, 59, 0.95);
        --border-card: rgba(148, 163, 184, 0.12);
        --border-highlight: rgba(96, 165, 250, 0.35);
        --text-main: #F8FAFC;
        --text-muted: #94A3B8;
        --badge-bg: rgba(59, 130, 246, 0.15);
        --badge-text: #93C5FD;
    }

    /* Global typography */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    code, pre {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Hide Streamlit top header bar */
    header[data-testid="stHeader"] {
        display: none;
    }
    
    /* Main container padding */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 4rem !important;
        max-width: 1120px !important;
    }

    /* Hero Section */
    .hero-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        padding: 3rem 1.5rem 2rem 1.5rem;
        background: radial-gradient(circle at 50% 20%, rgba(59, 130, 246, 0.15) 0%, rgba(15, 23, 42, 0) 70%);
        border-radius: 24px;
        margin-bottom: 3rem;
        border: 1px solid var(--border-card);
    }

    .hero-avatar {
        width: 140px;
        height: 140px;
        border-radius: 50%;
        object-fit: cover;
        border: 3px solid #3B82F6;
        box-shadow: 0 0 25px var(--primary-glow);
        margin-bottom: 1.5rem;
        transition: transform 0.3s ease;
    }
    .hero-avatar:hover {
        transform: scale(1.05);
    }

    .hero-name {
        font-size: 2.75rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, #FFFFFF 30%, #93C5FD 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero-tagline {
        font-size: 1.25rem;
        color: #94A3B8;
        font-weight: 500;
        max-width: 650px;
        line-height: 1.5;
        margin-bottom: 1.25rem;
    }

    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.35rem 0.9rem;
        background: rgba(16, 185, 129, 0.12);
        color: #34D399;
        border: 1px solid rgba(16, 185, 129, 0.25);
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 1.25rem;
    }

    .status-dot {
        width: 8px;
        height: 8px;
        background-color: #10B981;
        border-radius: 50%;
        box-shadow: 0 0 8px #10B981;
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0% { transform: scale(0.95); opacity: 0.7; }
        50% { transform: scale(1.15); opacity: 1; }
        100% { transform: scale(0.95); opacity: 0.7; }
    }

    .social-links {
        display: flex;
        gap: 0.8rem;
        flex-wrap: wrap;
        justify-content: center;
        margin-top: 1rem;
    }

    .social-btn {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.5rem 1rem;
        border-radius: 12px;
        background: rgba(255, 255, 255, 0.05);
        color: #E2E8F0 !important;
        text-decoration: none !important;
        font-size: 0.9rem;
        font-weight: 500;
        border: 1px solid var(--border-card);
        transition: all 0.2s ease;
    }
    .social-btn:hover {
        background: rgba(59, 130, 246, 0.15);
        border-color: #3B82F6;
        color: #FFFFFF !important;
        transform: translateY(-2px);
    }

    /* Section Headings */
    .section-header {
        margin-top: 3.5rem;
        margin-bottom: 2rem;
        text-align: left;
    }
    .section-title {
        font-size: 1.85rem;
        font-weight: 700;
        color: #F8FAFC;
        letter-spacing: -0.02em;
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }
    .section-subtitle {
        color: #94A3B8;
        font-size: 0.95rem;
        margin-top: 0.25rem;
    }

    /* Glass Cards */
    .glass-card {
        background: var(--bg-card);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid var(--border-card);
        border-radius: 18px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .glass-card:hover {
        border-color: var(--border-highlight);
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3), 0 0 15px var(--primary-glow);
        transform: translateY(-3px);
    }

    /* Project Cards */
    .project-card {
        background: var(--bg-card);
        border: 1px solid var(--border-card);
        border-radius: 18px;
        overflow: hidden;
        margin-bottom: 2rem;
        display: flex;
        flex-direction: column;
        transition: all 0.3s ease;
        height: 100%;
    }
    .project-card:hover {
        border-color: var(--border-highlight);
        transform: translateY(-4px);
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.4);
    }
    .project-img {
        width: 100%;
        height: 200px;
        object-fit: cover;
        border-bottom: 1px solid var(--border-card);
    }
    .project-body {
        padding: 1.3rem;
        display: flex;
        flex-direction: column;
        flex-grow: 1;
    }
    .project-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #FFFFFF;
        margin-bottom: 0.4rem;
    }
    .project-tagline {
        font-size: 0.9rem;
        color: #94A3B8;
        margin-bottom: 0.8rem;
        line-height: 1.4;
    }
    .tech-pill {
        display: inline-block;
        font-size: 0.75rem;
        font-weight: 600;
        background: var(--badge-bg);
        color: var(--badge-text);
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        margin-right: 0.4rem;
        margin-bottom: 0.4rem;
        border: 1px solid rgba(96, 165, 250, 0.2);
    }
    .project-links {
        display: flex;
        gap: 0.8rem;
        margin-top: auto;
        padding-top: 1rem;
    }
    .project-btn {
        flex: 1;
        text-align: center;
        padding: 0.5rem 0.8rem;
        font-size: 0.85rem;
        font-weight: 600;
        border-radius: 10px;
        text-decoration: none !important;
        transition: all 0.2s;
    }
    .project-btn-primary {
        background: #2563EB;
        color: #FFFFFF !important;
    }
    .project-btn-primary:hover {
        background: #1D4ED8;
    }
    .project-btn-secondary {
        background: rgba(255, 255, 255, 0.08);
        color: #E2E8F0 !important;
        border: 1px solid var(--border-card);
    }
    .project-btn-secondary:hover {
        background: rgba(255, 255, 255, 0.15);
    }

    /* Skills Progress Bars */
    .skill-item {
        margin-bottom: 1.2rem;
    }
    .skill-meta {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.4rem;
        font-size: 0.9rem;
        font-weight: 600;
        color: #E2E8F0;
    }
    .skill-bar-bg {
        width: 100%;
        height: 8px;
        background: rgba(255, 255, 255, 0.08);
        border-radius: 9999px;
        overflow: hidden;
    }
    .skill-bar-fill {
        height: 100%;
        border-radius: 9999px;
        background: linear-gradient(90deg, #3B82F6 0%, #8B5CF6 100%);
        transition: width 1s ease-in-out;
    }

    /* Certifications */
    .cert-card {
        background: var(--bg-card);
        border: 1px solid var(--border-card);
        border-radius: 16px;
        padding: 1.2rem;
        margin-bottom: 1.2rem;
        display: flex;
        gap: 1.2rem;
        align-items: center;
        transition: all 0.2s ease;
    }
    .cert-card:hover {
        border-color: var(--border-highlight);
        transform: translateY(-2px);
    }
    .cert-badge {
        font-size: 1.8rem;
        width: 54px;
        height: 54px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(59, 130, 246, 0.12);
        border: 1px solid rgba(59, 130, 246, 0.25);
        border-radius: 12px;
        flex-shrink: 0;
    }
    .cert-title {
        font-weight: 700;
        font-size: 1.05rem;
        color: #F8FAFC;
    }
    .cert-issuer {
        font-size: 0.85rem;
        color: #94A3B8;
    }
    .cert-date {
        font-size: 0.8rem;
        color: #64748B;
    }

    /* CV Section */
    .cv-banner {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.9) 100%);
        border: 1px solid var(--border-highlight);
        border-radius: 20px;
        padding: 2.2rem;
        text-align: center;
        margin-top: 1rem;
        margin-bottom: 3rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    }

    /* Footer */
    .footer {
        margin-top: 5rem;
        padding-top: 2rem;
        border-top: 1px solid var(--border-card);
        text-align: center;
        color: #64748B;
        font-size: 0.85rem;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.5rem;
    }
    .admin-link {
        color: #475569 !important;
        text-decoration: none !important;
        font-size: 0.8rem;
        transition: color 0.2s;
    }
    .admin-link:hover {
        color: #94A3B8 !important;
    }

    /* Admin Management UI Enhancements */
    .admin-header {
        background: linear-gradient(135deg, rgba(37, 99, 235, 0.15) 0%, rgba(139, 92, 246, 0.1) 100%);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 16px;
        padding: 1.5rem 2rem;
        margin-bottom: 2rem;
    }
    .admin-badge {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        background: #DC2626;
        color: white;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Streamlit button tweaks */
    div.stButton > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button:hover {
        transform: translateY(-1px);
    }
    </style>
    """
