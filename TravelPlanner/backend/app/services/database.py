import logging
from contextlib import contextmanager
from typing import Generator, Optional
from sqlmodel import Session, create_engine
from sqlalchemy import URL
from app.core.settings import settings
from app.services.snowflake_db import SnowflakeDB

logger = logging.getLogger(__name__)

# Global Snowflake database instance
snowflake_db: Optional[SnowflakeDB] = None

# SQLAlchemy engine for SQLModel operations
engine = None

def get_engine():
    """Get or create SQLAlchemy engine for Snowflake"""
    global engine
    if engine is None:
        # Build Snowflake connection URL
        snowflake_url = URL.create(
            "snowflake",
            username=settings.snowflake_user,
            password=settings.snowflake_password,
            host=settings.snowflake_account,
            database=settings.snowflake_database,
            query={
                "warehouse": settings.snowflake_warehouse,
                "schema": settings.snowflake_schema,
                "role": settings.snowflake_role
            }
        )
        
        engine = create_engine(snowflake_url, echo=False)
        logger.info("✅ SQLAlchemy engine created for Snowflake")
    
    return engine

def get_session() -> Generator[Session, None, None]:
    """Get SQLModel session for database operations"""
    engine = get_engine()
    with Session(engine) as session:
        yield session

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

def create_db_and_tables():
    """Initialize database and create tables if needed"""
    try:
        logger.info("Setting up database...")
        
        # Initialize database connection
        db = init_database()
        
        # Check if tables exist and create them if needed
        create_tables_if_not_exist(db)
        
        logger.info("✅ Database setup completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Database setup failed: {e}")
        raise

def create_tables_if_not_exist(db: SnowflakeDB):
    """Create database tables if they don't exist"""
    try:
        # Check if users table exists
        check_users_table = f"""
        SELECT COUNT(*) as table_count 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_SCHEMA = '{settings.snowflake_schema}' 
        AND TABLE_NAME = '{settings.snowflake_users_table}'
        """
        
        result = db.execute_query(check_users_table)
        table_exists = result[0]['TABLE_COUNT'] > 0
        
        if not table_exists:
            logger.info(f"Creating {settings.snowflake_users_table} table...")
            create_users_table = f"""
            CREATE TABLE {settings.snowflake_users_table} (
                USER_ID NUMBER AUTOINCREMENT PRIMARY KEY,
                EMAIL VARCHAR(255) UNIQUE NOT NULL,
                NAME VARCHAR(255) NOT NULL,
                SURNAME VARCHAR(255) NOT NULL,
                CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
                UPDATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
            )
            """
            db.execute_query(create_users_table)
            logger.info(f"✅ {settings.snowflake_users_table} table created successfully")
        else:
            logger.info(f"✅ {settings.snowflake_users_table} table already exists")
        
        # Add more table creation logic here as needed
        # create_hotels_table(db)
        # create_trips_table(db)
        # create_trip_legs_table(db)
        
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        raise

def close_database():
    """Close database connection"""
    global snowflake_db
    if snowflake_db:
        try:
            snowflake_db.close()
            logger.info("✅ Database connection closed successfully")
        except Exception as e:
            logger.error(f"Error closing database connection: {e}")
        finally:
            snowflake_db = None 