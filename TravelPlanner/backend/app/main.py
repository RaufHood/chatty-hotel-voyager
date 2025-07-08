from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.settings import settings
from app.api.routers import chat, trip, hotel, pay
from app.services.database import create_db_and_tables, close_database

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for database initialization and cleanup"""
    # Startup
    try:
        create_db_and_tables()
    except Exception as e:
        logging.error(f"Failed to initialize database: {e}")
    
    yield
    
    # Shutdown
    try:
        close_database()
    except Exception as e:
        logging.error(f"Failed to close database: {e}")

def create_app() -> FastAPI:
    app = FastAPI(title="TravelPlanner", lifespan=lifespan)

    configure_cors(app)
    configure_router(app)
    configure_logging()
    
    return app

def configure_cors(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 👈 replace with frontend origin(s) in prod
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

def configure_router(app: FastAPI):
    app.include_router(chat.router, tags=["chat"])
    app.include_router(trip.router, prefix="/api/trips", tags=["trips"])
    app.include_router(hotel.router, prefix="/api", tags=["hotels"])
    app.include_router(pay.router, prefix="/api", tags=["payments"])

    @app.get("/", tags=["root"])
    async def landing():
        return {"message": "Welcome to the Smart Travel Assistant API"}

def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
app = create_app()


