from pydantic_settings import BaseSettings
from typing import Optional
<<<<<<< Updated upstream
=======
import os

>>>>>>> Stashed changes

class Settings(BaseSettings):
    app_name: str = None
    enable_celery: bool = "y" == "y"
<<<<<<< Updated upstream
    database_url: str = "postgresql+psycopg://postgres:postgres@db:5432/TravelPlanner"
    redis_url: str = "redis://redis:6379/0"
=======
    database_url: str = None
>>>>>>> Stashed changes
    
    # Snowflake Database Settings
    snowflake_account: Optional[str] = None
    snowflake_user: Optional[str] = None
    snowflake_password: Optional[str] = None
    snowflake_warehouse: Optional[str] = None
<<<<<<< Updated upstream
    snowflake_database: Optional[str] = "CHATTY_HOTEL_VOYAGER"
    snowflake_schema: Optional[str] = "DBO"
=======
    snowflake_database: Optional[str] = None
    snowflake_schema: Optional[str] = None
>>>>>>> Stashed changes
    snowflake_role: Optional[str] = None
    
    # Snowflake Table Names
    snowflake_users_table: str = "USERS"
    snowflake_hotels_table: str = "HOTELS"
    snowflake_trips_table: str = "TRIPS"
    snowflake_trip_legs_table: str = "TRIP_LEGS"
    
    # OAuth2 Settings
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    facebook_client_id: Optional[str] = None
    facebook_client_secret: Optional[str] = None
    github_client_id: Optional[str] = None
    github_client_secret: Optional[str] = None
    microsoft_client_id: Optional[str] = None
    microsoft_client_secret: Optional[str] = None
    
<<<<<<< Updated upstream
    # Frontend URL for OAuth redirects
    frontend_url: str = "http://localhost:3000"
    
    # JWT Settings
    jwt_secret_key: str = "CHANGE_ME_JWT_SECRET"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30
    
    # API Keys
    groq_api_key: Optional[str] = None
    hotel_booking_key: Optional[str] = None

    class Config:
        env_file = ".env"
=======
    # AI/LLM Settings
    groq_api_key: Optional[str] = None
    
    # HotelBeds API Settings
    hotelbeds_api_key: Optional[str] = None
    hotelbeds_api_secret: Optional[str] = None

    class Config:
        env_file = "../.env"
>>>>>>> Stashed changes

settings = Settings()
