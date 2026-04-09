from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_decode_vin_validation_error():
    from app.main import app

    async with AsyncClient(app=app, base_url="http://test") as client:
        r = await client.post("/decode-vin", json={"vin": "SHORT"})
        assert r.status_code == 422


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

    async with AsyncClient(app=app, base_url="http://test") as client:
        vin = "1HGCM82633A004352"
        r = await client.post("/decode-vin", json={"vin": vin})
        assert r.status_code == 200
        data = r.json()
        assert "specs" in data
        assert data["specs"]["vin"] == vin
        assert data["specs"]["make"] == "Honda"
        assert data["specs"]["model"] == "Civic"
        assert data["specs"]["year"] == 2018
        assert data["specs"]["source"] in {"nhtsa", "vindecoder", "ai", "local"}
        assert isinstance(data["specs"]["safety_features"], list)

