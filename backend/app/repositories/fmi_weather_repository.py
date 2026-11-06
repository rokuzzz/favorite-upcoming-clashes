from datetime import datetime

from app import config
from app.clients.fmi_client import FmiClient
from app.models import ForecastPoint
from app.repositories.cache import TtlCache


class FmiWeatherRepository:
    """Caching proxy in front of FmiClient. Games at the same rink and hour share one request."""

    def __init__(self, client: FmiClient, cache: TtlCache) -> None:
        self._client = client
        self._cache = cache

    async def get_hourly_forecast(
        self, latitude: float, longitude: float, start: datetime, end: datetime
    ) -> list[ForecastPoint]:
        key = ("fmi-forecast", round(latitude, 4), round(longitude, 4), start, end)
        return await self._cache.get_or_load(
            key,
            config.FORECAST_TTL_S,
            lambda: self._client.fetch_point_forecast(latitude, longitude, start, end),
        )
