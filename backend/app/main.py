"""FastAPI application entry point: `uvicorn app.main:app --reload`."""

from fastapi import FastAPI

app = FastAPI(title="Favorite Upcoming Clashes", version="0.1.0")


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
