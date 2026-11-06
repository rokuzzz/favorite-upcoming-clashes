"""MatchService: the facade the API layer talks to for everything match-related."""

import asyncio
import logging
from collections.abc import Callable, Collection, Iterable, Sequence
from datetime import UTC, datetime, timedelta
from typing import Any, Protocol

from app import config
from app.models import DataSource, Match, MatchesResponse, Team, UpcomingMatch
from app.repositories.liiga_repository import LiigaRepository

log = logging.getLogger(__name__)


class UnknownTeamError(LookupError):
    pass


class MatchEnricher(Protocol):
    """A data source that fills one optional field of each UpcomingMatch.

    To add a new data source: write a service with `key` (the UpcomingMatch field it fills),
    `label` and `fetch()`, then register it in app/container.py. MatchService needs no change.
    """

    key: str
    label: str

    async def fetch(self, match: UpcomingMatch) -> Any: ...


class MatchService:
    def __init__(
        self,
        liiga: LiigaRepository,
        enrichers: Sequence[MatchEnricher] = (),
        clock: Callable[[], datetime] = lambda: datetime.now(UTC),
    ) -> None:
        self._liiga = liiga
        self._enrichers = list(enrichers)
        self._clock = clock

    @property
    def data_sources(self) -> list[DataSource]:
        return [DataSource(key=e.key, label=e.label) for e in self._enrichers]

    async def get_teams(self) -> list[Team]:
        return sorted(await self._liiga.get_teams(), key=lambda t: t.name)

    async def get_upcoming_matches(
        self, team_id: str, horizon_days: int, include: Collection[str] = ()
    ) -> MatchesResponse:
        """Upcoming matches of team_id within the next horizon_days, with data from the sources listed in include."""
        teams = {team.id: team for team in await self._liiga.get_teams()}
        if team_id not in teams:
            raise UnknownTeamError(team_id)

        schedule = await self._liiga.get_schedule()
        selected = select_upcoming(schedule, team_id, teams.keys(), self._clock(), horizon_days)
        matches = [to_upcoming_match(match, team_id, teams) for match in selected]

        enrichers = [e for e in self._enrichers if e.key in include]
        enriched = await asyncio.gather(*(self._enrich(m, enrichers) for m in matches))
        return MatchesResponse(
            team=teams[team_id],
            horizon_days=horizon_days,
            included=[e.key for e in enrichers],
            matches=list(enriched),
        )

    async def _enrich(self, match: UpcomingMatch, enrichers: list[MatchEnricher]) -> UpcomingMatch:
        """Ask every data source for this match in parallel; a failing source leaves its field empty."""
        results = await asyncio.gather(*(e.fetch(match) for e in enrichers), return_exceptions=True)
        update = {}
        for enricher, result in zip(enrichers, results, strict=True):
            if isinstance(result, Exception):
                log.warning("Data source %s failed for match %s: %r", enricher.key, match.id, result)
                continue
            update[enricher.key] = result
        return match.model_copy(update=update)


def select_upcoming(
    schedule: Iterable[Match],
    team_id: str,
    liiga_team_ids: Collection[str],
    now: datetime,
    horizon_days: int,
) -> list[Match]:
    """Not-yet-started Liiga-vs-Liiga games of team_id starting in [now, now + horizon), by start time."""
    until = now + timedelta(days=horizon_days)
    return sorted(
        (
            m
            for m in schedule
            if not m.started
            and not m.ended
            and team_id in (m.home_team_id, m.away_team_id)
            and m.home_team_id in liiga_team_ids
            and m.away_team_id in liiga_team_ids
            and now <= m.start < until
        ),
        key=lambda m: m.start,
    )


def to_upcoming_match(match: Match, team_id: str, teams: dict[str, Team]) -> UpcomingMatch:
    is_home = match.home_team_id == team_id
    opponent_id = match.away_team_id if is_home else match.home_team_id
    return UpcomingMatch(
        id=match.id,
        start_utc=match.start,
        start_local=match.start.astimezone(config.LOCAL_TZ),
        opponent=teams[opponent_id],
        is_home=is_home,
        venue=match.venue,
    )
