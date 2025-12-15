import logging

from fastapi import FastAPI
import socketio  # type: ignore[import-untyped]

from api.chat.chat import register_socket_handlers
from extensions.ext_blueprint import init_app as init_blueprints
from extensions.ext_error_handling import init_app as init_error_handling
from extensions.ext_logging import init_logging

# Configure logging
init_logging()

logger = logging.getLogger(__name__)

# FastAPI application
app = FastAPI()

# Socket.IO (sio) create a Socket.IO server
sio = socketio.AsyncServer(cors_allowed_origins="*", async_mode="asgi")

# Register SocketIO handlers BEFORE mounting (important!)
register_socket_handlers(sio)

# Wrap with ASGI application and mount at /socket.io/ path
socket_app = socketio.ASGIApp(sio)
app.mount("/socket.io", socket_app)

# Initialize FastAPI extensions (routers, error handlers, etc.)
init_blueprints(app)
init_error_handling(app)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=5001, lifespan="on", reload=True)
