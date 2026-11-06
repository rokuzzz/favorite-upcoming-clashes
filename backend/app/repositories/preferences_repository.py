import logging
import os
from pathlib import Path

from app.models import Preferences

log = logging.getLogger(__name__)


class PreferencesRepository:
    """Stores preferences in a JSON file. A missing or broken file means default preferences."""

    def __init__(self, path: Path) -> None:
        self._path = path

    def load(self) -> Preferences:
        try:
            return Preferences.model_validate_json(self._path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return Preferences()
        except ValueError:  # invalid JSON or values; pydantic's ValidationError is a ValueError
            log.warning("Ignoring invalid preferences file %s", self._path)
            return Preferences()

    def save(self, preferences: Preferences) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        # Write to a temp file and rename, so a crash never leaves a half-written file.
        tmp_path = self._path.with_suffix(".tmp")
        tmp_path.write_text(preferences.model_dump_json(indent=2), encoding="utf-8")
        os.replace(tmp_path, self._path)
