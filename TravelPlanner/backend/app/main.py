from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.settings import settings
from app.api.routers import chat, trip, auth, hotel, pay
from app.services.database import create_db_and_tables
from app.services.oauth_service import oauth_service

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
    configure_oauth(app)
    configure_router(app)
    configure_logging()
    
<<<<<<< Updated upstream
    # Create database tables on startup
    create_db_and_tables()
=======
    return app
>>>>>>> Stashed changes

def configure_cors(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 👈 replace with frontend origin(s) in prod
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

def configure_oauth(app: FastAPI):
    """Configure OAuth middleware"""
    app.add_middleware(oauth_service.oauth)

def configure_router(app: FastAPI):
<<<<<<< Updated upstream
    app.include_router(auth.router, prefix="/api", tags=["auth"])
    app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
=======
    app.include_router(chat.router, tags=["chat"])
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
app = create_app
=======
app = create_app()
>>>>>>> Stashed changes


