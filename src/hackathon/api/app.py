"""FastAPI application."""

from fastapi import FastAPI

from hackathon.api.routes import health, agents
from hackathon.infrastructure.config import settings

app = FastAPI(title=settings.app_name, version="0.1.0")

app.include_router(health.router, tags=["health"])
app.include_router(agents.router, prefix="/agents", tags=["agents"])
