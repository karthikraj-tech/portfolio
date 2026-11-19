"""
seed.py - Database Seeder
Loads portfolio data from data/portfolio_data.json into the configured database (SQLite or MySQL).
Idempotent: Running this script multiple times will NEVER create duplicate entries.
"""

import json
from pathlib import Path
from app import create_app
from database.db import db
from database.models import Project, Skill, Certification

DATA_FILE = Path(__file__).resolve().parent / "data" / "portfolio_data.json"

def seed_database():
    app = create_app()

    with app.app_context():
        # Ensure database tables exist
        db.create_all()
        print(f"[SEED] Using Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

        if not DATA_FILE.exists():
            print(f"[SEED ERROR] Data file not found at: {DATA_FILE}")
            return

        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 1. Seed Skills (Idempotent: check by name and category)
        skills_added = 0
        skills_skipped = 0
        for item in data.get("skills", []):
            existing = Skill.query.filter_by(
                name=item["name"],
                category=item["category"]
            ).first()

            if not existing:
                skill = Skill(
                    category=item["category"],
                    name=item["name"],
                    sort_order=item.get("sort_order", 0)
                )
                db.session.add(skill)
                skills_added += 1
            else:
                # Update sort_order if changed
                existing.sort_order = item.get("sort_order", 0)
                skills_skipped += 1

        # 2. Seed Projects (Idempotent: check by title)
        projects_added = 0
        projects_skipped = 0
        for item in data.get("projects", []):
            existing = Project.query.filter_by(title=item["title"]).first()

            if not existing:
                project = Project(
                    title=item["title"],
                    description=item["description"],
                    tech_stack=item["tech_stack"],
                    status=item.get("status", "Planned / In Progress"),
                    screenshot_url=item.get("screenshot_url"),
                    github_url=item.get("github_url"),
                    live_url=item.get("live_url"),
                    sort_order=item.get("sort_order", 0)
                )
                db.session.add(project)
                projects_added += 1
            else:
                # Update fields if changed in JSON
                existing.description = item["description"]
                existing.tech_stack = item["tech_stack"]
                existing.status = item.get("status", "Planned / In Progress")
                existing.screenshot_url = item.get("screenshot_url")
                existing.github_url = item.get("github_url")
                existing.live_url = item.get("live_url")
                existing.sort_order = item.get("sort_order", 0)
                projects_skipped += 1

        # 3. Seed Certifications (Idempotent: check by title and issuer)
        certs_added = 0
        certs_skipped = 0
        for item in data.get("certifications", []):
            existing = Certification.query.filter_by(
                title=item["title"],
                issuer=item["issuer"]
            ).first()

            if not existing:
                cert = Certification(
                    title=item["title"],
                    issuer=item["issuer"],
                    completion_date=item["completion_date"],
                    certificate_url=item.get("certificate_url"),
                    image_url=item.get("image_url")
                )
                db.session.add(cert)
                certs_added += 1
            else:
                existing.completion_date = item["completion_date"]
                existing.certificate_url = item.get("certificate_url")
                existing.image_url = item.get("image_url")
                certs_skipped += 1

        # Commit all changes to the database
        db.session.commit()

        print("--------------------------------------------------")
        print(f" [SEED RESULTS]")
        print(f" Skills:         {skills_added} added, {skills_skipped} verified/updated")
        print(f" Projects:       {projects_added} added, {projects_skipped} verified/updated")
        print(f" Certifications: {certs_added} added, {certs_skipped} verified/updated")
        print(" Database seeding completed successfully!")
        print("--------------------------------------------------")

if __name__ == "__main__":
    seed_database()
