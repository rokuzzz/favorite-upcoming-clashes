"""FastAPI application entry point: `uvicorn app.main:app --reload`."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

from app import config
from app.api.routes import router
from app.container import Services, build_services


def create_app(services: Services | None = None) -> FastAPI:
    """Pass `services` to run the app with fakes (tests); otherwise real API clients are built."""

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        if services is not None:
            app.state.services = services
            yield
        else:
            async with httpx.AsyncClient(timeout=config.HTTP_TIMEOUT_S, follow_redirects=True) as http:
                app.state.services = build_services(http)
                yield

    app = FastAPI(title="Favorite Upcoming Clashes", version="0.1.0", lifespan=lifespan)
    app.include_router(router)
    return app


app = create_app()
