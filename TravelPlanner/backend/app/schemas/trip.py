from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from .trip_leg import TripLegResponse

class TripBase(BaseModel):
    user_id: int
    date_start: Optional[datetime] = None
    date_end: Optional[datetime] = None

class TripCreate(TripBase):
    pass

class TripUpdate(BaseModel):
    date_start: Optional[datetime] = None
    date_end: Optional[datetime] = None

class TripResponse(TripBase):
    trip_id: int
    trip_legs: List[TripLegResponse] = []

    class Config:
        from_attributes = True 