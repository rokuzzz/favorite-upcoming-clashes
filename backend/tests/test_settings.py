from app.models import Preferences
from app.repositories.preferences_repository import PreferencesRepository
from app.services.settings_service import SettingsService


def test_defaults_when_file_is_missing(tmp_path):
    assert PreferencesRepository(tmp_path / "missing.json").load() == Preferences()


def test_defaults_when_file_is_broken(tmp_path):
    path = tmp_path / "preferences.json"
    path.write_text("{not json", encoding="utf-8")

    assert PreferencesRepository(path).load() == Preferences()


def test_saved_preferences_survive_a_restart(tmp_path):
    path = tmp_path / "data" / "preferences.json"  # parent folder does not exist yet

    SettingsService(PreferencesRepository(path)).save(Preferences(favourite_team_id="624554857:lukko"))

    assert SettingsService(PreferencesRepository(path)).get().favourite_team_id == "624554857:lukko"
    assert '"favouriteTeamId": "624554857:lukko"' in path.read_text(encoding="utf-8")
