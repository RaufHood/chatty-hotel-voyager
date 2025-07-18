from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from app.core.settings import settings

if TYPE_CHECKING:
    from app.models.trip import Trip
    from app.models.trip_leg import TripLeg

class User(SQLModel, table=True):
    __tablename__ = settings.snowflake_users_table
    
    user_id: Optional[int] = Field(default=None, primary_key=True, alias="USER_ID")
    email: str = Field(max_length=30, alias="EMAIL")
    name: str = Field(max_length=30, alias="NAME")
    surname: str = Field(max_length=30, alias="SURNAME")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    trips: List["Trip"] = Relationship(back_populates="user")
    trip_legs: List["TripLeg"] = Relationship(back_populates="user")
    
    class Config:
        populate_by_name = True 