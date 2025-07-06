from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.schemas.auth import OAuthProvider

class UserBase(BaseModel):
    email: EmailStr
    name: str
    surname: str

class UserCreate(UserBase):
    oauth_provider: OAuthProvider
    oauth_id: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    surname: Optional[str] = None
    auto_token: Optional[str] = None

class UserResponse(UserBase):
    user_id: int
    auto_token: Optional[str] = None
    oauth_provider: Optional[OAuthProvider] = None
    oauth_id: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 