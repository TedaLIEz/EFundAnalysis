from http import HTTPStatus
import logging

from flask import Flask, jsonify, request
from flask_restful import Api, Resource  # type: ignore

from api.observability.health import HealthCheck

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
api = Api(app)


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found"}), HTTPStatus.NOT_FOUND


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({"error": "Internal server error"}), HTTPStatus.INTERNAL_SERVER_ERROR


api.add_resource(HealthCheck, "/health")
