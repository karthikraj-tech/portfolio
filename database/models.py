from datetime import datetime, timezone
from database.db import db

class Project(db.Model):
    """
    Project model storing portfolio projects.
    Honesty Rule: Unfinished projects carry 'Planned' or 'In Progress' status.
    Empty links (screenshot, github, live demo) are stored as NULL.
    """
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    tech_stack = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), nullable=False, default="Planned / In Progress")
    screenshot_url = db.Column(db.String(500), nullable=True)
    github_url = db.Column(db.String(500), nullable=True)
    live_url = db.Column(db.String(500), nullable=True)
    sort_order = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        """Serialize Project object to JSON-ready dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "tech_stack": self.tech_stack,
            "status": self.status,
            "screenshot_url": self.screenshot_url,
            "github_url": self.github_url,
            "live_url": self.live_url,
            "sort_order": self.sort_order
        }


class Skill(db.Model):
    """
    Skill model storing categorized skills.
    Honesty Rule: No fake proficiency levels or percentages.
    """
    __tablename__ = "skills"

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    sort_order = db.Column(db.Integer, default=0, nullable=False)

    def to_dict(self):
        """Serialize Skill object to JSON-ready dictionary."""
        return {
            "id": self.id,
            "category": self.category,
            "name": self.name,
            "sort_order": self.sort_order
        }


class Certification(db.Model):
    """
    Certification model storing earned course credentials.
    Honesty Rule: Links shown only when a real URL exists.
    """
    __tablename__ = "certifications"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    issuer = db.Column(db.String(150), nullable=False)
    completion_date = db.Column(db.String(50), nullable=False)
    certificate_url = db.Column(db.String(500), nullable=True)
    image_url = db.Column(db.String(500), nullable=True)

    def to_dict(self):
        """Serialize Certification object to JSON-ready dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "issuer": self.issuer,
            "completion_date": self.completion_date,
            "certificate_url": self.certificate_url,
            "image_url": self.image_url
        }


class ContactMessage(db.Model):
    """
    ContactMessage model storing user inquiries submitted through the contact form.
    Messages are protected by rate limiting and honeypot validation before creation.
    """
    __tablename__ = "contact_messages"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        """Serialize ContactMessage object to JSON-ready dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "subject": self.subject,
            "message": self.message,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
