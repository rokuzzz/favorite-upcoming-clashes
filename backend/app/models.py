"""Domain models shared by all layers.

JSON field names are camelCase (for the TypeScript frontend); Python attributes stay snake_case.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class ApiModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        validate_by_name=True,
        validate_by_alias=True,
        serialize_by_alias=True,
        # Responses always contain every field (possibly null), so the schema marks them as required.
        json_schema_serialization_defaults_required=True,
    )


class Team(ApiModel):
    id: str
    name: str
    logo_url: str | None = None


class Venue(ApiModel):
    name: str
    city: str
    latitude: float | None = None
    longitude: float | None = None


class Match(ApiModel):
    """A scheduled Liiga game, independent of whose point of view we look at it from."""

    id: int
    start: datetime  # UTC
    home_team_id: str
    away_team_id: str
    venue: Venue
    started: bool = False
    ended: bool = False


class ForecastPoint(ApiModel):
    """One hourly value set from FMI. None means FMI returned NaN (no forecast yet)."""

    time: datetime
    temperature_c: float | None = None
    precipitation_mm: float | None = None
    wind_speed_ms: float | None = None
    wind_direction_deg: float | None = None
    weather_symbol: float | None = None


class WeatherForecast(ApiModel):
    """What the UI shows: either the values or available=False with a message."""

    available: bool
    message: str | None = None
    time: datetime | None = None
    temperature_c: float | None = None
    precipitation_mm: float | None = None
    wind_speed_ms: float | None = None
    wind_direction_deg: float | None = None
    weather_symbol: int | None = None

    @classmethod
    def unavailable(cls, message: str) -> "WeatherForecast":
        return cls(available=False, message=message)


class UpcomingMatch(ApiModel):
    """A match seen from the favourite team's point of view."""

    id: int
    start_utc: datetime
    start_local: datetime
    opponent: Team
    is_home: bool
    venue: Venue


class MatchesResponse(ApiModel):
    team: Team
    horizon_days: int
    matches: list[UpcomingMatch]


class Preferences(ApiModel):
    """What the user has saved. Owned by SettingsService."""

    favourite_team_id: str | None = None
