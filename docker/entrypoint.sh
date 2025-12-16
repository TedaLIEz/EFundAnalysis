#!/bin/bash
set -e

# Use the virtual environment created during Docker build
exec .venv/bin/uvicorn app:app --host 0.0.0.0 --port 5001 --reload
