from fastapi import APIRouter

health_router = APIRouter(tags=["observability"])


@health_router.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "healthy"}
