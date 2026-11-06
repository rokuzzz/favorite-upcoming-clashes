# Architecture

The core of the application is a Python backend (FastAPI). It fetches data from external APIs, applies the business
logic and serves a small REST API. The React frontend only displays that data and never talks to external APIs directly.

## Layers

Each layer calls only the layer directly below it. The domain models in `backend/app/models.py` are shared by all
layers, so external data formats never leak past the API clients.

```
React UI          frontend/src            components → queries (TanStack Query) → api/client.ts
                       │  HTTP + JSON (/api/*)
API routes        app/api/routes.py       HTTP ↔ service calls, errors → status codes, no business logic
                       │
Services          app/services/           MatchService, SettingsService: business logic
                       │
Repositories      app/repositories/       LiigaRepository (in-memory cache), PreferencesRepository (JSON file)
                       │
API clients       app/clients/            LiigaClient: HTTP + conversion to domain models
                       │
External APIs                             liiga.fi (later: FMI, Digitraffic)
```

The design document (`designDocument.pdf`) shows the same structure: its *handlers* are the API clients, the *main
program* is the service layer, and *data processing and visualization* is split between the API routes and the React UI.

## Design patterns

| Pattern | Where | Why |
|---|---|---|
| **Adapter** | `app/clients/liiga_client.py` | Converts Liiga's JSON (`teamId`, `iceRink`, …) into our models (`Team`, `Match`, `Venue`). If Liiga changes its format, only this file changes. |
| **Proxy** (caching) | `app/repositories/liiga_repository.py`, `cache.py` | Same interface as the client, but answers from an in-memory TTL cache. Concurrent requests share a single API call. |
| **Facade** | `app/services/match_service.py` | One call — "upcoming matches of team X in the next N days" — hides filtering, the team's point of view and time zones. |
| **Repository** | `app/repositories/preferences_repository.py` | Hides how preferences are stored (a JSON file now, per-user storage later). |
| **Composition root / dependency injection** | `app/container.py`, `app/main.py` | The only place that creates concrete classes. Everything else receives its dependencies through the constructor, so tests can pass fakes. |
| **Generated API contract** | `frontend/openapi.json`, `frontend/src/api/schema.ts` | TypeScript types are generated from the backend models, so both sides always agree on the data format. |

## Example: `GET /api/matches?team=624554857:lukko&days=14`

1. `routes.list_matches` validates `days` (7, 14 or 21) and calls `MatchService.get_upcoming_matches`.
2. `MatchService` asks `LiigaRepository` for the teams and the season schedule. The repository returns cached data or
   calls `LiigaClient`, which fetches and converts Liiga's JSON.
3. `select_upcoming` keeps games of the team that have not started, are against Liiga teams and start within the horizon.
4. `to_upcoming_match` turns each game into the team's point of view: opponent, home/away, start time in Finnish time.
5. The route returns `MatchesResponse` as camelCase JSON; the React UI renders one `MatchCard` per match.

## Code structure

```
backend/app/
├── main.py              FastAPI app factory (create_app), lifespan with one shared HTTP client
├── __main__.py          dev server: `uv run python -m app`
├── container.py         composition root
├── config.py            URLs, season, cache lifetimes, time zone, preferences file
├── models.py            domain models (pydantic)
├── openapi.py           exports the OpenAPI schema for frontend type generation
├── api/routes.py        REST endpoints
├── services/            MatchService, SettingsService
├── repositories/        cache.py, LiigaRepository, PreferencesRepository
└── clients/             LiigaClient

frontend/src/
├── main.tsx             providers (TanStack Query)
├── App.tsx              the page: selection state and layout
├── api/                 client.ts (fetch), queries.ts (hooks), types.ts, schema.ts (generated)
├── components/          Controls, MatchCard (+ skeletons), ui/ (shadcn/ui, generated)
└── lib/                 utils.ts, format.ts (dates in Finnish time)
```

The frontend will move to feature folders (`src/features/matches`, `src/features/weather`, …) when more data sources
are added.

## Data handling

| Data | Source | Cached for |
|---|---|---|
| Teams | `GET liiga.fi/api/v2/standings/?season=2027` | 6 hours |
| Schedule | `GET liiga.fi/api/v2/schedule?tournament=runkosarja&season=2027` | 15 minutes |
| Favourite team | `backend/data/preferences.json` (not in git) | — |

- Times are kept in UTC inside the backend and converted to `Europe/Helsinki` only for display (`startLocal`, UI).
- The Liiga API is unofficial and undocumented; requests send a browser-like User-Agent.
- Preferences are written atomically (temporary file + rename), and a missing or broken file falls back to defaults.

## Tests

`cd backend && uv run pytest`. The tests use fakes and mocked HTTP (`respx`), so they run without network access. They
cover parsing Liiga responses, the cache (expiry, concurrent callers), match filtering and the team's point of view,
the REST endpoints and their error codes, preferences storage and the OpenAPI export.

## Planned extensions

- **More data per match** (weather from FMI, nearest road weather camera from Digitraffic). These will plug into
  `MatchService` as independent data sources, so adding a source does not change the existing code.
- **Tickets** (Lippu.fi in the design document). Liiga's schedule already contains a `buyTicketsUrl` for each game.
- **Charts and a map** (Recharts, Leaflet) for the required graphical presentation.
