# Multi-stage Dockerfile for Big Mann Entertainment FastAPI Backend
# Optimized for production deployment with security and performance considerations

FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_NO_INTERACTION=1

# Create non-root user
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid appuser --shell /bin/bash --create-home appuser

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libc6-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Development stage
FROM base as development

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies with dev tools
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install pytest pytest-cov black flake8 bandit safety

# Copy source code
COPY . .

# Change ownership to appuser
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Development command
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Staging stage
FROM base as staging

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies (no dev tools)
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install gunicorn

# Copy source code
COPY . .

# Run security checks and tests
RUN pip install pytest pytest-cov black flake8 bandit safety && \
    safety check && \
    bandit -r . -x tests/ && \
    black --check . && \
    flake8 . && \
    python -m pytest tests/ --cov=. --cov-report=term-missing || true

# Remove dev dependencies
RUN pip uninstall -y pytest pytest-cov black flake8 bandit safety

# Change ownership to appuser
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Staging command with gunicorn
CMD ["gunicorn", "server:app", "-w", "2", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--access-logfile", "-", "--error-logfile", "-", "--log-level", "info"]

# Production stage
FROM base as production

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies (production only)
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install gunicorn

# Copy source code
COPY . .

# Remove unnecessary files
RUN rm -rf tests/ *.md .git* .dockerignore Dockerfile*

# Change ownership to appuser
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Production command with optimized gunicorn settings
CMD ["gunicorn", "server:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--access-logfile", "-", "--error-logfile", "-", "--log-level", "warning", "--max-requests", "1000", "--max-requests-jitter", "100", "--preload", "--timeout", "30"]