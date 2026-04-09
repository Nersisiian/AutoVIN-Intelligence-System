from __future__ import annotations

import hashlib
import hmac
import time
from typing import Any

import httpx

from app.core.config import settings


class VinDecoderExternalClient:
    """
    Supports VINDecoder.eu style API (paid) when key exists.
    When no key is present, returns a deterministic mock based on VIN.
    """

    async def decode(self, vin: str) -> dict[str, Any]:
        if settings.vindecoder_api_key.strip():
            return await self._decode_paid(vin)
        return self._mock_decode(vin)

    async def _decode_paid(self, vin: str) -> dict[str, Any]:
        base = str(settings.vindecoder_api_base).rstrip("/")
        # VINDecoder.eu: /{api_version}/{apikey}/{secret}/decode/{vin}.json
        # They also use HMAC for signature in some plans. We'll implement a simple timestamped signature:
        # signature = HMAC-SHA1(apikey, f"{vin}|{timestamp}") -> hex
        # This keeps the client functional for typical "apikey only" gateways too (servers may ignore signature).
        ts = str(int(time.time()))
        msg = f"{vin}|{ts}".encode("utf-8")
        sig = hmac.new(settings.vindecoder_api_key.encode("utf-8"), msg, hashlib.sha1).hexdigest()

        url = f"{base}/decode/{vin}.json"
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.get(url, params={"key": settings.vindecoder_api_key, "ts": ts, "sig": sig})
            resp.raise_for_status()
            return resp.json()

    def _mock_decode(self, vin: str) -> dict[str, Any]:
        seed = int(hashlib.sha256(vin.encode("utf-8")).hexdigest()[:8], 16)
        makes = ["Toyota", "Honda", "Ford", "BMW", "Mercedes-Benz", "Nissan", "Hyundai", "Kia"]
        models = ["Corolla", "Civic", "F-150", "3 Series", "C-Class", "Altima", "Elantra", "Sportage"]
        trims = ["Base", "SE", "Sport", "Limited", "Premium"]
        engines = ["2.0L I4", "2.5L I4", "3.5L V6", "1.6L Turbo I4"]
        transmissions = ["Automatic", "Manual", "CVT", "Dual-clutch"]
        safety = ["ABS", "ESC", "Lane Keep Assist", "Adaptive Cruise Control", "Blind Spot Monitor"]

        make = makes[seed % len(makes)]
        model = models[(seed // 7) % len(models)]
        trim = trims[(seed // 13) % len(trims)]
        engine = engines[(seed // 17) % len(engines)]
        transmission = transmissions[(seed // 19) % len(transmissions)]
        safety_features = [safety[(seed + i) % len(safety)] for i in range(3)]

        return {
            "mock": True,
            "vin": vin,
            "make": make,
            "model": model,
            "trim": trim,
            "engine": engine,
            "transmission": transmission,
            "safety_features": safety_features,
        }


vindecoder_client = VinDecoderExternalClient()
