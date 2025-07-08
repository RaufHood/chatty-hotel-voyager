"""Wrapper around the Hotelbeds API"""

import httpx
import time
import hashlib
import os
from typing import List, Dict, Any
import logging
from dotenv import load_dotenv
from datetime import datetime, timedelta
from fastapi import HTTPException

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

# Hotelbeds API configuration
HOTELBEDS_API_KEY = os.getenv("HOTEL_BEDS_API_KEY")
HOTELBEDS_SECRET = os.getenv("HOTEL_BEDS_SECRET")
HOTELBEDS_BASE_URL = "https://api.test.hotelbeds.com"

def generate_signature(api_key: str, secret: str) -> str:
    """Generate X-Signature for Hotelbeds API authentication"""
    timestamp = int(time.time())
    signature_string = f"{api_key}{secret}{timestamp}"
    return hashlib.sha256(signature_string.encode('utf-8')).hexdigest()

def _parse_rating(category_code: str) -> float:
    """Parse category code to rating, handling non-numeric values"""
    try:
        # Extract numeric part from codes like '3EST', '4LL', etc.
        numeric_part = ''.join(filter(str.isdigit, str(category_code)))
        if numeric_part:
            rating = float(numeric_part)
            return min(max(rating, 1.0), 5.0)  # Clamp between 1-5
        return 3.0  # Default rating
    except (ValueError, TypeError):
        return 3.0

def city_to_destination_code(city: str) -> str:
    """Convert city name to Hotelbeds destination code"""
    city_mapping = {
        "barcelona": "BCN",
        "madrid": "MAD", 
        "paris": "PAR",
        "london": "LON",
        "rome": "ROM",
        "berlin": "BER",
        "amsterdam": "AMS",
        "vienna": "VIE"
    }
    return city_mapping.get(city.lower(), city.upper()[:3])

