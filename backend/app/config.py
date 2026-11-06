"""Central configuration: external API endpoints and request settings."""

LIIGA_BASE_URL = "https://www.liiga.fi/api/v2"

# Liiga rejects requests that do not look like they come from a browser.
BROWSER_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
)
