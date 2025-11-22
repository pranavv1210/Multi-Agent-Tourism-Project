import pytest

from app.agents.parent_agent import orchestrate
from app.services.geocode import GeocodeResult


class DummyGeo(GeocodeResult):
    pass


@pytest.mark.asyncio
async def test_orchestrate_happy_path(monkeypatch):
    async def fake_geocode_place(candidate):  # noqa: D401
        return [DummyGeo(display_name="Bangalore, Karnataka, India", lat=12.97, lon=77.59)]

    async def fake_weather(lat, lon):
        return {"temperature": 24.0, "precipitation_probability": 35, "summary": "Clear"}

    async def fake_places(lat, lon):
        return [
            {"name": "Lalbagh"},
            {"name": "Cubbon Park"},
        ]

    monkeypatch.setattr("app.agents.parent_agent.geocode_place", fake_geocode_place)
    monkeypatch.setattr("app.agents.parent_agent.fetch_weather", fake_weather)
    monkeypatch.setattr("app.agents.parent_agent.fetch_places", fake_places)

    result = await orchestrate("Bangalore", ["weather", "places"])
    assert result["place"].startswith("Bangalore")
    assert result["weather"]["temperature"] == 24.0
    assert "Lalbagh" in result["places"]
    assert "Cubbon Park" in result["places"]
    assert "24" in result["text"]


@pytest.mark.asyncio
async def test_orchestrate_partial_failure(monkeypatch):
    async def fake_geocode_place(candidate):  # noqa: D401
        return [DummyGeo(display_name="Bangalore, Karnataka, India", lat=12.97, lon=77.59)]

    async def failing_weather(lat, lon):
        raise RuntimeError("weather down")

    async def fake_places(lat, lon):
        return [
            {"name": "Lalbagh"},
        ]

    monkeypatch.setattr("app.agents.parent_agent.geocode_place", fake_geocode_place)
    monkeypatch.setattr("app.agents.parent_agent.fetch_weather", failing_weather)
    monkeypatch.setattr("app.agents.parent_agent.fetch_places", fake_places)

    result = await orchestrate("Bangalore", ["weather", "places"])
    # Weather error should yield either error entry or absence of weather data
    assert result["places"] == ["Lalbagh"]
    assert result["weather"] is None or result["weather"].get("error")
    assert result["errors"] is not None
