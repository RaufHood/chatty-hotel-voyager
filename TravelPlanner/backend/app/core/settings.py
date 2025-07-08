from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    app_name: str = "Chatty-hotel-voyager"
    enable_celery: bool = "y" == "y"
    
    # Snowflake Database Settings
    snowflake_account: Optional[str] = None
    snowflake_user: Optional[str] = None
    snowflake_password: Optional[str] = None
    snowflake_warehouse: Optional[str] = None
    snowflake_database: Optional[str] = None
    snowflake_schema: Optional[str] = None
    snowflake_role: Optional[str] = None
    
    # Snowflake Table Names
    snowflake_users_table: str = "USERS"
    snowflake_hotels_table: str = "HOTELS"
    snowflake_trips_table: str = "TRIPS"
    snowflake_trip_legs_table: str = "TRIP_LEGS"
    
    # Frontend URL
    frontend_url: str = "http://localhost:8000"
    
    # AI/LLM Settings
    groq_api_key: Optional[str] = None
    
    # HotelBeds API Settings
    hotelbeds_api_key: Optional[str] = None
    hotelbeds_api_secret: Optional[str] = None

    class Config:
        env_file = "../.env"

settings = Settings()
