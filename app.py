from http import HTTPStatus
import logging
import os

from flask import Flask, jsonify, request
from flask_socketio import SocketIO

from api.chat.chat import register_socket_handlers

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure reloader to exclude dev_ui folder
# This prevents Flask from reloading when files in dev_ui change
# Alternative: Set FLASK_RUN_EXCLUDE_PATTERNS in .flaskenv file or environment
if os.getenv("FLASK_RUN_EXCLUDE_PATTERNS") is None:
    os.environ["FLASK_RUN_EXCLUDE_PATTERNS"] = "dev_ui/*;dev_ui/**/*"


def create_app() -> Flask:
    app = Flask(__name__)
    init_ext(app)
    return app


def init_ext(app: Flask) -> None:
    from extensions import ext_blueprint, ext_error_handling

    extensions = [ext_error_handling, ext_blueprint]
    for ext in extensions:
        ext.init_app(app)


app = create_app()


socketio = SocketIO(
    cors_allowed_origins="*",  # Allow all origins for localhost development
    cors_credentials=True,
)
socketio.init_app(app)
register_socket_handlers(socketio)


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5001, debug=True)
