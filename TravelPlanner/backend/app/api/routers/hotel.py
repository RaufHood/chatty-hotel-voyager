from fastapi import APIRouter, Path, Query
from app.services.hotel_ops import get_hotel_details, get_hotel_price
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/hotel/{hotel_id}")
async def get_hotel(
    hotel_id: str = Path(..., description="Hotel identifier"),
    check_in: str = Query(None, description="Check-in date (YYYY-MM-DD)"),
    check_out: str = Query(None, description="Check-out date (YYYY-MM-DD)")
):
    """Get detailed hotel information by ID using real Hotelbeds API"""
    hotel_details = await get_hotel_details(hotel_id)
    
    # If dates are provided, get real prices
    if check_in and check_out:
        try:
            price_info = await get_hotel_price(hotel_id, check_in, check_out)
            hotel_details["price"] = price_info["price"]
            hotel_details["originalPrice"] = price_info["originalPrice"]
            hotel_details["currency"] = price_info["currency"]
        except Exception as e:
            # If price lookup fails, keep the default values
            pass
    
    return hotel_details
