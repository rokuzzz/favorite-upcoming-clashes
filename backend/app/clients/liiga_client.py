"""Adapter for the (unofficial) Liiga web API."""

from datetime import datetime
from typing import Any

import httpx

from app import config
from app.models import Match, Team, Venue

_HEADERS = {"User-Agent": config.BROWSER_USER_AGENT, "Accept": "application/json"}


class LiigaClient:
    """Adapter: turns Liiga's JSON into our domain models. No other module knows Liiga's field names."""

    def __init__(self, http: httpx.AsyncClient, base_url: str = config.LIIGA_BASE_URL) -> None:
        self._http = http
        self._base_url = base_url

    async def fetch_teams(self, season: int) -> list[Team]:
        data = await self._get_json("/standings/", {"season": season})
        return [parse_team(raw) for raw in data.get("season", [])]

    async def fetch_schedule(self, season: int, tournament: str) -> list[Match]:
        data = await self._get_json("/schedule", {"tournament": tournament, "season": season})
        return [parse_match(raw) for raw in data]

    async def _get_json(self, path: str, params: dict[str, Any]) -> Any:
        response = await self._http.get(f"{self._base_url}{path}", params=params, headers=_HEADERS)
        response.raise_for_status()
        return response.json()


def parse_team(raw: dict[str, Any]) -> Team:
    logos = raw.get("teamLogos") or {}
    return Team(
        id=raw["teamId"],
        name=raw["teamName"],
        logo_url=logos.get("lightBg") or logos.get("darkBg"),
    )


def parse_match(raw: dict[str, Any]) -> Match:
    rink = raw.get("iceRink") or {}
    return Match(
        id=raw["id"],
        start=datetime.fromisoformat(raw["start"]),
        home_team_id=raw["homeTeamId"],
        away_team_id=raw["awayTeamId"],
        started=bool(raw.get("started")),
        ended=bool(raw.get("ended")),
        venue=Venue(
            name=rink.get("name") or "Unknown venue",
            city=(rink.get("city") or "").title(),
            latitude=rink.get("latitude"),
            longitude=rink.get("longitude"),
        ),
    )
