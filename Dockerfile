# Use Python 3.12 as base image
FROM python:3.12-slim AS base

ENV TZ=UTC
# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

FROM base AS builder

# Set working directory
WORKDIR /app
# Copy dependency files and README (needed by hatchling during build)
COPY pyproject.toml uv.lock README.md ./

# Install dependencies using uv
RUN uv sync --frozen --no-dev


FROM builder AS runner
# Copy application code
COPY . .

# Expose the port Flask runs on
EXPOSE 5001

COPY docker/entrypoint.sh ./entrypoint.sh
RUN chmod +x ./entrypoint.sh
ENTRYPOINT ["/bin/bash", "./entrypoint.sh"]
