from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def init_app(app: FastAPI) -> None:
    """Initialize FastAPI application with routers and middleware."""
    from api.observability.health import health_router

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers
    app.include_router(health_router)
