# syntax=docker/dockerfile:1.4

# =============================================================================
# Production runtime
# =============================================================================
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHON_TEMPLATE_HOST=0.0.0.0 \
    PYTHON_TEMPLATE_PORT=8000

WORKDIR /app

# Create non-root user
RUN useradd --create-home --uid 10001 appuser

# Copy dependency files first for better caching
COPY pyproject.toml README.md /app/

# Install dependencies (without the package itself)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system -e .

# Copy source code
COPY src/ /app/src/

# Install the package
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system -e .

USER appuser

EXPOSE 8000

CMD ["uvicorn", "python_template.api.asgi:app", "--host", "0.0.0.0", "--port", "8000"]


# =============================================================================
# Development runtime (with reload and dev dependencies)
# =============================================================================
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS runtime-dev

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHON_TEMPLATE_HOST=0.0.0.0 \
    PYTHON_TEMPLATE_PORT=8000 \
    PYTHON_TEMPLATE_LOG_FORMAT=pretty \
    PYTHON_TEMPLATE_DEBUGPY=1 \
    PYTHON_TEMPLATE_DEBUGPY_HOST=0.0.0.0 \
    PYTHON_TEMPLATE_DEBUGPY_PORT=5678 \
    PYDEVD_DISABLE_FILE_VALIDATION=1

WORKDIR /app

# Create non-root user
RUN useradd --create-home --uid 10001 appuser

# Copy dependency files
COPY pyproject.toml README.md /app/

# Install all dependencies including dev
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system -e ".[dev]"

# Copy source code
COPY src/ /app/src/

# Reinstall with source
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system -e ".[dev]"

USER appuser

EXPOSE 8000
EXPOSE 5678

# Reload improves breakpoint reliability with debugpy in containers
CMD ["uvicorn", "python_template.api.asgi:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--reload-dir", "/app/src"]
