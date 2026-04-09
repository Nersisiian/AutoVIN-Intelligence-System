from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator


class DecodeVinRequest(BaseModel):
    vin: str = Field(..., min_length=17, max_length=17, description="17-character VIN")

    @field_validator("vin")
    @classmethod
    def validate_vin(cls, v: str) -> str:
        v = v.strip().upper()
        if len(v) != 17:
            raise ValueError("VIN must be exactly 17 characters")
        # VIN excludes I, O, Q to avoid confusion.
        forbidden = {"I", "O", "Q"}
        if any(ch in forbidden for ch in v):
            raise ValueError("VIN contains invalid characters (I, O, Q are not allowed)")
        if not v.isalnum():
            raise ValueError("VIN must be alphanumeric")
        return v


class VehicleSpecs(BaseModel):
    vin: str
    make: str | None = None
    model: str | None = None
    year: int | None = None
    trim: str | None = None
    engine: str | None = None
    transmission: str | None = None
    country_of_origin: str | None = None
    safety_features: list[str] = Field(default_factory=list)
    recalls: list[dict[str, Any]] | None = None
    accident_history: dict[str, Any] | None = None

    source: str = Field(..., description="local|nhtsa|vindecoder|ai")
    confidence: float = Field(..., ge=0.0, le=1.0)


class DecodeVinResponse(BaseModel):
    specs: VehicleSpecs
    raw: dict[str, Any] = Field(default_factory=dict)
