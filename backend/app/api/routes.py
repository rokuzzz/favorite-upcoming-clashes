"""HTTP layer: turns requests into service calls and errors into status codes. No business logic."""

from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, Request

from app import config
from app.container import Services
from app.models import MatchesResponse, Team
from app.services.match_service import MatchService, UnknownTeamError

router = APIRouter(prefix="/api")


def get_match_service(request: Request) -> MatchService:
    services: Services = request.app.state.services
    return services.match_service


MatchServiceDep = Annotated[MatchService, Depends(get_match_service)]


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/teams", response_model=list[Team])
async def list_teams(matches: MatchServiceDep) -> list[Team]:
    try:
        return await matches.get_teams()
    except httpx.HTTPError as exc:
        raise HTTPException(502, "Liiga API is unavailable") from exc


@router.get("/matches", response_model=MatchesResponse)
async def list_matches(
    matches: MatchServiceDep,
    team: Annotated[str, Query(description="Liiga team id, e.g. 624554857:lukko")],
    days: Annotated[int, Query(description="Time horizon in days: 7, 14 or 21")] = 14,
) -> MatchesResponse:
    if days not in config.ALLOWED_HORIZONS:
        raise HTTPException(422, f"days must be one of {config.ALLOWED_HORIZONS}")
    try:
        return await matches.get_upcoming_matches(team, days)
    except UnknownTeamError as exc:
        raise HTTPException(404, f"Unknown team: {team}") from exc
    except httpx.HTTPError as exc:
        raise HTTPException(502, "Liiga API is unavailable") from exc
