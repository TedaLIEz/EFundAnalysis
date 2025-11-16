from http import HTTPStatus

from flask_restful import Resource  # type: ignore


class HealthCheck(Resource):
    def get(self):
        return {"status": "healthy"}, HTTPStatus.OK
