"""Development server: `uv run python -m app` (auto-reloads on code changes)."""

import uvicorn

if __name__ == "__main__":
    # Watch only our code: changes inside .venv (e.g. `uv add`) must not trigger reloads.
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True, reload_dirs=["app"])
