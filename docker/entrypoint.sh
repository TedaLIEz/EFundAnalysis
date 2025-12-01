#!/bin/bash
set -e

exec uv run gunicorn -b "0.0.0.0:5001" --worker-class eventlet --workers 1 --timeout 200 app:app
