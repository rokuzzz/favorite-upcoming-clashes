# Favorite Upcoming Clashes

COMP.SE.110 Software Design — group assignment (group *remote-passing-grade*).

A web app for Liiga ice hockey fans: pick a team and a time horizon and see its upcoming games — opponent, home or
away, arena and start time in Finnish time. Weather forecasts and road weather cameras near the arena are next.

The core is a Python backend (FastAPI); the React frontend only displays its data.

## User stories

| | As a hockey fan, I want to… | so that… |
|---|---|---|
| ✅ | choose any Liiga team and see its upcoming games | I know when and where it plays |
| ✅ | choose how far ahead to look (7, 14 or 21 days) | I see only the period I am planning for |
| ✅ | see the opponent, home or away, the arena and city, and the start time in Finnish time | I can plan going to the game |
| ✅ | save my favourite team | the app opens with its games straight away |
| 🔜 | see the weather forecast at the arena at game time (FMI) | I know how to dress and travel |
| 🔜 | see the latest image from the road weather camera nearest to the arena (Digitraffic) | I see the road conditions on the way |
| 🔜 | choose which extra data is shown | the page shows only what I care about |
| 🔜 | see the data as a chart and the arenas on a map | I get the overview at a glance |
| 💡 | follow several favourite teams in a "My teams" tab | I see all games I care about in one list |
| 💡 | log in | my favourites follow me to other devices |
| 💡 | open a team page with standings, form and past results | I know how the team is doing |
| 💡 | open a match page with a link to buy tickets | I can get to the game easily |

✅ done · 🔜 planned (required by the assignment) · 💡 idea for later

## Documentation

- [Architecture](docs/architecture.md): layers, design patterns, code structure, data handling, tests
- [REST API](docs/api.md): endpoints with examples
- [Design document](docs/designDocument.pdf) and the earlier [prototype](docs/software-desig-prototype.rar)

## Requirements

- [uv](https://docs.astral.sh/uv/) (Python package and project manager; installs Python 3.12 automatically if missing)
- [Node.js](https://nodejs.org/) 22+ with npm

Install uv once:

```powershell
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Quick start

From the repository root:

```bash
npm install      # root tools (runs backend and frontend together)
npm run setup    # backend dependencies, git hooks, frontend dependencies
npm run dev      # backend on :8000 and frontend on :5173
```

Open http://localhost:5173. The frontend forwards `/api/*` requests to the backend.

| Command | What it does |
|---|---|
| `npm run dev` | Start backend and frontend together |
| `npm run dev:backend` / `npm run dev:frontend` | Start only one of them |
| `npm test` | Run backend tests |
| `npm run gen:api` | Regenerate frontend API types after changing backend models |

## Backend

Python 3.12, FastAPI. Commands are run in the `backend/` folder.

```bash
cd backend
uv sync                      # create .venv and install dependencies
uv run pre-commit install    # enable git hooks (once per clone)
uv run python -m app         # dev server with auto-reload on :8000
```

- Health check: http://localhost:8000/api/health
- API docs (Swagger): http://localhost:8000/docs

Tests, lint and format:

```bash
uv run pytest
uv run ruff check --fix
uv run ruff format
```

## Frontend

React, TypeScript, Vite, Tailwind CSS, shadcn/ui. Commands are run in the `frontend/` folder.

```bash
cd frontend
npm install
npm run dev          # dev server on :5173 (the backend must be running for data)
npm run build        # type-check and production build
npm run lint         # oxlint
npm run format       # Prettier
npm run gen:api      # regenerate src/api/schema.ts from the backend's OpenAPI schema
```

API types in `src/api/schema.ts` are generated from the backend models, so backend and frontend always agree on the
data format. Run `npm run gen:api` after changing a model in `backend/app/models.py`.

## Tech stack

| Part | Tools (version used) |
|---|---|
| Backend | Python 3.12, FastAPI 0.162, uvicorn 0.54, httpx 0.28, pydantic 2.14 |
| Backend tooling | uv 0.13, pytest 9.2, respx 0.23, ruff 0.17 |
| Frontend | React 19.3, TypeScript 7.0, Vite 8.3, Tailwind CSS 4.3, shadcn/ui (Base UI), TanStack Query 5 |
| Frontend tooling | oxlint, Prettier, openapi-typescript 7.13 |
| Repository | pre-commit (ruff, Prettier, oxlint, Conventional Commits) |

Exact versions are locked in `backend/uv.lock` and `frontend/package-lock.json`.

## Commits

Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/), e.g. `feat(backend): add Liiga client`.
Git hooks (pre-commit) check the message format and run ruff, Prettier and oxlint on staged files before each commit.
