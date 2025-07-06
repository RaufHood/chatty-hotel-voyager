from .auth import *
from .user import *
from .hotel import *
from .trip import *
from .trip_leg import *
from .chat import *

__all__ = [
    # Auth schemas
    "OAuthProvider", "UserBase", "UserCreate", "User", "Token", 
    "RefreshTokenRequest", "OAuthLoginRequest", "OAuthURLResponse", "LoginResponse",
    # User schemas
    "UserUpdate", "UserResponse",
    # Hotel schemas
    "HotelBase", "HotelCreate", "HotelUpdate", "HotelResponse",
    # Trip schemas
    "TripBase", "TripCreate", "TripUpdate", "TripResponse",
    # Trip Leg schemas
    "TripLegBase", "TripLegCreate", "TripLegUpdate", "TripLegResponse",
    # Chat schemas
    "ChatMessage", "ChatRequest", "ChatResponse", "ChatHistoryRequest", 
    "ChatHistoryResponse", "ClearChatRequest"
]
