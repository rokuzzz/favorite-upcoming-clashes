from datetime import UTC, datetime

import httpx
import respx

from app import config
from app.clients.fmi_client import FmiClient, parse_forecast_xml


def fmi_xml(rows: list[tuple[str, str, str]]) -> str:
    """A minimal FMI 'simple' WFS response: one element per (time, parameter, value)."""
    members = "".join(
        f"""<wfs:member><BsWfs:BsWfsElement>
              <BsWfs:Time>{time}</BsWfs:Time>
              <BsWfs:ParameterName>{name}</BsWfs:ParameterName>
              <BsWfs:ParameterValue>{value}</BsWfs:ParameterValue>
            </BsWfs:BsWfsElement></wfs:member>"""
        for time, name, value in rows
    )
    return (
        '<wfs:FeatureCollection xmlns:wfs="http://www.opengis.net/wfs/2.0" '
        f'xmlns:BsWfs="http://xml.fmi.fi/schema/wfs/2.0">{members}</wfs:FeatureCollection>'
    )


def at(hour: int, minute: int = 0) -> datetime:
    return datetime(2026, 11, 11, hour, minute, tzinfo=UTC)


def test_parse_groups_values_by_hour_and_turns_nan_into_none():
    xml = fmi_xml(
        [
            ("2026-11-11T16:00:00Z", "Temperature", "2.98"),
            ("2026-11-11T16:00:00Z", "WindSpeedMS", "4.1"),
            ("2026-11-11T16:00:00Z", "WeatherSymbol3", "3.0"),
            ("2026-11-11T17:00:00Z", "Temperature", "NaN"),  # beyond FMI's ~10-day range
        ]
    )

    points = parse_forecast_xml(xml)

    assert [(p.time, p.temperature_c, p.wind_speed_ms, p.weather_symbol) for p in points] == [
        (at(16), 2.98, 4.1, 3.0),
        (at(17), None, None, None),
    ]


def test_parse_ignores_unknown_parameters_and_empty_responses():
    assert parse_forecast_xml(fmi_xml([("2026-11-11T16:00:00Z", "Humidity", "80")])) == []
    assert parse_forecast_xml(fmi_xml([])) == []


@respx.mock
async def test_fetch_sends_point_parameters_and_explicit_time_range():
    route = respx.get(config.FMI_WFS_URL).mock(
        return_value=httpx.Response(200, text=fmi_xml([("2026-11-11T16:00:00Z", "Temperature", "-1.5")]))
    )

    async with httpx.AsyncClient() as http:
        points = await FmiClient(http).fetch_point_forecast(61.12, 21.50, at(16), at(17))

    assert points[0].temperature_c == -1.5
    params = route.calls.last.request.url.params
    assert params["storedquery_id"] == config.FMI_STORED_QUERY
    assert params["latlon"] == "61.12,21.5"
    # Without starttime/endtime FMI only answers for about 3 days ahead
    assert (params["starttime"], params["endtime"]) == ("2026-11-11T16:00:00Z", "2026-11-11T17:00:00Z")
    assert params["parameters"] == "Temperature,Precipitation1h,WindSpeedMS,WindDirection,WeatherSymbol3"
