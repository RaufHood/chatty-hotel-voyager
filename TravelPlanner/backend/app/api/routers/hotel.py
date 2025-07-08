from fastapi import APIRouter, Path, HTTPException
from app.services.snowflake_db import snowflake_db
from app.services import hotel_ops
import asyncio

router = APIRouter()

@router.get("/hotel/{hotel_id}")
async def get_hotel(hotel_id: int = Path(..., description="Hotel identifier")):
    # Fetch basic hotel details from DB
    hotel = snowflake_db.get_hotel_by_id(hotel_id)
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")

    # Fetch Hotelbeds static content and rates (async)
    hotel_code = str(hotel.get("HOTEL_CODE") or hotel.get("HOTEL_ID"))
    try:
        # Fetch static content (e.g., name, category, images, etc.)
        static_content_task = hotel_ops.hotel_static(hotel_code)
        # Fetch rates (dummy params for now, should be replaced with real search params)
        today = asyncio.to_thread(lambda: __import__('datetime').datetime.today().strftime('%Y-%m-%d'))
        rates_task = hotel_ops.availability(dest=hotel.get("CITY_CODE", ""), cin=await today, cout=await today)
        static_content, rates = await asyncio.gather(static_content_task, rates_task)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Hotelbeds API error: {e}")

    # Merge DB, static, and rates
    return {
        "hotel_id": hotel_id,
        "db_details": hotel,
        "static_content": static_content.get(hotel_code, {}),
        "rates": rates.get("hotels", [])
    }
