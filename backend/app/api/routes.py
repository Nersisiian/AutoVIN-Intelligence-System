from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import DecodeVinRequest, DecodeVinResponse
from app.core.db import get_db
from app.services.decode_service import decode_vin

router = APIRouter()


@router.post("/decode-vin", response_model=DecodeVinResponse)
async def decode_vin_endpoint(payload: DecodeVinRequest, db: AsyncSession = Depends(get_db)) -> DecodeVinResponse:  # noqa: B008
    result = await decode_vin(payload.vin, db=db)
    return DecodeVinResponse(**result)

