import pytest
from httpx import ASGITransport, AsyncClient


@pytest.mark.asyncio
async def test_decode_vin_validation_error():
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/decode-vin", json={"vin": "INVALID"})
        assert response.status_code == 422

@pytest.mark.asyncio
async def test_decode_vin_success_shape(monkeypatch: pytest.MonkeyPatch):
    from app.main import app
    from app.services import nhtsa as nhtsa_mod

    async def fake_decode(vin: str):
        return {
            "Results": [
                {"Variable": "Make", "Value": "Honda"},
                {"Variable": "Model", "Value": "Civic"},
                {"Variable": "Model Year", "Value": "2018"},
                {"Variable": "Trim", "Value": "EX"},
                {"Variable": "Transmission Style", "Value": "CVT"},
                {"Variable": "Plant Country", "Value": "United States"},
                {"Variable": "ABS", "Value": "Standard"},
                {"Variable": "ESC", "Value": "Standard"},
            ]
        }

    monkeypatch.setattr(nhtsa_mod.nhtsa_client, "decode_vin", fake_decode)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/decode-vin", json={"vin": "1HGCM82633A004352"})
        assert response.status_code == 200
        data = response.json()
        assert "make" in data
        assert "model" in data
        assert data["make"] == "Honda"
        assert data["model"] == "Civic"
