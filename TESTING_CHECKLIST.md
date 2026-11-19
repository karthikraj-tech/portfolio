# Testing Checklist & Verification Report

**Project**: Karthikraj S - Personal Portfolio Website  
**Date**: November 19, 2026  
**Environment**: Windows 11 (64-bit), Python 3.13.14, SQLite 3 (DEV MODE) / MySQL 8.0 Server  
**Test Suite**: `pytest` 9.2.0, Live HTTP socket probe, End-to-End DOM/CSS validation  

---

## 1. Automated Test Suite Results (`pytest`)

Command run: `.\.venv\Scripts\python.exe -m pytest tests\ -v`

| Test File | Test Case | Description | Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| `test_app.py` | `test_health_check` | Verify `GET /api/health` status, database engine, and timestamp | HTTP 200, valid payload | **PASS** |
| `test_app.py` | `test_get_projects` | Verify `GET /api/projects` returns list with status badges | HTTP 200, count >= 1 | **PASS** |
| `test_app.py` | `test_get_skills` | Verify `GET /api/skills` returns categorized skills | HTTP 200, count >= 2 | **PASS** |
| `test_app.py` | `test_get_certifications` | Verify `GET /api/certifications` returns earned credentials | HTTP 200, count >= 1 | **PASS** |
| `test_app.py` | `test_resume_status` | Verify `GET /api/resume-status` file check on disk | HTTP 200, `available: false` | **PASS** |
| `test_app.py` | `test_valid_contact_submission` | Submit valid contact payload and verify database persistence | HTTP 201, saved in DB | **PASS** |
| `test_app.py` | `test_contact_invalid_email` | Submit malformed email (`invalid-email-format`) | HTTP 400 Bad Request | **PASS** |
| `test_app.py` | `test_contact_empty_fields` | Submit missing name and short message (< 10 chars) | HTTP 400 Bad Request | **PASS** |
| `test_app.py` | `test_contact_honeypot_spam` | Submit payload with filled honeypot (`website_url`) | HTTP 400, not saved in DB | **PASS** |
| `test_app.py` | `test_contact_rate_limit` | Submit 6 messages from same client IP within 1 hour | 6th request triggers 429 | **PASS** |
| `test_frontend_e2e.py` | `test_html_semantics_and_accessibility` | Check landmarks, skip link, nav anchors, form inputs | All 7 sections present | **PASS** |
| `test_frontend_e2e.py` | `test_css_tokens_and_accessibility_rules` | Check color tokens, focus styles, responsive media queries | Dark/Light & 360px verified | **PASS** |
| `test_frontend_e2e.py` | `test_javascript_security_and_dom_handling` | Verify anti-XSS (`textContent`), API calls, theme storage | Zero `innerHTML` for inputs | **PASS** |
| `test_frontend_e2e.py` | `test_portfolio_data_honesty_compliance` | Verify no fake experience, no fake links, planned status | 100% honesty adherence | **PASS** |

**Summary**: 14 passed in 1.12 seconds (100% pass rate).

---

## 2. Database Seeder & Idempotency Testing

Command run: `.\.venv\Scripts\python.exe seed.py`

| Run | Operation | Expected Outcome | Actual Outcome | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Run 1 (Initial Seed)** | Seed SQLite `portfolio_dev.db` from `portfolio_data.json` | Insert 10 skills, 2 projects, 2 certs | 10 skills, 2 projects, 2 certs added | **PASS** |
| **Run 2 (Idempotency Check)** | Re-run seeder on already populated database | 0 duplicates created | 0 added, 14 verified/updated | **PASS** |

---

## 3. Live Server & Endpoint Verification

Flask server running live at `http://127.0.0.1:5000` (DEV MODE SQLite):

| Route | Method | Status | Content-Type | Verified Payload / Behavior | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `/` | GET | `200 OK` | `text/html` | HTML document delivered with security headers | **PASS** |
| `/api/health` | GET | `200 OK` | `application/json` | `{"database": "sqlite", "status": "healthy"}` | **PASS** |
| `/api/projects` | GET | `200 OK` | `application/json` | 2 projects returned; empty URLs null | **PASS** |
| `/api/skills` | GET | `200 OK` | `application/json` | 10 skills returned across 4 categories | **PASS** |
| `/api/certifications` | GET | `200 OK` | `application/json` | 2 certifications returned | **PASS** |
| `/api/resume-status` | GET | `200 OK` | `application/json` | `{"available": false, "message": "Resume coming soon"}` | **PASS** |
| `/api/contact` | POST | `201 Created` | `application/json` | Live record created and verified in SQLite table | **PASS** |

---

## 4. UI & Feature Verification

| Feature | Verification Method | Outcome | Status |
| :--- | :--- | :--- | :--- |
| **Hero Section** | Rendered via `/` route | Headline, title, 2-line intro, and buttons present | **PASS** |
| **Resume Button** | Frontend logic (`initResumeStatus`) | Shows "Resume coming soon", disabled (`aria-disabled="true"`) | **PASS** |
| **Skills Badges** | Client DOM rendering | Grouped into 4 cards with pill labels | **PASS** |
| **Projects Status** | Client DOM rendering | Badges show "Planned / In Progress"; missing links hidden | **PASS** |
| **Education Section** | Timeline rendering | RIT (2024-2028) & Sri Ramakrishna School (2024) shown | **PASS** |
| **Theme Toggle** | CSS Variables + JS localStorage | Switches `--bg-primary` and persists `portfolio_theme` | **PASS** |
| **Mobile Hamburger** | CSS Media Query (< 768px) + JS | Toggle button toggles `.open` on navigation menu | **PASS** |
| **Spam Honeypot** | Hidden input `website_url` | Invisible in UI (`display: none`), triggers 400 when filled | **PASS** |
| **Rate Limiter** | Flask-Limiter memory backend | Blocks IP after 5 submissions/hour with friendly message | **PASS** |
| **Anti-XSS Protection** | DOM assignment audit | All dynamic text is set via `textContent`, never `innerHTML` | **PASS** |

---

## 5. What Was NOT Tested & Manual Testing Steps

### A. MySQL Database Authentication
- **Status**: **NOT tested with MySQL user credentials**.
- **Explanation**: The local MySQL service (`MySQL80`) is active and listening on port 3306 on your Windows machine, but it requires your personal root password. To avoid interfering with your local password or databases, SQLite DEV MODE was tested and passed.
- **How to test with MySQL manually**:
  1. Open MySQL Command Line Client or run: `mysql -u root -p`
  2. Create database: `CREATE DATABASE portfolio_db CHARACTER SET utf8mb4;`
  3. Edit your `.env` file:
     ```env
     DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/portfolio_db
     ```
  4. Run the seeder and start Flask:
     ```powershell
     python seed.py
     python app.py
     ```
  5. Verify terminal output: `[DATABASE] Connected to database via DATABASE_URL (mysql)`.

### B. Live Cloud Deployment on Render
- **Status**: **NOT deployed to a public URL**.
- **Explanation**: Prepared for deployment (`render.yaml`, `Procfile`, production Gunicorn setup, and TiDB Cloud compatibility), but per honesty guidelines, the project is not yet uploaded to your personal GitHub account or deployed to Render.
- **How to deploy manually**:
  Follow Section 12 in `README.md` to push the repository to GitHub, configure TiDB Cloud Starter (free MySQL), and link to Render.
