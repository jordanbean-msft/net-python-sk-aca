# Use Python 3.12 slim image
FROM python:3.12-slim AS base

# Set working directory
WORKDIR /app

# Install system dependencies including curl for health checks
RUN apt-get update && \
  apt-get install -y --no-install-recommends curl && \
  rm -rf /var/lib/apt/lists/*

# Install uv for fast Python package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set environment variables for uv
ENV UV_SYSTEM_PYTHON=1 \
  UV_COMPILE_BYTECODE=1

# Copy pyproject.toml first for better caching
COPY pyproject.toml .

# Install Python dependencies using uv (much faster than pip)
RUN uv pip install --no-cache .

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
  chown -R appuser:appuser /app

USER appuser

# Expose port (configurable via PORT environment variable)
ARG PORT=8000
EXPOSE ${PORT}

# Set default environment variables
ENV PORT=${PORT} \
  LOG_LEVEL=info

# Health check (uses PORT environment variable at runtime)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:${PORT}/health || exit 1

# Run the application (port and log level configurable via environment variables)
CMD sh -c "uvicorn main:app --host 0.0.0.0 --port ${PORT} --log-level ${LOG_LEVEL}"
