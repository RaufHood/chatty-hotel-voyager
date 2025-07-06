from pydantic import BaseModel
from typing import Optional

class HotelBase(BaseModel):
    hotel_name: str
    stars: Optional[int] = None
    rating: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    country_code: Optional[str] = None
    city_code: Optional[str] = None
    hotel_type: Optional[str] = None

class HotelCreate(HotelBase):
    pass

class HotelUpdate(BaseModel):
    hotel_name: Optional[str] = None
    stars: Optional[int] = None
    rating: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    country_code: Optional[str] = None
    city_code: Optional[str] = None
    hotel_type: Optional[str] = None

class HotelResponse(HotelBase):
    hotel_id: int

    class Config:
        from_attributes = True 