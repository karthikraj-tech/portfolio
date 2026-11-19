"""
extensions.py
Flask extension instances shared across blueprints and application factory.
"""

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Rate limiter instance using client IP
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)
