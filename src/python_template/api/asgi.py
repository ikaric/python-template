"""ASGI entrypoint for production servers (uvicorn/gunicorn)."""

from __future__ import annotations

from python_template.debug import setup_debugpy

# Start debugpy before app creation (if enabled)
setup_debugpy()

from python_template.api.app import create_app  # noqa: E402

app = create_app()
