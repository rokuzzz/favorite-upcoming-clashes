from datetime import UTC, datetime, timedelta

import pytest

from app.models import Match, Team, Venue, WeatherForecast
from app.services.match_service import MatchService, UnknownTeamError, select_upcoming

NOW = datetime(2026, 11, 6, 12, 0, tzinfo=UTC)
LIIGA_TEAMS = {"lukko", "tps", "kalpa"}


def make_match(match_id: int, home: str, away: str, days_from_now: float, **flags: bool) -> Match:
    return Match(
        id=match_id,
        start=NOW + timedelta(days=days_from_now),
        home_team_id=home,
        away_team_id=away,
        venue=Venue(name="Areena", city="Rauma", latitude=61.12, longitude=21.50),
        **flags,
    )


def test_keeps_only_future_games_of_the_team_within_horizon_sorted_by_start():
    schedule = [
        make_match(1, "tps", "lukko", 5),
        make_match(2, "lukko", "kalpa", 1),
        make_match(3, "tps", "kalpa", 2),  # Lukko not playing
        make_match(4, "lukko", "tps", 8),  # beyond a 7-day horizon
        make_match(5, "lukko", "tps", -1, started=True, ended=True),  # already played
        make_match(6, "kalpa", "lukko", 0.1, started=True),  # in progress
        make_match(7, "lukko", "foreign-team", 3),  # e.g. a CHL game against a non-Liiga team
    ]

    result = select_upcoming(schedule, "lukko", LIIGA_TEAMS, NOW, horizon_days=7)

    assert [m.id for m in result] == [2, 1]


def test_horizon_end_is_exclusive():
    schedule = [make_match(1, "lukko", "tps", 7), make_match(2, "lukko", "tps", 6.99)]

    assert [m.id for m in select_upcoming(schedule, "lukko", LIIGA_TEAMS, NOW, 7)] == [2]


class FakeLiigaRepository:
    async def get_teams(self):
        return [Team(id=team_id, name=team_id.upper()) for team_id in LIIGA_TEAMS]

    async def get_schedule(self):
        return [make_match(1, "tps", "lukko", 1), make_match(2, "lukko", "kalpa", 2)]


async def test_builds_matches_from_the_team_point_of_view():
    service = MatchService(FakeLiigaRepository(), clock=lambda: NOW)

    response = await service.get_upcoming_matches("lukko", 7)

    away_game, home_game = response.matches
    assert (away_game.is_home, away_game.opponent.id) == (False, "tps")
    assert (home_game.is_home, home_game.opponent.id) == (True, "kalpa")
    assert away_game.start_local.utcoffset() == timedelta(hours=2)  # Finnish winter time
    assert away_game.start_local == away_game.start_utc  # same moment, different clock
    assert (response.team.name, response.horizon_days) == ("LUKKO", 7)


async def test_unknown_team_raises():
    with pytest.raises(UnknownTeamError):
        await MatchService(FakeLiigaRepository(), clock=lambda: NOW).get_upcoming_matches("nope", 7)


async def test_teams_are_sorted_by_name():
    teams = await MatchService(FakeLiigaRepository()).get_teams()

    assert [t.name for t in teams] == ["KALPA", "LUKKO", "TPS"]


class FakeWeatherSource:
    key = "weather"
    label = "Fake weather"

    def __init__(self) -> None:
        self.asked_for: list[int] = []

    async def fetch(self, match):
        self.asked_for.append(match.id)
        return WeatherForecast.unavailable(f"forecast for {match.id}")


class BrokenSource:
    key = "weather"
    label = "Always fails"

    async def fetch(self, match):
        raise RuntimeError("FMI is down")


async def test_requested_data_source_fills_its_field_for_every_match():
    source = FakeWeatherSource()
    service = MatchService(FakeLiigaRepository(), [source], clock=lambda: NOW)

    response = await service.get_upcoming_matches("lukko", 7, include={"weather"})

    assert response.included == ["weather"]
    assert [m.weather.message for m in response.matches] == ["forecast for 1", "forecast for 2"]
    assert sorted(source.asked_for) == [1, 2]


async def test_data_sources_are_only_asked_when_requested():
    source = FakeWeatherSource()
    service = MatchService(FakeLiigaRepository(), [source], clock=lambda: NOW)

    response = await service.get_upcoming_matches("lukko", 7)

    assert response.included == []
    assert source.asked_for == []
    assert all(m.weather is None for m in response.matches)


async def test_failing_data_source_does_not_break_the_match_list():
    service = MatchService(FakeLiigaRepository(), [BrokenSource()], clock=lambda: NOW)

    response = await service.get_upcoming_matches("lukko", 7, include={"weather"})

    assert len(response.matches) == 2
    assert all(m.weather is None for m in response.matches)


def test_data_sources_are_listed_for_the_ui():
    service = MatchService(FakeLiigaRepository(), [FakeWeatherSource()])

    assert [(s.key, s.label) for s in service.data_sources] == [("weather", "Fake weather")]
