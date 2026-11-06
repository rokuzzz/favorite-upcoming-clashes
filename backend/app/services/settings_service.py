from app.models import Preferences
from app.repositories.preferences_repository import PreferencesRepository


class SettingsService:
    """The only component that reads or writes user preferences."""

    def __init__(self, repository: PreferencesRepository) -> None:
        self._repository = repository

    def get(self) -> Preferences:
        return self._repository.load()

    def save(self, preferences: Preferences) -> Preferences:
        self._repository.save(preferences)
        return preferences
