import httpx
import pytest
from fastapi.testclient import TestClient

from app.container import Services
from app.main import create_app
from app.repositories.preferences_repository import PreferencesRepository
from app.services.match_service import MatchService
from app.services.settings_service import SettingsService
from tests.test_match_service import NOW, FakeLiigaRepository


class BrokenLiigaRepository:
    async def get_teams(self):
        raise httpx.ConnectError("Liiga is down")


def make_services(tmp_path, liiga=None) -> Services:
    return Services(
        match_service=MatchService(liiga or FakeLiigaRepository(), clock=lambda: NOW),
        settings_service=SettingsService(PreferencesRepository(tmp_path / "preferences.json")),
    )


@pytest.fixture
def client(tmp_path):
    with TestClient(create_app(make_services(tmp_path))) as client:
        yield client


def test_teams(client):
    response = client.get("/api/teams")

    assert response.status_code == 200
    assert [t["id"] for t in response.json()] == ["kalpa", "lukko", "tps"]


def test_matches_returns_camel_case_json(client):
    response = client.get("/api/matches", params={"team": "lukko", "days": 7})

    assert response.status_code == 200
    body = response.json()
    assert body["horizonDays"] == 7
    assert body["matches"][0]["opponent"]["id"] == "tps"
    assert body["matches"][0]["isHome"] is False
    assert body["matches"][0]["startLocal"].endswith("+02:00")


@pytest.mark.parametrize(
    ("params", "status"),
    [
        ({"team": "nope", "days": 7}, 404),  # unknown team
        ({"team": "lukko", "days": 10}, 422),  # horizon not 7/14/21
        ({"days": 7}, 422),  # team missing
    ],
)
def test_matches_rejects_bad_input(client, params, status):
    assert client.get("/api/matches", params=params).status_code == status


def test_liiga_outage_becomes_502(tmp_path):
    with TestClient(create_app(make_services(tmp_path, BrokenLiigaRepository()))) as client:
        assert client.get("/api/teams").status_code == 502


def test_preferences_start_empty_and_saved_favourite_is_returned(client):
    assert client.get("/api/preferences").json() == {"favouriteTeamId": None}

    saved = client.put("/api/preferences", json={"favouriteTeamId": "lukko"})

    assert saved.status_code == 200
    assert client.get("/api/preferences").json() == {"favouriteTeamId": "lukko"}
    assert client.put("/api/preferences", json={"favouriteTeamId": None}).json() == {"favouriteTeamId": None}
