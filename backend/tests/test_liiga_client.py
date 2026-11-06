from datetime import UTC, datetime

import httpx
import pytest
import respx

from app import config
from app.clients.liiga_client import LiigaClient, parse_match, parse_team

# Trimmed real responses (season 2027)
RAW_TEAM = {
    "teamId": "624554857:lukko",
    "teamName": "Lukko",
    "ranking": 1,
    "teamLogos": {"darkBg": "https://cdn/lukko-dark", "lightBg": "https://cdn/lukko-light"},
}
RAW_GAME = {
    "id": 2701477,
    "start": "2026-11-09T16:30:00Z",
    "homeTeamId": "651304385:tps",
    "awayTeamId": "859884935:kalpa",
    "started": False,
    "ended": False,
    "spectators": 0,
    "iceRink": {
        "id": 199,
        "name": "Turun Monitoimihalli Oy",
        "latitude": 60.4562,
        "longitude": 22.1869,
        "city": "TURKU",
    },
}


def test_parse_team_prefers_light_background_logo():
    team = parse_team(RAW_TEAM)

    assert (team.id, team.name, team.logo_url) == ("624554857:lukko", "Lukko", "https://cdn/lukko-light")


def test_parse_match_converts_to_domain_model():
    match = parse_match(RAW_GAME)

    assert match.id == 2701477
    assert match.start == datetime(2026, 11, 9, 16, 30, tzinfo=UTC)
    assert (match.home_team_id, match.away_team_id) == ("651304385:tps", "859884935:kalpa")
    assert (match.venue.name, match.venue.city) == ("Turun Monitoimihalli Oy", "Turku")
    assert (match.venue.latitude, match.venue.longitude) == (60.4562, 22.1869)


def test_parse_match_tolerates_missing_rink():
    match = parse_match({**RAW_GAME, "iceRink": None})

    assert (match.venue.name, match.venue.city, match.venue.latitude) == ("Unknown venue", "", None)


@respx.mock
async def test_fetch_teams_sends_browser_user_agent_and_season():
    route = respx.get(f"{config.LIIGA_BASE_URL}/standings/").mock(
        return_value=httpx.Response(200, json={"season": [RAW_TEAM], "playoffs": []})
    )

    async with httpx.AsyncClient() as http:
        teams = await LiigaClient(http).fetch_teams(2027)

    assert [t.name for t in teams] == ["Lukko"]
    request = route.calls.last.request
    assert request.url.params["season"] == "2027"
    assert request.headers["User-Agent"] == config.BROWSER_USER_AGENT


@respx.mock
async def test_fetch_schedule_passes_tournament_and_raises_on_http_error():
    route = respx.get(f"{config.LIIGA_BASE_URL}/schedule").mock(return_value=httpx.Response(200, json=[RAW_GAME]))

    async with httpx.AsyncClient() as http:
        client = LiigaClient(http)
        matches = await client.fetch_schedule(2027, "runkosarja")

        assert [m.id for m in matches] == [2701477]
        assert route.calls.last.request.url.params["tournament"] == "runkosarja"

        route.mock(return_value=httpx.Response(503))
        with pytest.raises(httpx.HTTPStatusError):
            await client.fetch_schedule(2027, "runkosarja")
