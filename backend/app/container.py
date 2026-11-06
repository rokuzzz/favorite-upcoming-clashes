"""Composition root: the only place that knows which concrete classes are wired together."""

from dataclasses import dataclass

import httpx

from app.clients.liiga_client import LiigaClient
from app.repositories.cache import TtlCache
from app.repositories.liiga_repository import LiigaRepository
from app.services.match_service import MatchService


@dataclass
class Services:
    match_service: MatchService


def build_services(http: httpx.AsyncClient) -> Services:
    cache = TtlCache()
    liiga = LiigaRepository(LiigaClient(http), cache)
    return Services(match_service=MatchService(liiga))
