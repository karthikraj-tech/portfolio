"""
tests/test_app.py
Comprehensive automated test suite for Karthikraj S Portfolio API.
Tests cover health checks, catalog endpoints, contact form validation,
honeypot bot detection, database persistence, and rate limiting.
"""

import json
import pytest
from app import create_app
from config import TestingConfig
from database.db import db
from database.models import Project, Skill, Certification, ContactMessage
from extensions import limiter


@pytest.fixture
def app():
    """Create and configure a clean Flask application instance for testing."""
    test_app = create_app(TestingConfig)

    with test_app.app_context():
        db.create_all()

        # Seed sample data for testing endpoints
        skill1 = Skill(category="Programming Languages", name="Python", sort_order=1)
        skill2 = Skill(category="Databases", name="MySQL", sort_order=2)
        proj1 = Project(
            title="Student Attendance Management System",
            description="Academic project concept",
            tech_stack="Python, Database Management",
            status="Planned / In Progress",
            sort_order=1
        )
        cert1 = Certification(
            title="Introduction to Artificial Intelligence",
            issuer="Infosys Springboard",
            completion_date="October 2025"
        )
        db.session.add_all([skill1, skill2, proj1, cert1])
        db.session.commit()

        # Reset rate limiter memory before running tests
        limiter.reset()

        yield test_app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Test client for issuing HTTP requests."""
    return app.test_client()


def test_health_check(client):
    """GET /api/health should return 200 with status healthy and database engine."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert "database" in data
    assert "timestamp" in data


def test_get_projects(client):
    """GET /api/projects should return 200 with list of projects."""
    response = client.get("/api/projects")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert data["count"] >= 1
    assert data["data"][0]["title"] == "Student Attendance Management System"
    assert data["data"][0]["status"] == "Planned / In Progress"


def test_get_skills(client):
    """GET /api/skills should return 200 with list of skills."""
    response = client.get("/api/skills")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert data["count"] >= 2
    skill_names = [s["name"] for s in data["data"]]
    assert "Python" in skill_names
    assert "MySQL" in skill_names


def test_get_certifications(client):
    """GET /api/certifications should return 200 with list of certifications."""
    response = client.get("/api/certifications")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert data["count"] >= 1
    assert data["data"][0]["issuer"] == "Infosys Springboard"


def test_resume_status(client):
    """GET /api/resume-status should return 200 and available boolean flag."""
    response = client.get("/api/resume-status")
    assert response.status_code == 200
    data = response.get_json()
    assert "available" in data
    assert "message" in data


def test_valid_contact_submission(client, app):
    """POST /api/contact with valid data should succeed (201) and persist to database."""
    payload = {
        "name": "Jane Recruiter",
        "email": "jane@techcorp.com",
        "subject": "Internship Opportunity",
        "message": "Hello Karthikraj, we came across your portfolio and are interested in discussing an internship.",
        "website_url": ""  # Honeypot left empty by human users
    }
    response = client.post("/api/contact", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data["status"] == "success"

    # Confirm message was stored in database
    with app.app_context():
        saved = ContactMessage.query.filter_by(email="jane@techcorp.com").first()
        assert saved is not None
        assert saved.name == "Jane Recruiter"
        assert saved.subject == "Internship Opportunity"


def test_contact_invalid_email(client):
    """POST /api/contact with an invalid email format must return 400 Bad Request."""
    payload = {
        "name": "Alex",
        "email": "invalid-email-format",
        "subject": "Question",
        "message": "This is a test message to verify email validation logic."
    }
    response = client.post("/api/contact", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert data["status"] == "error"
    assert "valid email" in data["message"].lower()


def test_contact_empty_fields(client):
    """POST /api/contact with missing/empty fields must return 400 Bad Request."""
    # Test missing name
    response = client.post("/api/contact", json={
        "name": "",
        "email": "test@example.com",
        "subject": "Hello",
        "message": "Valid length message here."
    })
    assert response.status_code == 400
    assert "name" in response.get_json()["message"].lower()

    # Test short message (< 10 chars)
    response = client.post("/api/contact", json={
        "name": "Karthik",
        "email": "test@example.com",
        "subject": "Hello",
        "message": "Short"
    })
    assert response.status_code == 400
    assert "message" in response.get_json()["message"].lower()


def test_contact_honeypot_spam_detected(client, app):
    """
    POST /api/contact with honeypot field filled must be blocked (400)
    and MUST NOT be saved into the database.
    """
    initial_count = 0
    with app.app_context():
        initial_count = ContactMessage.query.count()

    payload = {
        "name": "Spam Bot 3000",
        "email": "bot@spammer.org",
        "subject": "Buy cheap SEO ranking",
        "message": "Click here to buy backlinks for your portfolio website right now!",
        "website_url": "http://spamsite.xyz"  # Bots fill this hidden input
    }
    response = client.post("/api/contact", json=payload)
    assert response.status_code == 400
    assert "spam" in response.get_json()["message"].lower()

    # Verify message was NOT saved
    with app.app_context():
        final_count = ContactMessage.query.count()
        assert final_count == initial_count


def test_contact_rate_limit(client):
    """
    POST /api/contact rate limit test:
    After 5 valid submissions within an hour, the 6th must return 429 Too Many Requests.
    """
    payload_template = {
        "name": "User",
        "subject": "Testing Rate Limit",
        "message": "This is rate limit testing message content for portfolio test suite."
    }

    # Reset limiter for this test
    limiter.reset()

    # Submit 5 times (allowed limit)
    for i in range(5):
        payload = {**payload_template, "email": f"user{i}@example.com"}
        res = client.post("/api/contact", json=payload)
        assert res.status_code == 201

    # 6th request should be rate-limited
    payload_excess = {**payload_template, "email": "excess@example.com"}
    res_excess = client.post("/api/contact", json=payload_excess)
    assert res_excess.status_code == 429
    data = res_excess.get_json()
    assert data["status"] == "error"
    assert "limit" in data["message"].lower()
