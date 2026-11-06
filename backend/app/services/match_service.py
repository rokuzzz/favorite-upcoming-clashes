"""MatchService: the facade the API layer talks to for everything match-related."""

from collections.abc import Callable, Collection, Iterable
from datetime import UTC, datetime, timedelta

from app import config
from app.models import Match, MatchesResponse, Team, UpcomingMatch
from app.repositories.liiga_repository import LiigaRepository


class UnknownTeamError(LookupError):
    pass


class MatchService:
    def __init__(
        self,
        liiga: LiigaRepository,
        clock: Callable[[], datetime] = lambda: datetime.now(UTC),
    ) -> None:
        self._liiga = liiga
        self._clock = clock

    async def get_teams(self) -> list[Team]:
        return sorted(await self._liiga.get_teams(), key=lambda t: t.name)

    async def get_upcoming_matches(self, team_id: str, horizon_days: int) -> MatchesResponse:
        """Upcoming matches of team_id within the next horizon_days."""
        teams = {team.id: team for team in await self._liiga.get_teams()}
        if team_id not in teams:
            raise UnknownTeamError(team_id)

        schedule = await self._liiga.get_schedule()
        selected = select_upcoming(schedule, team_id, teams.keys(), self._clock(), horizon_days)
        return MatchesResponse(
            team=teams[team_id],
            horizon_days=horizon_days,
            matches=[to_upcoming_match(match, team_id, teams) for match in selected],
        )


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
