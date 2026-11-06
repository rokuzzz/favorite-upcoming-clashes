import json

from app.openapi import export_schema


def test_exported_schema_contains_routes_and_camel_case_models(tmp_path):
    path = tmp_path / "openapi.json"

    export_schema(path)

    schema = json.loads(path.read_text(encoding="utf-8"))
    assert {"/api/teams", "/api/matches"} <= schema["paths"].keys()
    assert "isHome" in schema["components"]["schemas"]["UpcomingMatch"]["properties"]
