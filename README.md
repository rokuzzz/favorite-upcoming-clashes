# Favorite Upcoming Clashes

COMP.SE.110 Software Design — group assignment (group *remote-passing-grade*).

Upcoming Liiga games of your favourite team with the weather forecast and the nearest road weather camera.

## Requirements

- [uv](https://docs.astral.sh/uv/) (Python package and project manager; installs Python 3.12 automatically if missing)

Install uv once:

```powershell
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Backend

All commands are run in the `backend/` folder.

```bash
cd backend
uv sync                      # create .venv and install dependencies
uv run pre-commit install    # enable git hooks (once per clone)
```

Run the server:

```bash
uv run uvicorn app.main:app --reload --port 8000
```

- Health check: http://localhost:8000/api/health
- API docs (Swagger): http://localhost:8000/docs

Tests, lint and format:

```bash
uv run pytest
uv run ruff check --fix
uv run ruff format
```

## Commits

Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/), e.g. `feat(backend): add Liiga client`.
The git hooks check this, and run ruff on staged Python files before each commit.
