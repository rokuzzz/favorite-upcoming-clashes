# REST API

The backend serves JSON under `/api`. Field names are camelCase; times are ISO 8601. Interactive documentation
(Swagger UI) is available at http://localhost:8000/docs while the backend is running.

| Method | Path | Description |
|---|---|---|
| GET | `/api/health` | Health check: `{"status": "ok"}` |
| GET | `/api/teams` | Liiga teams of the current season, sorted by name |
| GET | `/api/matches?team={id}&days={7\|14\|21}` | Upcoming games of a team within the time horizon (default 14 days) |
| GET | `/api/preferences` | Saved preferences |
| PUT | `/api/preferences` | Replace saved preferences |

## GET /api/teams

```json
[
  { "id": "168761288:hifk", "name": "HIFK", "logoUrl": "https://cdn.builder.io/api/v1/image/assets%2F…" },
  { "id": "624554857:lukko", "name": "Lukko", "logoUrl": "https://cdn.builder.io/api/v1/image/assets%2F…" }
]
```

## GET /api/matches?team=624554857:lukko&days=7

```json
{
  "team": { "id": "624554857:lukko", "name": "Lukko", "logoUrl": "https://…" },
  "horizonDays": 7,
  "matches": [
    {
      "id": 2701442,
      "startUtc": "2026-11-11T16:30:00Z",
      "startLocal": "2026-11-11T18:30:00+02:00",
      "opponent": { "id": "859884935:kalpa", "name": "KalPa", "logoUrl": "https://…" },
      "isHome": true,
      "venue": { "name": "Rauman jäähalli / Äijänsuo Areena", "city": "Rauma", "latitude": 61.1203, "longitude": 21.501 }
    }
  ]
}
```

Only games that have not started, are between two Liiga teams and start within the horizon are returned, sorted by
start time.

## GET / PUT /api/preferences

```json
{ "favouriteTeamId": "624554857:lukko" }
```

`favouriteTeamId` is `null` when no favourite team is saved. `PUT` replaces the stored preferences and returns them.

## Errors

Errors have the FastAPI shape `{"detail": "…"}`.

| Status | When |
|---|---|
| 404 | `team` is not a Liiga team (`Unknown team: …`) |
| 422 | Invalid input, e.g. `days` is not 7, 14 or 21, or `team` is missing |
| 502 | The Liiga API is unavailable |
