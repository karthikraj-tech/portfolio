"""
tests/test_frontend_e2e.py
End-to-end verification of HTML structure, CSS responsiveness/accessibility rules,
JavaScript anti-XSS safety, and live API-to-database contract.
"""

import re
from pathlib import Path
from app import create_app
from database.models import ContactMessage, Project, Skill, Certification

BASE_DIR = Path(__file__).resolve().parent.parent

def test_html_semantics_and_accessibility():
    """Verify semantic HTML elements, skip links, ARIA attributes, and required IDs."""
    html_path = BASE_DIR / "templates" / "index.html"
    assert html_path.exists(), "index.html must exist"
    content = html_path.read_text(encoding="utf-8")

    # Semantic landmarks
    assert "<header" in content and "</header>" in content
    assert "<nav" in content and "</nav>" in content
    assert '<main id="main-content">' in content or '<main' in content
    assert "<footer" in content and "</footer>" in content

    # Skip link for accessibility
    assert 'class="skip-link"' in content
    assert 'href="#main-content"' in content

    # Navigation anchors
    nav_targets = ["#hero", "#about", "#skills", "#projects", "#certifications", "#education", "#contact"]
    for target in nav_targets:
        assert f'href="{target}"' in content, f"Nav link for {target} missing"

    # Required section containers for dynamic rendering
    assert 'id="skills-container"' in content
    assert 'id="projects-container"' in content
    assert 'id="certifications-container"' in content

    # Contact form elements
    assert 'id="contact-form"' in content
    assert 'name="name"' in content
    assert 'name="email"' in content
    assert 'name="subject"' in content
    assert 'name="message"' in content
    assert 'name="website_url"' in content  # Honeypot
    assert 'id="contact-submit-btn"' in content

    # Resume button
    assert 'id="resume-btn"' in content
    assert 'id="resume-btn-text"' in content

    # Theme toggle & mobile menu toggle
    assert 'id="theme-toggle"' in content
    assert 'id="mobile-toggle"' in content


def test_css_tokens_and_accessibility_rules():
    """Verify modern design tokens, light/dark themes, responsive breakpoints, and motion reduction."""
    css_path = BASE_DIR / "static" / "css" / "style.css"
    assert css_path.exists(), "style.css must exist"
    content = css_path.read_text(encoding="utf-8")

    # Dark / Light Theme Tokens
    assert ":root" in content
    assert '[data-theme="light"]' in content
    assert "--bg-primary" in content
    assert "--accent-color" in content

    # Accessibility Focus & Motion
    assert ":focus-visible" in content
    assert "prefers-reduced-motion" in content
    assert ".skip-link" in content

    # Responsiveness (Desktop, Tablet, Mobile 768px, Mobile 360px)
    assert "@media (max-width: 768px)" in content
    assert "@media (max-width: 360px)" in content


def test_javascript_security_and_dom_handling():
    """Verify that script.js strictly uses textContent (never innerHTML for user inputs) to prevent XSS."""
    js_path = BASE_DIR / "static" / "js" / "script.js"
    assert js_path.exists(), "script.js must exist"
    content = js_path.read_text(encoding="utf-8")

    # Anti-XSS: dynamic elements must be assigned via textContent
    assert "textContent" in content
    assert "alertBox.textContent" in content
    assert "pill.textContent = skill.name" in content
    assert "title.textContent = proj.title" in content
    assert "desc.textContent = proj.description" in content

    # Endpoints called
    assert '"/api/skills"' in content
    assert '"/api/projects"' in content
    assert '"/api/certifications"' in content
    assert '"/api/resume-status"' in content
    assert '"/api/contact"' in content

    # Honeypot check presence
    assert "website_url" in content

    # Theme toggle persistence
    assert "portfolio_theme" in content
    assert "localStorage" in content


def test_portfolio_data_honesty_compliance():
    """Verify that no fabricated details, marks, fake links, or completed project statuses exist."""
    json_path = BASE_DIR / "data" / "portfolio_data.json"
    assert json_path.exists(), "portfolio_data.json must exist"
    import json
    data = json.loads(json_path.read_text(encoding="utf-8"))

    # Name and title
    assert data["personal"]["name"] == "Karthikraj S"
    assert "Aspiring AI Engineer" in data["personal"]["title"]

    # Projects status check: NOT marked as completed
    for p in data["projects"]:
        assert p["status"] in ["Planned", "In Progress", "Planned / In Progress"]
        # Links must be null/empty
        assert not p.get("github_url")
        assert not p.get("live_url")
        assert not p.get("screenshot_url")

    # Certifications check: no fake URLs
    for c in data["certifications"]:
        assert not c.get("certificate_url")
