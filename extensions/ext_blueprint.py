from flask import Flask


def init_app(app: Flask) -> None:
    from flask_cors import CORS

    from api.observability.health import health_bp

    CORS(
        health_bp,
        origins="*",
        methods=["GET", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
        supports_credentials=True,
    )
    app.register_blueprint(health_bp)
