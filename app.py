"""
app.py
Main Flask application entry point for Karthikraj S Portfolio.
Supports both local DEV MODE (SQLite) and Production (MySQL).
"""

import os
from flask import Flask, render_template, jsonify, request
from config import Config
from database.db import db
from extensions import limiter
from routes.api import api_bp

def create_app(config_class=Config):
    """Application factory for Flask portfolio service."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    limiter.init_app(app)

    # Register blueprints
    app.register_blueprint(api_bp)

    # Home route serving the frontend single-page application
    @app.route("/")
    def index():
        return render_template("index.html")

    # Security headers on every response
    @app.after_request
    def set_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

    # Custom Error Handlers
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify({
            "status": "error",
            "message": "Too many requests. You have reached the submission limit (5 per hour). Please try again later."
        }), 429

    @app.errorhandler(404)
    def not_found_handler(e):
        if request.path.startswith("/api/"):
            return jsonify({
                "status": "error",
                "message": "API endpoint not found."
            }), 404
        return render_template("index.html"), 404

    @app.errorhandler(500)
    def internal_error_handler(e):
        if request.path.startswith("/api/"):
            return jsonify({
                "status": "error",
                "message": "Internal server error. Please try again later."
            }), 500
        return "Internal Server Error", 500

    return app

# Application instance for local development and Gunicorn
app = create_app()

if __name__ == "__main__":
    with app.app_context():
        # Ensure database tables exist in active database (SQLite / MySQL)
        db.create_all()
    # Run development server
    port = int(os.environ.get("PORT", 5000))
    app.run(host="127.0.0.1", port=port, debug=True)
