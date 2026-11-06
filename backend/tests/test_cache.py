import asyncio

from app import config
from app.models import Team
from app.repositories.cache import TtlCache
from app.repositories.liiga_repository import LiigaRepository


class FakeClock:
    """Time that only moves when the test says so."""

    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now


class CountingLoader:
    def __init__(self) -> None:
        self.calls = 0

    async def __call__(self) -> int:
        self.calls += 1
        await asyncio.sleep(0)  # give other coroutines a chance to run, like a real HTTP call
        return self.calls


async def test_value_is_reused_until_ttl_expires():
    clock, load = FakeClock(), CountingLoader()
    cache = TtlCache(clock)

    assert await cache.get_or_load("k", 60, load) == 1
    clock.now = 59
    assert await cache.get_or_load("k", 60, load) == 1  # still fresh: no new load
    clock.now = 60
    assert await cache.get_or_load("k", 60, load) == 2  # expired: loaded again


async def test_keys_are_cached_independently():
    load = CountingLoader()
    cache = TtlCache(FakeClock())

    await cache.get_or_load("a", 60, load)
    await cache.get_or_load("b", 60, load)

    assert load.calls == 2


async def test_concurrent_callers_share_one_load():
    load = CountingLoader()
    cache = TtlCache(FakeClock())

    results = await asyncio.gather(*(cache.get_or_load("k", 60, load) for _ in range(5)))

    assert results == [1, 1, 1, 1, 1]
    assert load.calls == 1


class FakeLiigaClient:
    def __init__(self) -> None:
        self.team_requests: list[int] = []

    async def fetch_teams(self, season: int) -> list[Team]:
        self.team_requests.append(season)
        return [Team(id="624554857:lukko", name="Lukko")]


async def test_repository_calls_liiga_once_while_cache_is_fresh():
    clock, client = FakeClock(), FakeLiigaClient()
    repository = LiigaRepository(client, TtlCache(clock), season=2027)

    await repository.get_teams()
    await repository.get_teams()
    clock.now = config.TEAMS_TTL_S
    await repository.get_teams()

    assert client.team_requests == [2027, 2027]
