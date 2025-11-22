import pytest
import respx
import httpx

from app.services.geocode import geocode_place, GeocodeResult, NOMINATIM_URL


@pytest.mark.asyncio
@respx.mock
async def test_geocode_place_parses_top_three_unique():
    query = "Bangalore"
    # Mock response with duplicates & missing name entry
    respx.get(NOMINATIM_URL).mock(
        return_value=httpx.Response(
            200,
            json=[
                {"display_name": "Bangalore, India", "lat": "12.97", "lon": "77.59"},
                {"display_name": "Bengaluru, Karnataka, India", "lat": "12.96", "lon": "77.60"},
                {"display_name": "Bangalore Urban", "lat": "12.95", "lon": "77.58"},
                {"display_name": "Bangalore, India", "lat": "12.97", "lon": "77.59"},  # duplicate
                {"display_name": None, "lat": "0", "lon": "0"},  # unnamed filtered
            ],
        )
    )

    results = await geocode_place(query)
    assert len(results) == 3
    assert isinstance(results[0], GeocodeResult)
    names = [r.display_name for r in results]
    assert len(set(names)) == 3
    assert names[0].startswith("Bangalore")
