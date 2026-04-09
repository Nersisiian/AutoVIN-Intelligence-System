from __future__ import annotations

from typing import Any, Optional

import httpx

from app.core.config import settings


class NhtsaClient:
    def __init__(self) -> None:
        self._base = str(settings.nhtsa_base_url).rstrip("/")

    async def decode_vin(self, vin: str) -> dict[str, Any]:
        # NHTSA VPIC: /DecodeVin/{vin}?format=json
        url = f"{self._base}/DecodeVin/{vin}"
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.get(url, params={"format": "json"})
            resp.raise_for_status()
            return resp.json()

    @staticmethod
    def extract_best_effort(payload: dict[str, Any]) -> dict[str, Optional[str]]:
        # Payload format: { Results: [ { Variable, Value }, ... ] }
        results = payload.get("Results") or []
        kv: dict[str, Optional[str]] = {}
        for item in results:
            var = item.get("Variable")
            val = item.get("Value")
            if isinstance(var, str):
                kv[var] = val if isinstance(val, str) else None

        return {
            "make": kv.get("Make"),
            "model": kv.get("Model"),
            "year": kv.get("Model Year"),
            "trim": kv.get("Trim") or kv.get("Trim2"),
            "engine": kv.get("Engine Model") or kv.get("Engine Configuration") or kv.get("Displacement (L)"),
            "transmission": kv.get("Transmission Style") or kv.get("Transmission Type"),
            "country_of_origin": kv.get("Plant Country"),
            "abs": kv.get("ABS"),
            "esc": kv.get("ESC"),
            "tpms": kv.get("TPMS"),
            "airbags": kv.get("Air Bag Loc Front"),
        }


nhtsa_client = NhtsaClient()
