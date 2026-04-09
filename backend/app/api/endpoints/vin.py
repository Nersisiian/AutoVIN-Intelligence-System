from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.services import vin_decoder, auction, ocr, ml_service
from app.core.redis_client import redis_client
import json

router = APIRouter()

@router.post("/decode-vin")
async def decode_vin(vin: str):
    # existing implementation – keep as is
    pass

@router.post("/predict-specs")
async def predict_specs(vin: str):
    if len(vin) != 17:
        raise HTTPException(status_code=400, detail="Invalid VIN length")
    # Check cache
    cache_key = f"ml:{vin}"
    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    result = ml_service.predict_vin_specs(vin)
    await redis_client.setex(cache_key, 3600, json.dumps(result))
    return result

@router.post("/scan-vin-image")
async def scan_vin_image(file: UploadFile = File(...)):
    contents = await file.read()
    vin = ocr.extract_vin_from_image(contents)
    if not vin:
        raise HTTPException(status_code=400, detail="No VIN found in image")
    # Optionally decode
    return {"vin": vin}

@router.get("/auction-data")
async def auction_data(vin: str):
    cache_key = f"auction:{vin}"
    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    data = auction.get_auction_info(vin)
    await redis_client.setex(cache_key, 3600, json.dumps(data))
    return data