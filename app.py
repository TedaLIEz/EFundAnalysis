from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from http import HTTPStatus
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
api = Api(app)

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), HTTPStatus.NOT_FOUND

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({'error': 'Internal server error'}), HTTPStatus.INTERNAL_SERVER_ERROR

class HealthCheck(Resource):
    def get(self):
        return {'status': 'healthy'}, HTTPStatus.OK

api.add_resource(HealthCheck, '/health')