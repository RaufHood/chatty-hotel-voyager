from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.settings import settings
from app.api.routers import chat, trip, auth, hotel, pay
from app.services.database import create_db_and_tables
from app.services.oauth_service import oauth_service

def create_app() -> FastAPI:
    app = FastAPI(title="TravelPlanner")

    configure_cors(app)
    configure_oauth(app)
    configure_router(app)
    configure_logging()
    
    # Create database tables on startup
    create_db_and_tables()

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
    app.include_router(auth.router, prefix="/api", tags=["auth"])
    app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
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
app = create_app


