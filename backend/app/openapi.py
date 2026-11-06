"""Export the OpenAPI schema without running the server: `uv run python -m app.openapi <output.json>`.

The frontend generates its TypeScript API types from this file (`npm run gen:api`).
"""

import json
import sys
from pathlib import Path

from app.main import app


def export_schema(path: Path) -> None:
    path.write_text(json.dumps(app.openapi(), indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python -m app.openapi <output.json>")
    export_schema(Path(sys.argv[1]))
