"""Adapter for the FMI open data WFS point forecast."""

import math
import xml.etree.ElementTree as ET
from datetime import UTC, datetime

import httpx

from app import config
from app.models import ForecastPoint

_NS = {"wfs": "http://www.opengis.net/wfs/2.0", "BsWfs": "http://xml.fmi.fi/schema/wfs/2.0"}

# FMI parameter name -> ForecastPoint field
_PARAMETERS = {
    "Temperature": "temperature_c",
    "Precipitation1h": "precipitation_mm",
    "WindSpeedMS": "wind_speed_ms",
    "WindDirection": "wind_direction_deg",
    "WeatherSymbol3": "weather_symbol",
}


class FmiClient:
    """Adapter: turns FMI's WFS XML into a list of hourly ForecastPoints."""

    def __init__(self, http: httpx.AsyncClient, url: str = config.FMI_WFS_URL) -> None:
        self._http = http
        self._url = url

    async def fetch_point_forecast(
        self, latitude: float, longitude: float, start: datetime, end: datetime
    ) -> list[ForecastPoint]:
        # Without explicit start/end FMI returns only ~3 days; with them ~10 days.
        params = {
            "service": "WFS",
            "version": "2.0.0",
            "request": "getFeature",
            "storedquery_id": config.FMI_STORED_QUERY,
            "latlon": f"{latitude},{longitude}",
            "parameters": ",".join(_PARAMETERS),
            "timestep": "60",
            "starttime": _fmi_time(start),
            "endtime": _fmi_time(end),
        }
        response = await self._http.get(self._url, params=params)
        response.raise_for_status()
        return parse_forecast_xml(response.content)


def parse_forecast_xml(xml: bytes | str) -> list[ForecastPoint]:
    """Group FMI's flat (time, parameter, value) elements into one ForecastPoint per time step."""
    root = ET.fromstring(xml)
    values_by_time: dict[datetime, dict[str, float | None]] = {}
    for element in root.iterfind(".//BsWfs:BsWfsElement", _NS):
        time_text = element.findtext("BsWfs:Time", namespaces=_NS)
        field = _PARAMETERS.get(element.findtext("BsWfs:ParameterName", namespaces=_NS) or "")
        if time_text is None or field is None:
            continue
        value = _to_float(element.findtext("BsWfs:ParameterValue", namespaces=_NS))
        values_by_time.setdefault(datetime.fromisoformat(time_text), {})[field] = value
    return [ForecastPoint(time=time, **values) for time, values in sorted(values_by_time.items())]


def _to_float(text: str | None) -> float | None:
    """FMI uses the literal "NaN" for hours it has no forecast for yet."""
    try:
        value = float(text)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
    return None if math.isnan(value) else value


def _fmi_time(moment: datetime) -> str:
    return moment.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
