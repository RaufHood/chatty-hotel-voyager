from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from app.models.trip_leg import TripLeg

class Hotel(SQLModel, table=True):
    __tablename__ = "HOTELS"
    
    hotel_id: Optional[int] = Field(default=None, primary_key=True, alias="HOTEL_ID")
    hotel_name: str = Field(max_length=255, alias="HOTEL_NAME")
    stars: Optional[int] = Field(default=None, alias="STARS")
    rating: Optional[float] = Field(default=None, alias="RATING")
    latitude: Optional[float] = Field(default=None, alias="LATITUDE")
    longitude: Optional[float] = Field(default=None, alias="LONGITUDE")
    country_code: Optional[str] = Field(default=None, max_length=5, alias="COUNTRY_CODE")
    city_code: Optional[str] = Field(default=None, max_length=5, alias="CITY_CODE")
    hotel_type: Optional[str] = Field(default=None, max_length=50, alias="HOTEL_TYPE")
    
    # Relationships
    trip_legs: List["TripLeg"] = Relationship(back_populates="hotel")
    
    class Config:
        populate_by_name = True 