"""Debugpy integration for remote debugging.

Enables debugging in Docker containers or remote environments.
"""

from __future__ import annotations

from python_template.config import settings
from python_template.logging import get_logger


def setup_debugpy() -> None:
    """Start debugpy listener if enabled in settings.

    Call this early in application startup (before FastAPI app creation).
    """
    if not settings.debugpy:
        return

    log = get_logger("python_template.debug")

    try:
        import debugpy

        debugpy.listen((settings.debugpy_host, settings.debugpy_port))
        log.info(
            f"Debugpy listening on {settings.debugpy_host}:{settings.debugpy_port}"
        )

        if settings.debugpy_wait:
            log.info("Waiting for debugger to attach...")
            debugpy.wait_for_client()
            log.info("Debugger attached")

    except ImportError:
        log.warning("debugpy not installed. Install with: uv pip install -e '.[dev]'")
    except Exception as e:
        log.error(f"Failed to start debugpy: {e}")
