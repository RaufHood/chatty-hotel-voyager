from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum

class OAuthProvider(str, Enum):
    GOOGLE = "google"
    FACEBOOK = "facebook"
    GITHUB = "github"
    MICROSOFT = "microsoft"

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None

class UserCreate(UserBase):
    oauth_provider: OAuthProvider
    oauth_id: str

class User(UserBase):
    id: int
    oauth_provider: OAuthProvider
    oauth_id: str
    is_active: bool = True

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: Optional[str] = None
    user: User

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class OAuthLoginRequest(BaseModel):
    provider: OAuthProvider
    code: str
    state: Optional[str] = None

class OAuthURLResponse(BaseModel):
    auth_url: str
    state: str

class LoginResponse(BaseModel):
    message: str
    auth_url: Optional[str] = None
    state: Optional[str] = None 