import pytest
import respx
import httpx

from app.services.open_meteo import fetch_open_meteo, OPEN_METEO_URL


@pytest.mark.asyncio
@respx.mock
async def test_fetch_open_meteo_time_matching_precip():
    respx.get(OPEN_METEO_URL).mock(
        return_value=httpx.Response(
            200,
            json={
                "current_weather": {
                    "temperature": 24.3,
                    "time": "2025-05-01T10:00",
                    "weathercode": 0,
                },
                "hourly": {
                    "time": ["2025-05-01T09:00", "2025-05-01T10:00", "2025-05-01T11:00"],
                    "precipitation_probability": [10, 35, 5],
                },
            },
        )
    )

    data = await fetch_open_meteo(12.97, 77.59)
    assert data["temperature"] == pytest.approx(24.3)
    assert data["precipitation_probability"] == 35
    assert data["summary"] == "Clear"
