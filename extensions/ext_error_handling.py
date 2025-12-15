from http import HTTPStatus

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


def init_app(app: FastAPI) -> None:
    """Initialize FastAPI application with exception handlers."""

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        """Handle HTTP exceptions (including 404)."""
        # Don't interfere with Socket.IO paths
        if request.url.path.startswith("/socket.io/"):
            return JSONResponse(status_code=exc.status_code, content="")
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail if exc.detail else "Resource not found"},
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handle unhandled exceptions (500 errors)."""
        # Don't interfere with Socket.IO paths
        if request.url.path.startswith("/socket.io/"):
            return JSONResponse(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, content="")
        return JSONResponse(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            content={"error": "Internal server error"},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """Handle request validation errors."""
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"error": "Validation error", "details": exc.errors()},
        )
