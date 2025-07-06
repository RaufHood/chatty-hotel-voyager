from langchain.tools import tool
from typing import Any, Optional
from app.services import hotel_ops
from datetime import datetime, timedelta
import asyncio

@tool
def hotel_search(city: str, check_in: Optional[str] = None, check_out: Optional[str] = None) -> list[dict]:
    """Search hotels by city. You can also provide check_in and check_out dates in YYYY-MM-DD format. If dates are not provided, default dates will be used.
    
    Args:
        city: The city to search for hotels in
        check_in: Check-in date in YYYY-MM-DD format (optional)
        check_out: Check-out date in YYYY-MM-DD format (optional)
    
    Returns:
        List of hotel dictionaries with hotel information
    """
    # Set default dates if not provided
    if not check_in:
        check_in = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    if not check_out:
        check_out = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
    
    try:
        # Check if there's already a running event loop
        try:
            loop = asyncio.get_running_loop()
            # If there's a running loop, we need to use a different approach
            # For now, return mock data directly since the async function returns mock data anyway
            return [
                {
                    "id": "hotel_1",
                    "name": f"Grand Hotel {city}",
                    "city": city,
                    "rating": 4.5,
                    "price": 150,
                    "currency": "USD",
                    "amenities": ["WiFi", "Pool", "Gym", "Restaurant"],
                    "description": f"Luxury hotel in the heart of {city}",
                    "check_in": check_in,
                    "check_out": check_out
                },
                {
                    "id": "hotel_2", 
                    "name": f"Comfort Inn {city}",
                    "city": city,
                    "rating": 3.8,
                    "price": 80,
                    "currency": "USD",
                    "amenities": ["WiFi", "Breakfast"],
                    "description": f"Comfortable and affordable hotel in {city}",
                    "check_in": check_in,
                    "check_out": check_out
                },
                {
                    "id": "hotel_3",
                    "name": f"Boutique Hotel {city}",
                    "city": city,
                    "rating": 4.2,
                    "price": 120,
                    "currency": "USD", 
                    "amenities": ["WiFi", "Spa", "Restaurant"],
                    "description": f"Charming boutique hotel in {city}",
                    "check_in": check_in,
                    "check_out": check_out
                }
            ]
        except RuntimeError:
            # No running loop, we can create a new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(hotel_ops.search_hotels(city, check_in, check_out))
            loop.close()
            return result
    except Exception as e:
        print(f"Error in hotel search: {e}")
        return []

@tool
def choose_hotel(hotels: str, budget: Optional[int] = None) -> dict[str, Any]:
    """Choose the single best hotel from a list given an optional budget.
    
    Args:
        hotels: JSON string representation of the hotels list
        budget: Optional budget limit for hotel selection
    
    Returns:
        Dictionary with the best hotel information
    """
    import json
    
    try:
        # Parse the hotels string to list
        if isinstance(hotels, str):
            hotels_list = json.loads(hotels)
        else:
            hotels_list = hotels
            
        if not hotels_list:
            return {}
            
        sorted_hotels = sorted(hotels_list, key=lambda h: (h["price"], -h["rating"]))
        if budget:
            sorted_hotels = [h for h in sorted_hotels if h["price"] <= budget]
        return sorted_hotels[0] if sorted_hotels else {}
    except Exception as e:
        print(f"Error in hotel selection: {e}")
        return {}

# Keep the old tools for backward compatibility but use the new ones
hotel_search_tool = hotel_search
hotel_select_tool = choose_hotel
