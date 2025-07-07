from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.schemas.auth import OAuthProvider

class UserBase(BaseModel):
    email: EmailStr
    name: str
    surname: str
    phone_number: Optional[str] = None     # ✅ Add phone number

class UserCreate(UserBase):
    oauth_provider: OAuthProvider
    oauth_id: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    surname: Optional[str] = None
    auto_token: Optional[str] = None
    phone_number: Optional[str] = None      # ✅ Add phone number
    is_verified: Optional[bool] = None      # ✅ verify user's phone number

class UserResponse(UserBase):
    user_id: int
    auto_token: Optional[str] = None
    oauth_provider: Optional[OAuthProvider] = None
    oauth_id: Optional[str] = None
    is_active: bool
    is_verified: bool                       # ✅ verify user's phone number
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 