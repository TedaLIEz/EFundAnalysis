# Use Python 3.12 as base image
FROM python:3.12-slim

ENV TZ=UTC
# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files and README (needed by hatchling during build)
COPY pyproject.toml uv.lock README.md ./

# Install dependencies using uv
RUN uv sync --frozen --no-dev

# Copy application code
COPY . .

# Expose the port Flask runs on
EXPOSE 5001

COPY docker/entrypoint.sh ./entrypoint.sh
RUN chmod +x ./entrypoint.sh
ENTRYPOINT ["/bin/bash", "./entrypoint.sh"]
