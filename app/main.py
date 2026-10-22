"""ComStream API — Async Weather & Market Data Aggregator."""

from __future__ import annotations

import logging
import sys

from fastapi import FastAPI

from app.api.routes import router
from app.config import settings


def _configure_logging() -> None:
    """Set up structured, human-readable logging to stdout."""
    log_level = logging.DEBUG if settings.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        stream=sys.stdout,
        force=True,
    )


_configure_logging()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "A modern async API that aggregates real-time weather and "
        "cryptocurrency market data into a single dashboard endpoint."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(router)
