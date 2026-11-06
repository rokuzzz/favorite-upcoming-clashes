from collections.abc import Iterable
from datetime import datetime, timedelta

from app.models import ForecastPoint, WeatherForecast
from app.repositories.fmi_weather_repository import FmiWeatherRepository

FORECAST_NOT_AVAILABLE = "Forecast not yet available"


class WeatherService:
    """FMI forecast for a place at the hour a match starts."""

    def __init__(self, repository: FmiWeatherRepository) -> None:
        self._repository = repository

    async def get_forecast(self, latitude: float, longitude: float, at: datetime) -> WeatherForecast:
        hour = at.replace(minute=0, second=0, microsecond=0)
        points = await self._repository.get_hourly_forecast(latitude, longitude, hour, hour + timedelta(hours=1))
        point = select_forecast_hour(points, at)
        if point is None or point.temperature_c is None:
            # FMI only forecasts ~10 days ahead; beyond that it returns NaN values.
            return WeatherForecast.unavailable(FORECAST_NOT_AVAILABLE)
        return WeatherForecast(
            available=True,
            time=point.time,
            temperature_c=point.temperature_c,
            precipitation_mm=point.precipitation_mm,
            wind_speed_ms=point.wind_speed_ms,
            wind_direction_deg=point.wind_direction_deg,
            weather_symbol=round(point.weather_symbol) if point.weather_symbol is not None else None,
        )


def select_forecast_hour(points: Iterable[ForecastPoint], target: datetime) -> ForecastPoint | None:
    """The forecast step closest to target; on a tie (e.g. 18:30) the earlier hour wins."""
    return min(points, key=lambda p: (abs(p.time - target), p.time), default=None)
