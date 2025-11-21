#!/bin/bash
set -e

if [-n "$GUNICORN_WORKERS" ]; then
    WORKERS=$GUNICORN_WORKERS
else
    CPU_CORES=$(nproc 2>/dev/null || echo 1)
    WORKERS=$((2 * CPU_CORES + 1))
    if [ $WORKERS -lt 1 ]; then
        WORKERS=1
    fi
fi

exec uv run gunicorn -b "0.0.0.0:5001" --workers $WORKERS --timeout 200 app:app
