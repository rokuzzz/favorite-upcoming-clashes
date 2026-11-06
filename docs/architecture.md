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
Services          app/services/           MatchService, WeatherService, SettingsService: business logic
                       │
Repositories      app/repositories/       LiigaRepository, FmiWeatherRepository (in-memory cache), PreferencesRepository
                       │
API clients       app/clients/            LiigaClient, FmiClient: HTTP + conversion to domain models
                       │
External APIs                             liiga.fi, opendata.fmi.fi (later: Digitraffic)
```

The design document (`designDocument.pdf`) shows the same structure: its *handlers* are the API clients, the *main
program* is the service layer, and *data processing and visualization* is split between the API routes and the React UI.

## Design patterns

| Pattern | Where | Why |
|---|---|---|
| **Adapter** | `app/clients/` | `LiigaClient` converts Liiga's JSON (`teamId`, `iceRink`, …) and `FmiClient` FMI's WFS XML into our models. If an external format changes, only its client changes. |
| **Proxy** (caching) | `app/repositories/liiga_repository.py`, `fmi_weather_repository.py`, `cache.py` | Same interface as the client, but answers from an in-memory TTL cache. Concurrent requests share a single API call. |
| **Facade** | `app/services/match_service.py` | One call — "upcoming matches of team X in the next N days" — hides filtering, the team's point of view and time zones. |
| **Strategy / plug-in** | `MatchEnricher` in `app/services/match_service.py`, `WeatherService` | An optional data source per match is a class with `key`, `label` and `fetch(match)`. `MatchService` asks the requested sources in parallel; a failing source leaves only its field empty. A new source is registered in `container.py` without changing `MatchService`. |
| **Repository** | `app/repositories/preferences_repository.py` | Hides how preferences are stored (a JSON file now, per-user storage later). |
| **Composition root / dependency injection** | `app/container.py`, `app/main.py` | The only place that creates concrete classes. Everything else receives its dependencies through the constructor, so tests can pass fakes. |
| **Generated API contract** | `frontend/openapi.json`, `frontend/src/api/schema.ts` | TypeScript types are generated from the backend models, so both sides always agree on the data format. |

## Example: `GET /api/matches?team=624554857:lukko&days=14&include=weather`

1. `routes.list_matches` validates `days` (7, 14 or 21) and calls `MatchService.get_upcoming_matches`.
2. `MatchService` asks `LiigaRepository` for the teams and the season schedule. The repository returns cached data or
   calls `LiigaClient`, which fetches and converts Liiga's JSON.
3. `select_upcoming` keeps games of the team that have not started, are against Liiga teams and start within the horizon.
4. `to_upcoming_match` turns each game into the team's point of view: opponent, home/away, start time in Finnish time.
5. Each requested data source (here `WeatherService`) fills its field for every match in parallel: the FMI forecast
   at the arena for the hour the game starts, or "Forecast not yet available" beyond FMI's ~10-day range.
6. The route returns `MatchesResponse` as camelCase JSON; the React UI renders one `MatchCard` per match.

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
├── services/            MatchService, WeatherService, SettingsService
├── repositories/        cache.py, LiigaRepository, FmiWeatherRepository, PreferencesRepository
└── clients/             LiigaClient, FmiClient

frontend/src/
├── main.tsx             providers (TanStack Query)
├── App.tsx              the page: selection state and layout
├── api/                 client.ts (fetch), types.ts, schema.ts (generated): shared by all features
├── features/            one folder per feature: components + TanStack Query hooks
│   ├── matches/         Controls, MatchCard (+ skeletons), useMatches, dates in Finnish time
│   ├── teams/           useTeams
│   ├── preferences/     usePreferences, useSavePreferences
│   └── weather/         WeatherInfo, FMI weather symbols
├── components/ui/       shadcn/ui components (generated)
└── lib/                 utils.ts
```

A new data source gets its own feature folder, e.g. `features/cameras/`.

## Data handling

| Data | Source | Cached for |
|---|---|---|
| Teams | `GET liiga.fi/api/v2/standings/?season=2027` | 6 hours |
| Schedule | `GET liiga.fi/api/v2/schedule?tournament=runkosarja&season=2027` | 15 minutes |
| Weather forecast | FMI WFS `fmi::forecast::edited::weather::scandinavia::point::simple` (CC BY 4.0) | 1 hour per arena and hour |
| Favourite team | `backend/data/preferences.json` (not in git) | — |

- Times are kept in UTC inside the backend and converted to `Europe/Helsinki` only for display (`startLocal`, UI).
- The Liiga API is unofficial and undocumented; requests send a browser-like User-Agent.
- Preferences are written atomically (temporary file + rename), and a missing or broken file falls back to defaults.

## Tests

`cd backend && uv run pytest`. The tests use fakes and mocked HTTP (`respx`), so they run without network access. They
cover parsing Liiga responses, the cache (expiry, concurrent callers), match filtering and the team's point of view,
the REST endpoints and their error codes, preferences storage and the OpenAPI export.

## Planned extensions

- **Nearest road weather camera** (Digitraffic) as the next `MatchEnricher` data source, and letting the user choose
  which data sources are shown (`GET /api/data-sources`).
- **Tickets** (Lippu.fi in the design document). Liiga's schedule already contains a `buyTicketsUrl` for each game.
- **Charts and a map** (Recharts, Leaflet) for the required graphical presentation.
