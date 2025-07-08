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

async def search_hotels(city: str, check_in: str, check_out: str, rooms: int = 1, adults: int = 2, children: int = 0) -> List[Dict[str, Any]]:
    """
    Search for hotels in a given city with check-in and check-out dates.
    
    Args:
        city: City name to search for hotels
        check_in: Check-in date (YYYY-MM-DD format)
        check_out: Check-out date (YYYY-MM-DD format)
        rooms: Number of rooms (default: 1)
        adults: Number of adults (default: 2)
        children: Number of children (default: 0)
    
    Returns:
        List of hotel dictionaries with hotel information
    """
    try:
        # Check if we have API credentials
        if not HOTELBEDS_API_KEY or not HOTELBEDS_SECRET:
            raise ValueError("Hotelbeds API credentials not configured")
        
        # Use the exact dates provided by the user - no hardcoded fallbacks
        check_in_date = datetime.strptime(check_in, "%Y-%m-%d")
        check_out_date = datetime.strptime(check_out, "%Y-%m-%d")
        
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
                    "rooms": rooms,
                    "adults": adults,
                    "children": children
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
                    for hotel_data in data["hotels"]["hotels"]:  # No hardcoded limit
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

async def get_hotel_price(hotel_code: str, check_in: str, check_out: str) -> Dict[str, Any]:
    """
    Get hotel price by doing an availability search for the specific hotel
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
            "hotels": {
                "hotel": [int(hotel_code)]
            }
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{HOTELBEDS_BASE_URL}/hotel-api/1.0/hotels",
                json=payload,
                headers=headers
            )
            
            logger.info(f"Hotel price API response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Hotel price API response: {data}")
                
                if "hotels" in data and "hotels" in data["hotels"] and data["hotels"]["hotels"]:
                    hotel_data = data["hotels"]["hotels"][0]
                    logger.info(f"Found hotel data: {hotel_data}")
                    
                    if "rooms" in hotel_data and hotel_data["rooms"]:
                        room = hotel_data["rooms"][0]
                        logger.info(f"Found room data: {room}")
                        
                        if "rates" in room and room["rates"]:
                            rate = room["rates"][0]
                            logger.info(f"Found rate data: {rate}")
                            
                            return {
                                "price": float(rate.get("net", 0)),
                                "currency": rate.get("currency", "EUR"),
                                "originalPrice": float(rate.get("gross", 0))
                            }
                        else:
                            logger.warning("No rates found in room data")
                    else:
                        logger.warning("No rooms found in hotel data")
                else:
                    logger.warning("No hotels found in API response")
            else:
                logger.error(f"Hotel price API error: {response.text}")
            
            return {"price": 0, "currency": "EUR", "originalPrice": 0}
            
    except Exception as e:
        logger.error(f"Error getting hotel price: {e}")
        return {"price": 0, "currency": "EUR", "originalPrice": 0}

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
                
                # Get hotel name properly
                hotel_name = hotel_data.get('name', {})
                if isinstance(hotel_name, dict):
                    hotel_name = hotel_name.get('content', f'Hotel {hotel_code}')
                elif isinstance(hotel_name, str):
                    hotel_name = hotel_name
                else:
                    hotel_name = f'Hotel {hotel_code}'
                
                # Get location properly
                location = hotel_data.get('city', {}).get('content', 'Unknown Location')
                
                # Get images properly
                images = []
                if 'images' in hotel_data and hotel_data['images']:
                    for img in hotel_data['images']:
                        if 'path' in img:
                            images.append(img['path'])
                
                # Get facilities/amenities properly - convert numeric codes to user-friendly format
                amenities = []
                if 'facilities' in hotel_data and hotel_data['facilities']:
                    for facility in hotel_data['facilities']:
                        if isinstance(facility, dict) and 'facilityGroupCode' in facility:
                            amenity_info = get_amenity_info(facility['facilityGroupCode'])
                            amenities.append({
                                "icon": amenity_info["icon"],
                                "label": amenity_info["name"]
                            })
                        elif isinstance(facility, (str, int)):
                            # Handle both string and numeric facility codes
                            try:
                                facility_code = int(facility) if isinstance(facility, str) else facility
                                amenity_info = get_amenity_info(facility_code)
                                amenities.append({
                                    "icon": amenity_info["icon"],
                                    "label": amenity_info["name"]
                                })
                            except (ValueError, TypeError):
                                # If conversion fails, use the original value
                                amenities.append({
                                    "icon": "star",
                                    "label": str(facility)
                                })
                
                # Remove duplicates while preserving order
                unique_amenities = []
                seen = set()
                for amenity in amenities:
                    amenity_key = (amenity["icon"], amenity["label"])
                    if amenity_key not in seen:
                        seen.add(amenity_key)
                        unique_amenities.append(amenity)
                amenities = unique_amenities
                
                return {
                    "id": hotel_code,
                    "name": {"content": hotel_name},
                    "location": location,
                    "price": 0,  # Price will be determined by availability search
                    "originalPrice": 0,
                    "rating": _parse_rating(hotel_data.get('categoryCode', '3')),
                    "reviews": 0,
                    "images": images if images else [
                        "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&h=600&fit=crop",
                        "https://images.unsplash.com/photo-1521783988139-89397d761dce?w=800&h=600&fit=crop",
                        "https://images.unsplash.com/photo-1564501049412-61c2a3083791?w=800&h=600&fit=crop"
                    ],
                    "type": hotel_data.get('categoryName', 'Hotel'),
                    "description": hotel_data.get('description', {}).get('content', 'Modern hotel with excellent amenities'),
                    "amenities": amenities
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

def get_amenity_info(code):
    """
    Convert Hotelbeds amenity codes to user-friendly names and icons.
    Based on OTA Room Amenity Type codes documentation.
    """
    amenity_map = {
        # Basic amenities
        2: {"name": "Air conditioning", "icon": "thermometer"},
        3: {"name": "Alarm clock", "icon": "clock"},
        5: {"name": "AM/FM radio", "icon": "radio"},
        7: {"name": "Terrace", "icon": "home"},
        8: {"name": "Barbeque grills", "icon": "flame"},
        9: {"name": "Bath tub with spray jets", "icon": "bath"},
        10: {"name": "Bathrobe", "icon": "shirt"},
        11: {"name": "Bathroom amenities (free toiletries)", "icon": "droplets"},
        13: {"name": "Bathtub", "icon": "bath"},
        14: {"name": "Bathtub only", "icon": "bath"},
        15: {"name": "Bath or Shower", "icon": "bath"},
        16: {"name": "Bidet", "icon": "droplets"},
        18: {"name": "Cable television", "icon": "tv"},
        19: {"name": "Coffee/Tea maker", "icon": "coffee"},
        20: {"name": "Color television", "icon": "tv"},
        21: {"name": "Computer", "icon": "monitor"},
        22: {"name": "Connecting rooms", "icon": "door-open"},
        25: {"name": "Cordless phone", "icon": "phone"},
        28: {"name": "Desk", "icon": "desk"},
        29: {"name": "Desk with lamp", "icon": "desk"},
        30: {"name": "Deckchairs", "icon": "armchair"},
        32: {"name": "Dishwasher", "icon": "utensils"},
        38: {"name": "Fax machine", "icon": "printer"},
        40: {"name": "Garden", "icon": "trees"},
        41: {"name": "Fireplace", "icon": "flame"},
        46: {"name": "Free movies/video", "icon": "tv"},
        47: {"name": "Full kitchen", "icon": "chef-hat"},
        49: {"name": "Grecian tub", "icon": "bath"},
        50: {"name": "Hairdryer", "icon": "wind"},
        55: {"name": "Iron (ironing facilities)", "icon": "iron"},
        56: {"name": "Ironing board", "icon": "iron"},
        57: {"name": "Whirlpool", "icon": "bath"},
        59: {"name": "Kitchen", "icon": "chef-hat"},
        60: {"name": "Kitchen supplies", "icon": "utensils"},
        61: {"name": "Kitchenette", "icon": "chef-hat"},
        63: {"name": "Laptop", "icon": "laptop"},
        64: {"name": "Large desk", "icon": "desk"},
        68: {"name": "Microwave", "icon": "microwave"},
        69: {"name": "Minibar", "icon": "wine"},
        70: {"name": "Towels", "icon": "shirt"},
        71: {"name": "Elevators", "icon": "elevator"},
        72: {"name": "Multi-line phone", "icon": "phone"},
        73: {"name": "Foyer", "icon": "door-open"},
        74: {"name": "Reception", "icon": "door-open"},
        77: {"name": "Oven", "icon": "chef-hat"},
        78: {"name": "Pay per view movies on TV", "icon": "tv"},
        80: {"name": "Phone in bathroom", "icon": "phone"},
        81: {"name": "Plates and bowls", "icon": "utensils"},
        85: {"name": "Private bathroom", "icon": "bath"},
        88: {"name": "Refrigerator", "icon": "refrigerator"},
        89: {"name": "Refrigerator with ice maker", "icon": "refrigerator"},
        91: {"name": "Safe", "icon": "shield"},
        92: {"name": "Safe", "icon": "shield"},
        94: {"name": "Separate closet", "icon": "cabinet"},
        97: {"name": "Shower only", "icon": "shower"},
        98: {"name": "Silverware/utensils", "icon": "utensils"},
        99: {"name": "Sitting area", "icon": "armchair"},
        103: {"name": "Speaker phone", "icon": "phone"},
        105: {"name": "Stove", "icon": "chef-hat"},
        107: {"name": "Telephone", "icon": "phone"},
        108: {"name": "Telephone for hearing impaired", "icon": "phone"},
        111: {"name": "Trouser Press", "icon": "iron"},
        115: {"name": "VCR movies", "icon": "tv"},
        117: {"name": "Video games", "icon": "gamepad"},
        119: {"name": "Wake-up calls", "icon": "clock"},
        126: {"name": "Air conditioning individually controlled", "icon": "thermometer"},
        127: {"name": "Bathtub & whirlpool separate", "icon": "bath"},
        129: {"name": "CD player", "icon": "disc"},
        133: {"name": "Desk with electrical outlet", "icon": "desk"},
        138: {"name": "Marble bathroom", "icon": "bath"},
        139: {"name": "List of movie channels available", "icon": "tv"},
        141: {"name": "Oversized bathtub", "icon": "bath"},
        142: {"name": "Shower", "icon": "shower"},
        144: {"name": "Soundproofed room", "icon": "volume-x"},
        146: {"name": "Tables and chairs", "icon": "table"},
        147: {"name": "Two-line phone", "icon": "phone"},
        149: {"name": "Washer/dryer", "icon": "washing-machine"},
        155: {"name": "Separate tub and shower", "icon": "bath"},
        157: {"name": "Ceiling fan", "icon": "fan"},
        158: {"name": "CNN available", "icon": "tv"},
        162: {"name": "Closets in room", "icon": "cabinet"},
        163: {"name": "DVD player", "icon": "disc"},
        164: {"name": "Mini-refrigerator", "icon": "refrigerator"},
        166: {"name": "Self-controlled heating/cooling system", "icon": "thermometer"},
        167: {"name": "Toaster", "icon": "chef-hat"},
        193: {"name": "Shared bathroom", "icon": "bath"},
        194: {"name": "Telephone TDD/Textphone", "icon": "phone"},
        210: {"name": "Satellite television", "icon": "tv"},
        214: {"name": "iPod docking station", "icon": "smartphone"},
        217: {"name": "Satellite radio", "icon": "radio"},
        218: {"name": "Video on demand", "icon": "tv"},
        220: {"name": "Gulf view", "icon": "waves"},
        223: {"name": "Mountain view", "icon": "mountain"},
        224: {"name": "Ocean view", "icon": "waves"},
        228: {"name": "Slippers", "icon": "shirt"},
        230: {"name": "Chair provided with desk", "icon": "armchair"},
        234: {"name": "Luxury linen type", "icon": "bed"},
        245: {"name": "Private pool", "icon": "waves"},
        246: {"name": "High Definition (HD) Flat Panel Television", "icon": "tv"},
        251: {"name": "TV", "icon": "tv"},
        254: {"name": "Video game player", "icon": "gamepad"},
        256: {"name": "Dining room seats", "icon": "table"},
        258: {"name": "Mobile/cellular phones", "icon": "phone"},
        259: {"name": "Movies", "icon": "tv"},
        260: {"name": "Multiple closets", "icon": "cabinet"},
        262: {"name": "Safe large enough to accommodate a laptop", "icon": "shield"},
        265: {"name": "Blu-ray player", "icon": "disc"},
        268: {"name": "Non-allergenic room", "icon": "shield"},
        270: {"name": "Seating area with sofa/chair", "icon": "armchair"},
        271: {"name": "Separate toilet area", "icon": "door-open"},
        273: {"name": "Widescreen TV", "icon": "tv"},
        276: {"name": "Separate tub or shower", "icon": "bath"},
        280: {"name": "Plunge pool", "icon": "waves"},
        
        # Extended amenities (5000+ series)
        5001: {"name": "Coffee/Tea maker", "icon": "coffee"},
        5003: {"name": "Mini-bar", "icon": "wine"},
        5004: {"name": "Shower", "icon": "shower"},
        5005: {"name": "Bath", "icon": "bath"},
        5006: {"name": "Safe Deposit Box", "icon": "shield"},
        5007: {"name": "Pay-per-view Channels", "icon": "tv"},
        5008: {"name": "TV", "icon": "tv"},
        5009: {"name": "Telephone", "icon": "phone"},
        5011: {"name": "Air conditioning", "icon": "thermometer"},
        5012: {"name": "Hair Dryer", "icon": "wind"},
        5013: {"name": "Wake Up Service/Alarm-clock", "icon": "clock"},
        5014: {"name": "Hot Tub", "icon": "bath"},
        5015: {"name": "Clothing Iron", "icon": "iron"},
        5016: {"name": "Kitchenette", "icon": "chef-hat"},
        5017: {"name": "Balcony", "icon": "home"},
        5019: {"name": "Bath-robe", "icon": "shirt"},
        5021: {"name": "Radio", "icon": "radio"},
        5022: {"name": "Refrigerator", "icon": "refrigerator"},
        5023: {"name": "Desk", "icon": "desk"},
        5024: {"name": "Shared Bathroom", "icon": "bath"},
        5025: {"name": "Ironing facilities", "icon": "iron"},
        5026: {"name": "Seating area", "icon": "armchair"},
        5027: {"name": "Free Toiletries", "icon": "droplets"},
        5028: {"name": "DVD-Player", "icon": "disc"},
        5029: {"name": "CD-Player", "icon": "disc"},
        5030: {"name": "Fan", "icon": "fan"},
        5032: {"name": "Microwave", "icon": "microwave"},
        5033: {"name": "Dishwasher", "icon": "utensils"},
        5034: {"name": "Washing machine", "icon": "washing-machine"},
        5037: {"name": "Patio", "icon": "home"},
        5038: {"name": "Bathroom", "icon": "bath"},
        5040: {"name": "Heating", "icon": "thermometer"},
        5043: {"name": "Slippers", "icon": "shirt"},
        5044: {"name": "Satellite Channels", "icon": "tv"},
        5045: {"name": "Kitchen", "icon": "chef-hat"},
        5068: {"name": "Cable channels", "icon": "tv"},
        5070: {"name": "Carpeted Floor", "icon": "home"},
        5071: {"name": "Fireplace", "icon": "flame"},
        5075: {"name": "Flat-screen TV", "icon": "tv"},
        5076: {"name": "Private Entrance", "icon": "door-open"},
        5077: {"name": "Sofa", "icon": "armchair"},
        5079: {"name": "Soundproofing", "icon": "volume-x"},
        5080: {"name": "Tiled / Marble floor", "icon": "home"},
        5081: {"name": "View", "icon": "eye"},
        5082: {"name": "Wooden / Parquet floor", "icon": "home"},
        5086: {"name": "Electric Kettle", "icon": "coffee"},
        5087: {"name": "Executive Lounge Access", "icon": "crown"},
        5088: {"name": "iPod Docking Station", "icon": "smartphone"},
        5089: {"name": "Kitchenware", "icon": "utensils"},
        5090: {"name": "Mosquito Net", "icon": "shield"},
        5092: {"name": "Sauna", "icon": "thermometer"},
        5093: {"name": "Private Pool", "icon": "waves"},
        5094: {"name": "Tumble dryer (machine)", "icon": "washing-machine"},
        5095: {"name": "Wardrobe/Closet", "icon": "cabinet"},
        5096: {"name": "Oven", "icon": "chef-hat"},
        5097: {"name": "Stove", "icon": "chef-hat"},
        5098: {"name": "Toaster", "icon": "chef-hat"},
        5099: {"name": "Barbecue", "icon": "flame"},
        5101: {"name": "Computer", "icon": "monitor"},
        5102: {"name": "iPad", "icon": "tablet"},
        5103: {"name": "Game Console", "icon": "gamepad"},
        5108: {"name": "Sea View", "icon": "waves"},
        5109: {"name": "Lake View", "icon": "waves"},
        5110: {"name": "Garden View", "icon": "trees"},
        5111: {"name": "Pool View", "icon": "waves"},
        5112: {"name": "Mountain View", "icon": "mountain"},
        5113: {"name": "Landmark View", "icon": "eye"},
        5114: {"name": "Laptop", "icon": "laptop"},
        5115: {"name": "Allergy-Free", "icon": "shield"},
        5119: {"name": "Blu-ray player", "icon": "disc"},
        5120: {"name": "Coffee Machine", "icon": "coffee"},
        5121: {"name": "City View", "icon": "building"},
        5122: {"name": "River View", "icon": "waves"},
        5123: {"name": "Terrace", "icon": "home"},
        5124: {"name": "Towels", "icon": "shirt"},
        5125: {"name": "Linen", "icon": "bed"},
        5126: {"name": "Dining table", "icon": "table"},
        5127: {"name": "Children highchair", "icon": "baby"},
        5129: {"name": "Outdoor furniture", "icon": "armchair"},
        5130: {"name": "Outdoor dining area", "icon": "utensils"},
        5131: {"name": "Entire property on ground floor", "icon": "home"},
        5132: {"name": "Upper floor reachable by lift", "icon": "elevator"},
        5133: {"name": "Upper floor reachable by stairs only", "icon": "stairs"},
        5134: {"name": "Entire unit wheelchair accessible", "icon": "accessibility"},
        5135: {"name": "Detached", "icon": "home"},
        5136: {"name": "Semi-detached", "icon": "home"},
        5137: {"name": "Private flat in block of flats", "icon": "building"},
        5138: {"name": "Clothes Rack", "icon": "shirt"},
        5139: {"name": "Rollaway bed", "icon": "bed"},
        5140: {"name": "Clothes drying rack", "icon": "shirt"},
        5141: {"name": "Toilet paper", "icon": "droplets"},
        5142: {"name": "Child safety socket covers", "icon": "shield"},
        5143: {"name": "Board games/puzzles", "icon": "gamepad"},
        5144: {"name": "Book/DVD/Music library for children", "icon": "book"},
        5145: {"name": "Baby safety gates", "icon": "shield"},
        5146: {"name": "Sofa bed", "icon": "bed"},
        5147: {"name": "Toilet with grab rails", "icon": "accessibility"},
        5148: {"name": "Adapted bath", "icon": "accessibility"},
        5149: {"name": "Roll in shower", "icon": "accessibility"},
        5150: {"name": "Walk in shower", "icon": "shower"},
        5151: {"name": "Higher level toilet", "icon": "accessibility"},
        5152: {"name": "Low bathroom sink", "icon": "accessibility"},
        5153: {"name": "Bathroom emergency pull cord", "icon": "shield"},
        5154: {"name": "Shower chair", "icon": "accessibility"},
        5157: {"name": "Rooftop pool", "icon": "waves"},
        5158: {"name": "Infinity pool", "icon": "waves"},
        5159: {"name": "Pool with view", "icon": "waves"},
        5160: {"name": "Heated pool", "icon": "waves"},
        5161: {"name": "Salt-water pool", "icon": "waves"},
        5162: {"name": "Plunge pool", "icon": "waves"},
        5163: {"name": "Pool towels", "icon": "shirt"},
        5164: {"name": "Shallow end", "icon": "waves"},
        5165: {"name": "Pool cover", "icon": "waves"},
        5166: {"name": "Wine/champagne", "icon": "wine"},
        5167: {"name": "Bottle of water", "icon": "droplets"},
        5168: {"name": "Fruits", "icon": "apple"},
        5169: {"name": "Chocolate/cookies", "icon": "cookie"},
        5170: {"name": "Trash cans", "icon": "trash"},
        5171: {"name": "Wine glasses", "icon": "wine"},
        5172: {"name": "Game console - Xbox One", "icon": "gamepad"},
        5173: {"name": "Game console - Wii U", "icon": "gamepad"},
        5174: {"name": "Game console - PS4", "icon": "gamepad"},
        5175: {"name": "Children crib/cots", "icon": "baby"},
        5176: {"name": "Toothbrush", "icon": "droplets"},
        5177: {"name": "Shampoo", "icon": "droplets"},
        5178: {"name": "Conditioner", "icon": "droplets"},
        5179: {"name": "Body soap", "icon": "droplets"},
        5180: {"name": "Shower cap", "icon": "droplets"},
        5181: {"name": "Pajamas", "icon": "shirt"},
        5182: {"name": "Yukata", "icon": "shirt"},
        5184: {"name": "Socket near the bed", "icon": "plug"},
        5185: {"name": "Adapter", "icon": "plug"},
        5186: {"name": "Feather pillow", "icon": "bed"},
        5187: {"name": "Non-feather pillow", "icon": "bed"},
        5188: {"name": "Hypoallergenic pillow", "icon": "bed"},
        5189: {"name": "Accessible by Lift", "icon": "elevator"},
        5190: {"name": "Inner courtyard view", "icon": "eye"},
        5191: {"name": "Quiet street view", "icon": "eye"},
        5196: {"name": "Portable Wifi", "icon": "wifi"},
        5198: {"name": "Smartphone", "icon": "smartphone"},
        5199: {"name": "Streaming service (such as Netflix)", "icon": "tv"},
        5200: {"name": "Lockers", "icon": "lock"},
        5201: {"name": "Fire alarms or smoke detectors", "icon": "shield"},
        5202: {"name": "Fire extinguishers", "icon": "shield"},
        5203: {"name": "Metal keys access", "icon": "key"},
        5204: {"name": "Electronic key card access", "icon": "key"},
        5205: {"name": "Reading light", "icon": "lightbulb"},
        5206: {"name": "Earplugs", "icon": "ear"},
        5207: {"name": "Private curtain", "icon": "home"},
        5211: {"name": "Carbon monoxide detector", "icon": "shield"},
        5212: {"name": "Carbon monoxide source", "icon": "shield"},
        5215: {"name": "Air purifiers available", "icon": "wind"},
        5230: {"name": "Single-room air conditioning", "icon": "thermometer"},
        5231: {"name": "Hand sanitiser", "icon": "droplets"},
        
        # Bed types (for reference, though typically handled separately)
        249: {"name": "Double Bed", "icon": "bed"},
        200: {"name": "Futon Mat", "icon": "bed"},
        58: {"name": "King Size Bed", "icon": "bed"},
        86: {"name": "Queen Size Bed", "icon": "bed"},
        102: {"name": "Sofa Bed", "icon": "bed"},
        113: {"name": "Twin Bed", "icon": "bed"},
        203: {"name": "Single Bed", "icon": "bed"},
        4001: {"name": "Bunk Bed", "icon": "bed"},
    }
    
    # Return the amenity info or a default if code not found
    return amenity_map.get(code, {"name": f"Amenity {code}", "icon": "star"})


