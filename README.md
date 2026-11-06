# Favorite Upcoming Clashes

COMP.SE.110 Software Design — group assignment (group *remote-passing-grade*).

Upcoming Liiga games of your favourite team with the weather forecast and the nearest road weather camera.

## Requirements

- [uv](https://docs.astral.sh/uv/) (Python package and project manager; installs Python 3.12 automatically if missing)
- [Node.js](https://nodejs.org/) 20+ with npm

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

## Commits

Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/), e.g. `feat(backend): add Liiga client`.
Git hooks (pre-commit) check the message format and run ruff, Prettier and oxlint on staged files before each commit.
