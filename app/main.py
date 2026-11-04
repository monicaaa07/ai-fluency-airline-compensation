"""Application factory. Run with: uvicorn app.main:create_app --factory"""
from __future__ import annotations

from fastapi import FastAPI

from app.api.error_handlers import register_error_handlers
from app.api.routers import claims, health, incidents
from app.clock import Clock
from app.config import Settings
from app.container import build_container
from app.db import apply_migrations, connect
from app.logging_config import configure_logging
from app.seed import seed_staff


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings.from_env()
    configure_logging(settings.log_level)

    conn = connect(settings.db_path)
    apply_migrations(conn)
    if settings.seed_demo_data:
        seed_staff(conn)

    app = FastAPI(title="Airline Compensation Service", version="1.0.0")
    app.state.container = build_container(conn, Clock())
    register_error_handlers(app)
    app.include_router(health.router)
    app.include_router(incidents.router)
    app.include_router(claims.router)
    return app
