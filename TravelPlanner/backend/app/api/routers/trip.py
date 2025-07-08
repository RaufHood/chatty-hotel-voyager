from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.services.snowflake_db import snowflake_db
from app.schemas.trip import TripCreate, TripResponse
from app.schemas.trip_leg import TripLegCreate, TripLegResponse
from datetime import datetime

router = APIRouter()

@router.get("/trip", response_model=List[TripResponse])
async def list_trips(user_id: Optional[int] = Query(None, description="Filter trips by user ID")):
    """List all trips for a specific user or all trips if no user_id provided"""
    try:
        if user_id:
            trips = snowflake_db.list_trips(user_id)
        else:
            # If no user_id provided, return all trips (for demo purposes)
            # In production, you'd want to implement proper authentication
            trips = snowflake_db.execute_query("SELECT * FROM TRIPS ORDER BY DATE_START DESC")
        return trips
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch trips: {str(e)}")

@router.get("/trip/{trip_id}", response_model=TripResponse)
async def get_trip(trip_id: int):
    """Get a specific trip by ID"""
    try:
        trip = snowflake_db.get_trip_by_id(trip_id)
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found")
        
        return trip
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch trip: {str(e)}")

@router.get("/trip/{trip_id}/legs", response_model=List[TripLegResponse])
async def get_trip_legs(trip_id: int):
    """Get all trip legs for a specific trip"""
    try:
        # First verify the trip exists
        trip = snowflake_db.get_trip_by_id(trip_id)
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found")
        
        trip_legs = snowflake_db.get_trip_legs(trip_id)
        return trip_legs
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch trip legs: {str(e)}")

@router.get("/trip/{trip_id}/hotels")
async def get_trip_hotels(trip_id: int):
    """Get all hotels booked in a specific trip"""
    try:
        # First verify the trip exists
        trip = snowflake_db.get_trip_by_id(trip_id)
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found")
        
        hotels = snowflake_db.get_hotels_in_trip(trip_id)
        return {"hotels": hotels}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch trip hotels: {str(e)}")

@router.post("/trip", response_model=dict)
async def create_trip(trip_data: TripCreate):
    """Create a new trip"""
    try:
        trip_id = snowflake_db.create_trip(
            trip_data.user_id, 
            trip_data.date_start.isoformat() if trip_data.date_start else None,
            trip_data.date_end.isoformat() if trip_data.date_end else None
        )
        if trip_id:
            return {"trip_id": trip_id, "message": "Trip created successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to create trip")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create trip: {str(e)}")

@router.post("/trips/{trip_id}/legs", response_model=dict)
async def add_trip_leg(trip_id: int, trip_leg_data: TripLegCreate):
    """Add a trip leg to a trip"""
    try:
        # Verify the trip exists
        trip = snowflake_db.get_trip_by_id(trip_id)
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found")
        
        trip_leg_id = snowflake_db.add_trip_leg(
            trip_id, 
            trip_leg_data.user_id, 
            trip_leg_data.hotel_id,
            trip_leg_data.arrival_date.isoformat() if trip_leg_data.arrival_date else None,
            trip_leg_data.departure_date.isoformat() if trip_leg_data.departure_date else None,
            trip_leg_data.stay_price or 0.0
        )
        if trip_leg_id:
            return {"trip_leg_id": trip_leg_id, "message": "Trip leg added successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to add trip leg")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add trip leg: {str(e)}")
