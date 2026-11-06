from app import config
from app.clients.liiga_client import LiigaClient
from app.models import Match, Team
from app.repositories.cache import TtlCache


class LiigaRepository:
    """Caching proxy in front of LiigaClient: same data, far fewer HTTP calls."""

    def __init__(
        self,
        client: LiigaClient,
        cache: TtlCache,
        season: int = config.LIIGA_SEASON,
        tournament: str = config.LIIGA_TOURNAMENT,
    ) -> None:
        self._client = client
        self._cache = cache
        self._season = season
        self._tournament = tournament

    async def get_teams(self) -> list[Team]:
        return await self._cache.get_or_load(
            ("liiga-teams", self._season),
            config.TEAMS_TTL_S,
            lambda: self._client.fetch_teams(self._season),
        )

    async def get_schedule(self) -> list[Match]:
        return await self._cache.get_or_load(
            ("liiga-schedule", self._season, self._tournament),
            config.SCHEDULE_TTL_S,
            lambda: self._client.fetch_schedule(self._season, self._tournament),
        )
