from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from app.core.settings import settings

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.trip_leg import TripLeg

class Trip(SQLModel, table=True):
    __tablename__ = settings.snowflake_trips_table
    
    trip_id: Optional[int] = Field(default=None, primary_key=True, alias="TRIP_ID")
    user_id: int = Field(foreign_key="USERS.USER_ID", alias="USER_ID")
    date_start: Optional[datetime] = Field(default=None, alias="DATE_START")
    date_end: Optional[datetime] = Field(default=None, alias="DATE_END")
    
    # Relationships
    user: Optional["User"] = Relationship(back_populates="trips")
    trip_legs: List["TripLeg"] = Relationship(back_populates="trip")
    
    class Config:
        populate_by_name = True 