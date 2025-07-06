from pydantic_settings import BaseSettings
from typing import Optional
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    app_name: str = "TravelPlanner"
    secret_key: str = "CHANGE_ME"
    enable_celery: bool = "y" == "y"
    database_url: str = "postgresql+psycopg://postgres:postgres@db:5432/TravelPlanner"
    
    # Snowflake Database Settings
    snowflake_account: Optional[str] = os.getenv("SNOWFLAKE_ACCOUNT")
    snowflake_user: Optional[str] = os.getenv("SNOWFLAKE_USER")
    snowflake_password: Optional[str] = os.getenv("SNOWFLAKE_PASSWORD")
    snowflake_warehouse: Optional[str] = os.getenv("SNOWFLAKE_WAREHOUSE")
    snowflake_database: Optional[str] = os.getenv("SNOWFLAKE_DATABASE")
    snowflake_schema: Optional[str] = os.getenv("SNOWFLAKE_SCHEMA")
    snowflake_role: Optional[str] = os.getenv("SNOWFLAKE_ROLE")
    
    # Snowflake Table Names
    snowflake_users_table: str = "USERS"
    snowflake_hotels_table: str = "HOTELS"
    snowflake_trips_table: str = "TRIPS"
    snowflake_trip_legs_table: str = "TRIP_LEGS"
    
    # Frontend URL
    frontend_url: str = "http://localhost:8000"
    
    # AI/LLM Settings
    groq_api_key: Optional[str] = os.getenv("GROQ_API_KEY")
    

    class Config:
        env_file = ".env"

settings = Settings()
