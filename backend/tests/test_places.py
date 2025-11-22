import pytest
import respx
import httpx

from app.services.overpass import OVERPASS_URL, build_overpass_query, fetch_pois


@pytest.mark.asyncio
@respx.mock
async def test_fetch_pois_parses_and_limits():
    # Build a query to ensure endpoint called; content not validated here
    query = build_overpass_query(12.97, 77.59, 5000)
    respx.post(OVERPASS_URL).mock(
        return_value=httpx.Response(
            200,
            json={
                "elements": [
                    {"tags": {"name": "Lalbagh", "leisure": "park"}},
                    {"tags": {"name": "Cubbon Park", "leisure": "park"}},
                    {"tags": {"name": "Lalbagh", "tourism": "attraction"}},  # duplicate name
                    {"tags": {"name:en": "Bangalore Palace", "historic": "castle"}},
                    {"tags": {"name": "ISKCON Temple", "tourism": "attraction"}},
                    {"tags": {"name": "Extra Place", "tourism": "attraction"}},
                ]
            },
        )
    )

    pois = await fetch_pois(12.97, 77.59, 5000, limit=5)
    assert len(pois) == 5
    names = [p["name"] for p in pois]
    assert "Lalbagh" in names
    assert "Cubbon Park" in names
    assert "Bangalore Palace" in names
