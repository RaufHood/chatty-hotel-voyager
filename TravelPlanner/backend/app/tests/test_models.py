import pytest
from datetime import datetime
from app.models.user import User
from app.models.hotel import Hotel
from app.models.trip import Trip
from app.models.trip_leg import TripLeg

def test_user_model():
    """Test User model creation and validation"""
    user = User(
        email="test@example.com",
        name="John",
        surname="Doe",
        auto_token="test_token_123"
    )
    
    assert user.email == "test@example.com"
    assert user.name == "John"
    assert user.surname == "Doe"
    assert user.auto_token == "test_token_123"
    assert user.__tablename__ == "USERS"

def test_hotel_model():
    """Test Hotel model creation and validation"""
    hotel = Hotel(
        hotel_name="Grand Hotel",
        stars=5,
        rating=4.5,
        latitude=40.7128,
        longitude=-74.0060,
        country_code="US",
        city_code="NYC",
        hotel_type="Luxury"
    )
    
    assert hotel.hotel_name == "Grand Hotel"
    assert hotel.stars == 5
    assert hotel.rating == 4.5
    assert hotel.latitude == 40.7128
    assert hotel.longitude == -74.0060
    assert hotel.country_code == "US"
    assert hotel.city_code == "NYC"
    assert hotel.hotel_type == "Luxury"
    assert hotel.__tablename__ == "HOTELS"

def test_trip_model():
    """Test Trip model creation and validation"""
    trip = Trip(
        user_id=1,
        date_start=datetime(2024, 1, 1),
        date_end=datetime(2024, 1, 7)
    )
    
    assert trip.user_id == 1
    assert trip.date_start == datetime(2024, 1, 1)
    assert trip.date_end == datetime(2024, 1, 7)
    assert trip.__tablename__ == "TRIPS"

def test_trip_leg_model():
    """Test TripLeg model creation and validation"""
    trip_leg = TripLeg(
        trip_id=1,
        user_id=1,
        hotel_id=1,
        arrival_date=datetime(2024, 1, 1),
        departure_date=datetime(2024, 1, 3),
        stay_price=299.99
    )
    
    assert trip_leg.trip_id == 1
    assert trip_leg.user_id == 1
    assert trip_leg.hotel_id == 1
    assert trip_leg.arrival_date == datetime(2024, 1, 1)
    assert trip_leg.departure_date == datetime(2024, 1, 3)
    assert trip_leg.stay_price == 299.99
    assert trip_leg.__tablename__ == "TRIP_LEGS"

def test_model_relationships():
    """Test that models can be imported and have proper relationships"""
    # Test that all models can be imported
    assert User is not None
    assert Hotel is not None
    assert Trip is not None
    assert TripLeg is not None
    
    # Test that relationships are defined
    assert hasattr(User, 'trips')
    assert hasattr(User, 'trip_legs')
    assert hasattr(Trip, 'user')
    assert hasattr(Trip, 'trip_legs')
    assert hasattr(TripLeg, 'trip')
    assert hasattr(TripLeg, 'user')
    assert hasattr(TripLeg, 'hotel')
    assert hasattr(Hotel, 'trip_legs') 