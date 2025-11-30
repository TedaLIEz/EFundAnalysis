"""CORS extension for Flask application."""

from flask import Flask
from flask_cors import CORS


def init_app(app: Flask) -> None:
    """Initialize CORS for the Flask application.

    Allows all origins for local development. In production, you should
    restrict this to specific origins.

    Args:
        app: The Flask application instance

    """
    CORS(
        app,
        origins="*",  # Allow all origins for localhost development
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
        supports_credentials=True,
    )
