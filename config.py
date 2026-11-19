import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the portfolio project
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from .env file if it exists
load_dotenv(BASE_DIR / ".env")

class Config:
    """Base application configuration with automatic DEV MODE fallback."""

    # Secret key for CSRF and session signing
    SECRET_KEY = os.environ.get("SECRET_KEY", "karthikraj-dev-secret-key-2026")

    # Fetch database connection string
    raw_db_url = os.environ.get("DATABASE_URL", "").strip()

    if raw_db_url:
        # Standardize MySQL connection string format for SQLAlchemy + PyMySQL
        if raw_db_url.startswith("mysql://"):
            raw_db_url = raw_db_url.replace("mysql://", "mysql+pymysql://", 1)
        SQLALCHEMY_DATABASE_URI = raw_db_url
        DB_ENGINE = "mysql" if "mysql" in raw_db_url else "external"
        print(f"[DATABASE] Connected to database via DATABASE_URL ({DB_ENGINE})")
    else:
        # DEV MODE: Fallback to local SQLite when DATABASE_URL is not set
        sqlite_path = BASE_DIR / "portfolio_dev.db"
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{sqlite_path.as_posix()}"
        DB_ENGINE = "sqlite"
        print("=================================================================")
        print(" [DEV MODE] DATABASE_URL is not set.")
        print(f" Automatically using local SQLite: {SQLALCHEMY_DATABASE_URI}")
        print("=================================================================")

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Rate limiting storage (in-memory for development)
    RATELIMIT_STORAGE_URI = "memory://"
    RATELIMIT_DEFAULT = "200 per day;50 per hour"


class TestingConfig(Config):
    """Configuration for automated test suite."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    DB_ENGINE = "sqlite"
    RATELIMIT_ENABLED = True
