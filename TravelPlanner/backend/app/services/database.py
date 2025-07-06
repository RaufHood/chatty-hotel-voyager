from sqlmodel import Session, create_engine, SQLModel
from app.core.settings import settings

# Create database engine
engine = create_engine(settings.database_url, echo=True)

def create_db_and_tables():
    """Create database tables"""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Get database session"""
    with Session(engine) as session:
        yield session 