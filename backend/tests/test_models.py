from app.models import Team


def test_json_uses_camel_case_and_accepts_both_spellings():
    team = Team.model_validate({"id": "624554857:lukko", "name": "Lukko", "logoUrl": "lukko.png"})

    assert team.logo_url == "lukko.png"
    assert team.model_dump() == {"id": "624554857:lukko", "name": "Lukko", "logoUrl": "lukko.png"}
    assert Team(id="x", name="X", logo_url="x.png").logo_url == "x.png"
