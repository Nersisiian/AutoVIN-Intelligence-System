from __future__ import annotations

from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import cache
from app.core.config import settings
from app.core.logging import get_logger
from app.models.vin_decode import VinDecodeRecord
from app.services.ai_estimator import ai_estimator
from app.services.nhtsa import nhtsa_client
from app.services.vin_local import decode_vin_locally
from app.services.vindecoder_external import vindecoder_client

log = get_logger(component="decode_service")


def _cache_key(vin: str) -> str:
    # Bump this when decode logic changes materially to avoid stale cached responses.
    return f"vin:decode:v2:{vin}"


def _merge_safety(nhtsa_extracted: dict[str, Optional[str]]) -> list[str]:
    feats: list[str] = []
    if nhtsa_extracted.get("abs") and nhtsa_extracted["abs"] != "Not Applicable":
        feats.append("ABS")
    if nhtsa_extracted.get("esc") and nhtsa_extracted["esc"] != "Not Applicable":
        feats.append("ESC")
    if nhtsa_extracted.get("tpms") and nhtsa_extracted["tpms"] != "Not Applicable":
        feats.append("TPMS")
    if nhtsa_extracted.get("airbags") and nhtsa_extracted["airbags"] != "Not Applicable":
        feats.append("Airbags (Front)")
    return sorted(set(feats))


async def decode_vin(vin: str, db: AsyncSession) -> dict[str, Any]:
    cached = await cache.get_json(_cache_key(vin))
    if cached:
        return cached

    local = decode_vin_locally(vin)
    raw: dict[str, Any] = {"local": local.__dict__}

    # Try NHTSA first (free and usually rich).
    source = "local"
    confidence = 0.35
    specs: dict[str, Any] = {
        "vin": vin,
        "make": local.make,
        "model": None,
        "year": local.year,
        "trim": None,
        "engine": None,
        "transmission": None,
        "country_of_origin": local.country_of_origin,
        "safety_features": [],
        "recalls": None,
        "accident_history": None,
    }

    try:
        nhtsa_payload = await nhtsa_client.decode_vin(vin)
        raw["nhtsa"] = nhtsa_payload
        extracted = nhtsa_client.extract_best_effort(nhtsa_payload)
        safety_features = _merge_safety(extracted)

        if extracted.get("make") or extracted.get("model"):
            source = "nhtsa"
            confidence = 0.9
            specs.update(
                {
                    "make": extracted.get("make") or specs["make"],
                    "model": extracted.get("model"),
                    "year": int(extracted["year"]) if extracted.get("year") and str(extracted["year"]).isdigit() else specs["year"],
                    "trim": extracted.get("trim"),
                    "engine": extracted.get("engine"),
                    "transmission": extracted.get("transmission"),
                    "country_of_origin": extracted.get("country_of_origin") or specs["country_of_origin"],
                    "safety_features": safety_features,
                }
            )
    except Exception as e:  # noqa: BLE001
        log.warning("nhtsa_decode_failed", vin=vin, err=str(e))

    # If NHTSA didn't help enough, try external paid/mocked VINDecoder.
    if not specs.get("model"):
        try:
            ext = await vindecoder_client.decode(vin)
            raw["vindecoder"] = ext
            if ext.get("make") or ext.get("model"):
                source = "vindecoder"
                confidence = 0.75 if ext.get("mock") else 0.92
                specs.update(
                    {
                        "make": ext.get("make") or specs["make"],
                        "model": ext.get("model") or specs["model"],
                        "trim": ext.get("trim") or specs["trim"],
                        "engine": ext.get("engine") or specs["engine"],
                        "transmission": ext.get("transmission") or specs["transmission"],
                        "safety_features": ext.get("safety_features") or specs["safety_features"],
                    }
                )
        except Exception as e:  # noqa: BLE001
            log.warning("vindecoder_failed", vin=vin, err=str(e))

    # AI fallback if still unknown / sparse.
    if not specs.get("model") or not specs.get("engine"):
        est = ai_estimator.estimate(local.wmi, local.year)
        raw["ai"] = {
            "estimated": True,
            "make": est.make,
            "model": est.model,
            "trim": est.trim,
            "engine": est.engine,
            "transmission": est.transmission,
            "safety_features": est.safety_features,
            "confidence": est.confidence,
        }
        if not specs.get("model"):
            source = "ai"
            confidence = est.confidence
        specs.update(
            {
                "make": specs.get("make") or est.make,
                "model": specs.get("model") or est.model,
                "trim": specs.get("trim") or est.trim,
                "engine": specs.get("engine") or est.engine,
                "transmission": specs.get("transmission") or est.transmission,
                "safety_features": specs.get("safety_features") or est.safety_features,
            }
        )

    # Persist
    rec = VinDecodeRecord(vin=vin, source=source, payload={"specs": specs, "raw": raw, "confidence": confidence})
    db.add(rec)
    await db.commit()

    out = {"specs": {**specs, "source": source, "confidence": confidence}, "raw": raw}
    await cache.set_json(_cache_key(vin), out, ttl_seconds=settings.cache_ttl_seconds)
    return out

