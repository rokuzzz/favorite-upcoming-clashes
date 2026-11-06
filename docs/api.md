# REST API

The backend serves JSON under `/api`. Field names are camelCase; times are ISO 8601. Interactive documentation
(Swagger UI) is available at http://localhost:8000/docs while the backend is running.

| Method | Path | Description |
|---|---|---|
| GET | `/api/health` | Health check: `{"status": "ok"}` |
| GET | `/api/teams` | Liiga teams of the current season, sorted by name |
| GET | `/api/matches?team={id}&days={7\|14\|21}&include={sources}` | Upcoming games of a team within the time horizon (default 14 days), with optional data such as `include=weather` |
| GET | `/api/data-sources` | Optional data sources that `include` accepts |
| GET | `/api/preferences` | Saved preferences |
| PUT | `/api/preferences` | Replace saved preferences |

## GET /api/teams

```json
[
  { "id": "168761288:hifk", "name": "HIFK", "logoUrl": "https://cdn.builder.io/api/v1/image/assets%2F…" },
  { "id": "624554857:lukko", "name": "Lukko", "logoUrl": "https://cdn.builder.io/api/v1/image/assets%2F…" }
]
```

## GET /api/matches?team=624554857:lukko&days=7&include=weather

```json
{
  "team": { "id": "624554857:lukko", "name": "Lukko", "logoUrl": "https://…" },
  "horizonDays": 7,
  "included": ["weather"],
  "matches": [
    {
      "id": 2701442,
      "startUtc": "2026-11-11T16:30:00Z",
      "startLocal": "2026-11-11T18:30:00+02:00",
      "opponent": { "id": "859884935:kalpa", "name": "KalPa", "logoUrl": "https://…" },
      "isHome": true,
      "venue": { "name": "Rauman jäähalli / Äijänsuo Areena", "city": "Rauma", "latitude": 61.1203, "longitude": 21.501 },
      "weather": {
        "available": true,
        "message": null,
        "time": "2026-11-11T16:00:00Z",
        "temperatureC": 5.63,
        "precipitationMm": 0.0,
        "windSpeedMs": 3.6,
        "windDirectionDeg": 200.0,
        "weatherSymbol": 3
      }
    }
  ]
}
```

Only games that have not started, are between two Liiga teams and start within the horizon are returned, sorted by
start time. `included` lists the data sources that were applied; unknown names in `include` are ignored. Without
`include` the `weather` field is `null`. FMI forecasts about 10 days ahead; for later games `weather` is
`{"available": false, "message": "Forecast not yet available", …}`.

## GET /api/data-sources

```json
[{ "key": "weather", "label": "Weather forecast (FMI)" }]
```

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
