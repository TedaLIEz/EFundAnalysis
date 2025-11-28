from http import HTTPStatus
import logging
import os

from flask import Flask, jsonify, request
from flask_socketio import SocketIO

from api.chat.chat import register_socket_handlers
from api.observability.health import health_bp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configure reloader to exclude dev_ui folder
# This prevents Flask from reloading when files in dev_ui change
# Alternative: Set FLASK_RUN_EXCLUDE_PATTERNS in .flaskenv file or environment
if os.getenv("FLASK_RUN_EXCLUDE_PATTERNS") is None:
    os.environ["FLASK_RUN_EXCLUDE_PATTERNS"] = "dev_ui/*;dev_ui/**/*"

socketio = SocketIO(app)


@app.errorhandler(404)
def not_found(error):
    # Don't interfere with Socket.IO paths
    if request.path.startswith("/socket.io/"):
        return "", HTTPStatus.NOT_FOUND
    return jsonify({"error": "Resource not found"}), HTTPStatus.NOT_FOUND


@app.errorhandler(500)
def internal_server_error(error):
    # Don't interfere with Socket.IO paths
    if request.path.startswith("/socket.io/"):
        return "", HTTPStatus.INTERNAL_SERVER_ERROR
    return jsonify({"error": "Internal server error"}), HTTPStatus.INTERNAL_SERVER_ERROR


app.register_blueprint(health_bp)


register_socket_handlers(socketio)


if __name__ == "__main__":
    # Use socketio.run() instead of app.run() for WebSocket support
    socketio.run(app, host="0.0.0.0", port=5001, debug=True)
