from datetime import UTC, datetime

from app.models import ForecastPoint, Team, UpcomingMatch, Venue
from app.repositories.cache import TtlCache
from app.repositories.fmi_weather_repository import FmiWeatherRepository
from app.services.weather_service import FORECAST_NOT_AVAILABLE, WeatherService, select_forecast_hour

RAUMA = (61.1203, 21.501)


def at(hour: int, minute: int = 0) -> datetime:
    return datetime(2026, 11, 11, hour, minute, tzinfo=UTC)


class FakeFmiClient:
    """Returns the given hourly points and records every request."""

    def __init__(self, points: list[ForecastPoint]) -> None:
        self.points = points
        self.requests: list[tuple] = []

    async def fetch_point_forecast(self, latitude, longitude, start, end):
        self.requests.append((latitude, longitude, start, end))
        return self.points


def make_service(points: list[ForecastPoint]) -> tuple[WeatherService, FakeFmiClient]:
    client = FakeFmiClient(points)
    return WeatherService(FmiWeatherRepository(client, TtlCache())), client


def test_select_forecast_hour_picks_nearest_and_earlier_on_tie():
    points = [ForecastPoint(time=at(h), temperature_c=float(h)) for h in (16, 17, 18)]

    assert select_forecast_hour(points, at(16, 40)).time == at(17)
    assert select_forecast_hour(points, at(16, 30)).time == at(16)
    assert select_forecast_hour(points, at(17)).time == at(17)
    assert select_forecast_hour([], at(17)) is None


async def test_forecast_for_match_start_hour():
    service, client = make_service(
        [
            ForecastPoint(time=at(16), temperature_c=-1.5, wind_speed_ms=4.0, weather_symbol=3.0),
            ForecastPoint(time=at(17), temperature_c=-2.0),
        ]
    )

    forecast = await service.get_forecast(*RAUMA, at(16, 10))

    assert (forecast.available, forecast.temperature_c, forecast.wind_speed_ms, forecast.weather_symbol) == (
        True,
        -1.5,
        4.0,
        3,  # FMI sends symbols as floats ("3.0"); we expose an integer code
    )
    assert client.requests == [(*RAUMA, at(16), at(17))]  # asks for the start hour and the next one


async def test_unavailable_when_fmi_has_no_forecast_yet():
    service, _ = make_service([ForecastPoint(time=at(16)), ForecastPoint(time=at(17))])  # NaN -> None

    forecast = await service.get_forecast(*RAUMA, at(16))

    assert (forecast.available, forecast.message) == (False, FORECAST_NOT_AVAILABLE)


async def test_games_at_the_same_rink_and_hour_share_one_request():
    service, client = make_service([ForecastPoint(time=at(16), temperature_c=1.0)])

    await service.get_forecast(*RAUMA, at(16, 30))
    await service.get_forecast(*RAUMA, at(16, 0))

    assert len(client.requests) == 1


async def test_match_without_arena_coordinates_has_no_forecast():
    service, client = make_service([])
    match = UpcomingMatch(
        id=1,
        start_utc=at(16),
        start_local=at(16),
        opponent=Team(id="tps", name="TPS"),
        is_home=True,
        venue=Venue(name="Unknown venue", city=""),
    )

    forecast = await service.fetch(match)

    assert forecast.available is False
    assert client.requests == []
