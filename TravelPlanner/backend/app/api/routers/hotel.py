from fastapi import APIRouter, Path
from app.services.hotel_ops import get_hotel_details

router = APIRouter()

@router.get("/hotel/{hotel_id}")
async def get_hotel(hotel_id: str = Path(..., description="Hotel identifier")):
    """Get detailed hotel information by ID using real Hotelbeds API"""
    hotel_details = await get_hotel_details(hotel_id)
    return hotel_details
