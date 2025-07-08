<<<<<<< Updated upstream
from sqlmodel import Session, create_engine, SQLModel
=======
import logging
from contextlib import contextmanager
from typing import Generator, Optional
>>>>>>> Stashed changes
from app.core.settings import settings

<<<<<<< Updated upstream
# Create database engine
engine = create_engine(settings.database_url, echo=True)
=======
logger = logging.getLogger(__name__)

# Global Snowflake database instance
snowflake_db: Optional[SnowflakeDB] = None

def init_database() -> SnowflakeDB:
    """Initialize and return Snowflake database connection"""
    global snowflake_db
    
    try:
        logger.info("Initializing Snowflake database connection...")
        
        # Check if required settings are available
        required_settings = [
            'snowflake_account', 'snowflake_user', 'snowflake_password',
            'snowflake_warehouse', 'snowflake_database', 'snowflake_schema'
        ]
        
        missing_settings = []
        for setting in required_settings:
            if not getattr(settings, setting, None):
                missing_settings.append(setting)
        
        if missing_settings:
            logger.warning(f"Missing Snowflake settings: {missing_settings}")
            logger.warning("Database operations will be limited")
        
        # Initialize Snowflake connection
        snowflake_db = SnowflakeDB()
        
        # Test the connection
        test_connection()
        
        logger.info("✅ Snowflake database connection established successfully")
        return snowflake_db
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize Snowflake database: {e}")
        raise

def test_connection():
    """Test the database connection"""
    try:
        # Simple test query
        test_query = "SELECT CURRENT_VERSION()"
        result = snowflake_db.execute_query(test_query)
        logger.info(f"Database connection test successful. Snowflake version: {result[0]['CURRENT_VERSION()']}")
        return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        raise

def get_database() -> SnowflakeDB:
    """Get the global database instance"""
    global snowflake_db
    if snowflake_db is None:
        snowflake_db = init_database()
    return snowflake_db

@contextmanager
def get_db_session() -> Generator[SnowflakeDB, None, None]:
    """Get database session context manager"""
    db = get_database()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        raise
    finally:
        # Note: Snowflake connection is kept alive for the session
        # Connection will be closed when the application shuts down
        pass
>>>>>>> Stashed changes

def create_db_and_tables():
    """Create database tables"""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Get database session"""
    with Session(engine) as session:
        yield session 