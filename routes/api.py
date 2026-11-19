"""
routes/api.py
API endpoints for fetching portfolio content and handling contact submissions.
"""

import re
from datetime import datetime, timezone
from pathlib import Path
from flask import Blueprint, jsonify, request, current_app
from database.db import db
from database.models import Project, Skill, Certification, ContactMessage
from extensions import limiter

api_bp = Blueprint("api", __name__, url_prefix="/api")

# Basic RFC 5322 compliant regex for practical email format verification
EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}$")


@api_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint to verify backend status and database connectivity."""
    db_engine = current_app.config.get("DB_ENGINE", "unknown")
    return jsonify({
        "status": "healthy",
        "database": db_engine,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }), 200


@api_bp.route("/projects", methods=["GET"])
def get_projects():
    """Fetch all portfolio projects sorted by sort_order ascending."""
    try:
        projects = Project.query.order_by(Project.sort_order.asc(), Project.id.asc()).all()
        return jsonify({
            "status": "success",
            "count": len(projects),
            "data": [p.to_dict() for p in projects]
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching projects: {e}")
        return jsonify({
            "status": "error",
            "message": "Unable to load projects at this time."
        }), 500


@api_bp.route("/skills", methods=["GET"])
def get_skills():
    """Fetch all skills sorted by category and sort_order."""
    try:
        skills = Skill.query.order_by(Skill.category.asc(), Skill.sort_order.asc()).all()
        return jsonify({
            "status": "success",
            "count": len(skills),
            "data": [s.to_dict() for s in skills]
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching skills: {e}")
        return jsonify({
            "status": "error",
            "message": "Unable to load skills at this time."
        }), 500


@api_bp.route("/certifications", methods=["GET"])
def get_certifications():
    """Fetch all certifications."""
    try:
        certs = Certification.query.order_by(Certification.id.asc()).all()
        return jsonify({
            "status": "success",
            "count": len(certs),
            "data": [c.to_dict() for c in certs]
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching certifications: {e}")
        return jsonify({
            "status": "error",
            "message": "Unable to load certifications at this time."
        }), 500


@api_bp.route("/resume-status", methods=["GET"])
def get_resume_status():
    """
    Honesty Rule Check:
    Verify whether the actual resume PDF file exists in static/resume/.
    If the file does not exist, the frontend shows 'Resume coming soon' (disabled).
    """
    resume_path = Path(current_app.root_path) / "static" / "resume" / "Karthikraj_S_Resume.pdf"
    file_exists = resume_path.is_file()
    return jsonify({
        "available": file_exists,
        "filename": "Karthikraj_S_Resume.pdf" if file_exists else None,
        "message": "Resume available" if file_exists else "Resume coming soon"
    }), 200


@api_bp.route("/contact", methods=["POST"])
@limiter.limit("5 per hour")
def handle_contact():
    """
    Contact form submission handler.
    - Rate-limited to 5 submissions per hour per IP.
    - Hidden honeypot field protection against automated spam bots.
    - Validates name, email format, subject, and message length.
    - Uses SQLAlchemy ORM to prevent SQL injection.
    """
    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({
            "status": "error",
            "message": "Invalid request body. Expected JSON payload."
        }), 400

    # 1. Honeypot check (Spam Protection)
    # The frontend form includes a hidden input named 'website_url' which users don't see.
    honeypot_val = data.get("website_url", "").strip()
    if honeypot_val:
        # Automated bot caught; reject silently with standard bad request
        return jsonify({
            "status": "error",
            "message": "Spam submission detected."
        }), 400

    # 2. Extract and sanitize inputs
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    subject = (data.get("subject") or "").strip()
    message = (data.get("message") or "").strip()

    # 3. Required field validations
    if not name:
        return jsonify({"status": "error", "message": "Your name is required."}), 400
    if not email:
        return jsonify({"status": "error", "message": "Your email address is required."}), 400
    if not subject:
        return jsonify({"status": "error", "message": "A message subject is required."}), 400
    if not message:
        return jsonify({"status": "error", "message": "A message content is required."}), 400

    # 4. Length constraints
    if len(name) < 2 or len(name) > 100:
        return jsonify({"status": "error", "message": "Name must be between 2 and 100 characters."}), 400
    if len(email) < 5 or len(email) > 120:
        return jsonify({"status": "error", "message": "Email must be between 5 and 120 characters."}), 400
    if len(subject) < 2 or len(subject) > 200:
        return jsonify({"status": "error", "message": "Subject must be between 2 and 200 characters."}), 400
    if len(message) < 10 or len(message) > 5000:
        return jsonify({"status": "error", "message": "Message must be between 10 and 5,000 characters."}), 400

    # 5. Email format validation
    if not EMAIL_REGEX.match(email):
        return jsonify({"status": "error", "message": "Please provide a valid email address (e.g., name@example.com)."}), 400

    # 6. Store message using ORM (parameterized query)
    try:
        new_msg = ContactMessage(
            name=name,
            email=email,
            subject=subject,
            message=message
        )
        db.session.add(new_msg)
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Thank you, Karthikraj will get back to you shortly!"
        }), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to save contact message: {e}")
        return jsonify({
            "status": "error",
            "message": "An unexpected error occurred while saving your message. Please try again later."
        }), 500
