"""HTTP layer: turns requests into service calls and errors into status codes. No business logic."""

from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, Request

from app import config
from app.container import Services
from app.models import DataSource, MatchesResponse, Preferences, Team
from app.services.match_service import MatchService, UnknownTeamError
from app.services.settings_service import SettingsService

router = APIRouter(prefix="/api")


def get_match_service(request: Request) -> MatchService:
    services: Services = request.app.state.services
    return services.match_service


def get_settings_service(request: Request) -> SettingsService:
    services: Services = request.app.state.services
    return services.settings_service


MatchServiceDep = Annotated[MatchService, Depends(get_match_service)]
SettingsServiceDep = Annotated[SettingsService, Depends(get_settings_service)]


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/teams", response_model=list[Team])
async def list_teams(matches: MatchServiceDep) -> list[Team]:
    try:
        return await matches.get_teams()
    except httpx.HTTPError as exc:
        raise HTTPException(502, "Liiga API is unavailable") from exc


@router.get("/data-sources", response_model=list[DataSource])
async def list_data_sources(matches: MatchServiceDep) -> list[DataSource]:
    return matches.data_sources


@router.get("/matches", response_model=MatchesResponse)
async def list_matches(
    matches: MatchServiceDep,
    team: Annotated[str, Query(description="Liiga team id, e.g. 624554857:lukko")],
    days: Annotated[int, Query(description="Time horizon in days: 7, 14 or 21")] = 14,
    include: Annotated[str, Query(description="Comma-separated data sources, e.g. weather")] = "",
) -> MatchesResponse:
    if days not in config.ALLOWED_HORIZONS:
        raise HTTPException(422, f"days must be one of {config.ALLOWED_HORIZONS}")
    include_keys = {key.strip() for key in include.split(",") if key.strip()}
    try:
        return await matches.get_upcoming_matches(team, days, include_keys)
    except UnknownTeamError as exc:
        raise HTTPException(404, f"Unknown team: {team}") from exc
    except httpx.HTTPError as exc:
        raise HTTPException(502, "Liiga API is unavailable") from exc


# Plain `def` (not async): FastAPI runs these in a worker thread, so the file I/O does not block the event loop.
@router.get("/preferences", response_model=Preferences)
def get_preferences(settings: SettingsServiceDep) -> Preferences:
    return settings.get()


@router.put("/preferences", response_model=Preferences)
def save_preferences(preferences: Preferences, settings: SettingsServiceDep) -> Preferences:
    return settings.save(preferences)
