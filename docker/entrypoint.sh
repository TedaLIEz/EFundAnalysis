#!/bin/bash
set -e

# Use the virtual environment created during Docker build
exec .venv/bin/gunicorn -b "0.0.0.0:5001" --worker-class eventlet --workers 1 --timeout 200 app:app
