"""Central configuration: external API endpoints, season and cache lifetimes."""

from pathlib import Path
from zoneinfo import ZoneInfo

LIIGA_BASE_URL = "https://www.liiga.fi/api/v2"
LIIGA_SEASON = 2027  # season 2026-27 is named after the year it ends
LIIGA_TOURNAMENT = "runkosarja"  # regular season

# Liiga rejects requests that do not look like they come from a browser.
BROWSER_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
)

HTTP_TIMEOUT_S = 20.0
LOCAL_TZ = ZoneInfo("Europe/Helsinki")

ALLOWED_HORIZONS = (7, 14, 21)

# Cache lifetimes (seconds)
TEAMS_TTL_S = 6 * 3600
SCHEDULE_TTL_S = 15 * 60

# User preferences (favourite team) are stored in this JSON file.
PREFERENCES_FILE = Path(__file__).resolve().parent.parent / "data" / "preferences.json"
