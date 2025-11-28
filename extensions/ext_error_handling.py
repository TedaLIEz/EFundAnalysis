from http import HTTPStatus

from flask import Flask, jsonify, request


def init_app(app: Flask) -> None:
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
