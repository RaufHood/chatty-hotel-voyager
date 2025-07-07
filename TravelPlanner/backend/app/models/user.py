from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from app.schemas.auth import OAuthProvider

if TYPE_CHECKING:
    from app.models.trip import Trip
    from app.models.trip_leg import TripLeg

class User(SQLModel, table=True):
    __tablename__ = "USERS"
    
    user_id: Optional[int] = Field(default=None, primary_key=True, alias="USER_ID")
    email: str = Field(max_length=30, alias="EMAIL")
    name: str = Field(max_length=30, alias="NAME")
    surname: str = Field(max_length=30, alias="SURNAME")
    auto_token: Optional[str] = Field(default=None, max_length=255, alias="AUTO_TOKEN")
    phone_number: Optional[str] = Field(default=None, max_length=20, alias="PHONE_NUMBER") # ✅ New fields
    is_verified: bool = Field(default=False, alias="IS_VERIFIED")
    test_column: Optional[str] = Field(default=None, alias="TEST_COLUMN") # temporary test field

    
    # Additional fields for OAuth integration (not in Snowflake schema but needed for app)
    oauth_provider: Optional[OAuthProvider] = None
    oauth_id: Optional[str] = None
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    trips: List["Trip"] = Relationship(back_populates="user")
    trip_legs: List["TripLeg"] = Relationship(back_populates="user")
    
    class Config:
        populate_by_name = True 