async def search_hotels(city: str, check_in: str, check_out: str) -> List[Dict[str, Any]]:
    """
    Search for hotels in a given city with check-in and check-out dates.
    
    Args:
        city: City name to search for hotels
        check_in: Check-in date (YYYY-MM-DD format)
        check_out: Check-out date (YYYY-MM-DD format)
    
    Returns:
        List of hotel dictionaries with hotel information
    """
    try:
        # Check if we have API credentials
        if not HOTELBEDS_API_KEY or not HOTELBEDS_SECRET:
            raise ValueError("Hotelbeds API credentials not configured")
        
        # Ensure we're using future dates
        today = datetime.now()
        check_in_date = datetime.strptime(check_in, "%Y-%m-%d")
        check_out_date = datetime.strptime(check_out, "%Y-%m-%d")
        
        if check_in_date <= today:
            # Use tomorrow as check-in if date is in the past
            check_in_date = today + timedelta(days=1)
            check_out_date = check_in_date + timedelta(days=1)
            check_in = check_in_date.strftime("%Y-%m-%d")
            check_out = check_out_date.strftime("%Y-%m-%d")
            logger.info(f"Using future dates: {check_in} to {check_out}")
        
        logger.info(f"Searching hotels in {city} from {check_in} to {check_out}")
        
        # Convert city to destination code
        destination_code = city_to_destination_code(city)
        
        # Prepare API request
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Api-key": HOTELBEDS_API_KEY,
            "X-Signature": generate_signature(HOTELBEDS_API_KEY, HOTELBEDS_SECRET)
        }
        
        payload = {
            "stay": {
                "checkIn": check_in,
                "checkOut": check_out
            },
            "occupancies": [
                {
                    "rooms": 1,
                    "adults": 2,
                    "children": 0
                }
            ],
            "destination": {
                "code": destination_code
            }
        }
        
        # Make API request
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{HOTELBEDS_BASE_URL}/hotel-api/1.0/hotels",
                json=payload,
                headers=headers
            )
            
            logger.info(f"Hotelbeds API response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Parse hotels from response
                hotels = []
                if "hotels" in data and "hotels" in data["hotels"]:
                    for hotel_data in data["hotels"]["hotels"][:10]:  # Limit to 10 hotels
                        try:
                            hotel = {
                                "id": hotel_data.get("code", "unknown"),
                                "name": hotel_data.get("name", "Unknown Hotel"),
                                "category": hotel_data.get("categoryName", "Standard"),
                                "location": hotel_data.get("destinationName", city),
                                "rating": _parse_rating(hotel_data.get("categoryCode", "3")),
                                "price": 0.0,  # Will be filled from rates if available
                                "currency": "EUR",
                                "description": f"{hotel_data.get('categoryName', 'Standard')} hotel in {city}"
                            }
                            
                            # Extract price from rooms if available
                            if "rooms" in hotel_data and hotel_data["rooms"]:
                                room = hotel_data["rooms"][0]
                                if "rates" in room and room["rates"]:
                                    rate = room["rates"][0]
                                    hotel["price"] = float(rate.get("net", 0))
                                    hotel["currency"] = rate.get("currency", "EUR")
                            
                            hotels.append(hotel)
                            
                        except Exception as parse_error:
                            logger.warning(f"Error parsing hotel data: {parse_error}")
                            continue
                
                logger.info(f"Successfully parsed {len(hotels)} hotels from Hotelbeds API")
                return hotels
                
            else:
                logger.error(f"Hotelbeds API error {response.status_code}: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Hotel search failed: {response.text}"
                )
                
    except ValueError as ve:
        logger.error(f"Configuration error: {ve}")
        raise HTTPException(
            status_code=500,
            detail=f"Service configuration error: {str(ve)}"
        )
    except Exception as e:
        logger.error(f"Error searching hotels: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Hotel search failed: {str(e)}"
        )

async def get_hotel_details(hotel_code: str) -> Dict[str, Any]:
    """
    Get detailed hotel information from Hotelbeds API by hotel code
    """
    try:
        if not HOTELBEDS_API_KEY or not HOTELBEDS_SECRET:
            raise ValueError("Hotelbeds API credentials not configured")
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Api-key": HOTELBEDS_API_KEY,
            "X-Signature": generate_signature(HOTELBEDS_API_KEY, HOTELBEDS_SECRET)
        }
        
        # Get hotel details from Hotelbeds
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{HOTELBEDS_BASE_URL}/hotel-content-api/1.0/hotels/{hotel_code}",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                hotel_data = data.get('hotel', {})
                
                return {
                    "id": hotel_code,
                    "name": hotel_data.get('name', f'Hotel {hotel_code}'),
                    "location": hotel_data.get('city', {}).get('content', 'Unknown Location'),
                    "price": 89,  # Price would come from availability search
                    "originalPrice": 120,
                    "rating": _parse_rating(hotel_data.get('categoryCode', '4')),
                    "reviews": 1247,
                    "images": [
                        "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&h=600&fit=crop",
                        "https://images.unsplash.com/photo-1521783988139-89397d761dce?w=800&h=600&fit=crop",
                        "https://images.unsplash.com/photo-1564501049412-61c2a3083791?w=800&h=600&fit=crop"
                    ],
                    "type": hotel_data.get('categoryName', '4 Star Hotel'),
                    "description": hotel_data.get('description', {}).get('content', 'Modern hotel with excellent amenities'),
                    "amenities": [
                        {"icon": "Wifi", "label": "Free WiFi"},
                        {"icon": "Coffee", "label": "Restaurant"},
                        {"icon": "Car", "label": "Parking"},
                        {"icon": "Shield", "label": "24/7 Security"}
                    ]
                }
            else:
                logger.error(f"Hotelbeds hotel details API error {response.status_code}: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Hotel not found: {response.text}"
                )
                
    except Exception as e:
        logger.error(f"Error getting hotel details: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get hotel details: {str(e)}"
        )


