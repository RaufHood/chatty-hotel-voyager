from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from .hotel import HotelResponse

class TripLegBase(BaseModel):
    trip_id: int
    user_id: int
    hotel_id: int
    arrival_date: Optional[datetime] = None
    departure_date: Optional[datetime] = None
    stay_price: Optional[float] = None

class TripLegCreate(TripLegBase):
    pass

class TripLegUpdate(BaseModel):
    arrival_date: Optional[datetime] = None
    departure_date: Optional[datetime] = None
    stay_price: Optional[float] = None

class TripLegResponse(TripLegBase):
    trip_leg_id: int
    hotel: Optional[HotelResponse] = None

    class Config:
        from_attributes = True 