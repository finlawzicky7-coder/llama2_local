"""FastAPI app factory."""

from __future__ import annotations

import logging

from fastapi import FastAPI

from app.billing_routes import router as billing_router
from app.config import get_settings
from app.dashboard import router as dashboard_router
from app.voice import router as voice_router


def create_app() -> FastAPI:
    settings = get_settings()
    logging.basicConfig(level=settings.log_level)
    app = FastAPI(title="Ringback")
    app.include_router(dashboard_router)
    app.include_router(voice_router)
    app.include_router(billing_router)
    return app


app = create_app()
