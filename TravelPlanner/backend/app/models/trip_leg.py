from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.trip import Trip
    from app.models.hotel import Hotel

class TripLeg(SQLModel, table=True):
    __tablename__ = "TRIP_LEGS"
    
    trip_leg_id: Optional[int] = Field(default=None, primary_key=True, alias="TRIP_LEG_ID")
    trip_id: int = Field(foreign_key="TRIPS.TRIP_ID", alias="TRIP_ID")
    user_id: int = Field(foreign_key="USERS.USER_ID", alias="USER_ID")
    hotel_id: int = Field(foreign_key="HOTELS.HOTEL_ID", alias="HOTEL_ID")
    arrival_date: Optional[datetime] = Field(default=None, alias="ARRIVAL_DATE")
    departure_date: Optional[datetime] = Field(default=None, alias="DEPARTURE_DATE")
    stay_price: Optional[float] = Field(default=None, alias="STAY_PRICE")
    
    # Relationships
    trip: Optional["Trip"] = Relationship(back_populates="trip_legs")
    user: Optional["User"] = Relationship(back_populates="trip_legs")
    hotel: Optional["Hotel"] = Relationship(back_populates="trip_legs")
    
    class Config:
        populate_by_name = True 