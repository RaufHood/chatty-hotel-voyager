from fastapi import APIRouter, Path

router = APIRouter()

@router.get("/hotel/{hotel_id}")
async def get_hotel(hotel_id: str = Path(..., description="Hotel identifier")):
    # TODO: pull from DB / HotelOperations
    return {"hotel_id": hotel_id, "details": {}}
