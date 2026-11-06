"""Composition root: the only place that knows which concrete classes are wired together."""

from dataclasses import dataclass
from pathlib import Path

import httpx

from app import config
from app.clients.fmi_client import FmiClient
from app.clients.liiga_client import LiigaClient
from app.repositories.cache import TtlCache
from app.repositories.fmi_weather_repository import FmiWeatherRepository
from app.repositories.liiga_repository import LiigaRepository
from app.repositories.preferences_repository import PreferencesRepository
from app.services.match_service import MatchService
from app.services.settings_service import SettingsService
from app.services.weather_service import WeatherService


@dataclass
class Services:
    match_service: MatchService
    settings_service: SettingsService


def build_services(http: httpx.AsyncClient, preferences_file: Path = config.PREFERENCES_FILE) -> Services:
    cache = TtlCache()
    liiga = LiigaRepository(LiigaClient(http), cache)
    weather = WeatherService(FmiWeatherRepository(FmiClient(http), cache))
    return Services(
        # Optional data sources per match. A new source is added to this list; MatchService does not change.
        match_service=MatchService(liiga, enrichers=[weather]),
        settings_service=SettingsService(PreferencesRepository(preferences_file)),
    )
