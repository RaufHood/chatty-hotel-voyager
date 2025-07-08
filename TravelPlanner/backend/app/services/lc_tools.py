from langchain.tools import Tool
from typing import Any
import json
from app.services import hotel_ops

# Global variable to store last hotel search results for frontend
_last_hotel_cards = None

def hotel_search_sync(input_str: str) -> str:
    """
    Search hotels by city and dates. 
    Input format: "city=Barcelona,check_in=2025-07-08,check_out=2025-07-09"
    Returns JSON string of hotel list.
    """
    import asyncio
    try:
        # Parse the input string
        params = {}
        for param in input_str.split(','):
            key, value = param.split('=', 1)
            params[key.strip()] = value.strip()
        
        city = params.get('city', '')
        check_in = params.get('check_in', '')
        check_out = params.get('check_out', '')
        
        if not all([city, check_in, check_out]):
            return "Error: Missing required parameters. Use format: city=Barcelona,check_in=2025-07-08,check_out=2025-07-09"
        
        # Run the async function in a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(hotel_ops.search_hotels(city, check_in, check_out))
        loop.close()
        
        # Return JSON string
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error in hotel search: {e}"

hotel_search_tool = Tool(
    name="hotel_search",
    description="Search hotels by city and dates. Input format: city=Barcelona,check_in=2025-07-08,check_out=2025-07-09",
    func=hotel_search_sync,
)

def select_best_hotel_sync(input_str: str) -> str:
    """
    Pick top 3 hotels from search results using budget & rating heuristics.
    Input format: "budget=100,hotels=[hotel_data_json]" or just "budget=100"
    Returns JSON string of top 3 selected hotels from actual search results.
    """
    global _last_hotel_cards
    try:
        # Parse input to extract budget and hotels
        budget = None
        hotels_data = []
        
        # Try to extract budget
        if 'budget=' in input_str:
            try:
                budget_part = input_str.split('budget=')[1]
                if ',' in budget_part:
                    budget_str = budget_part.split(',')[0]
                else:
                    budget_str = budget_part
                budget = int(budget_str) if budget_str.replace('.', '').isdigit() else None
            except:
                pass
        else:
            # Try to extract any number from the input
            import re
            numbers = re.findall(r'\d+', input_str)
            if numbers:
                budget = int(numbers[0])
        
        # Try to extract hotels data
        if 'hotels=' in input_str:
            try:
                hotels_part = input_str.split('hotels=')[1]
                hotels_data = json.loads(hotels_part)
            except:
                pass
        
        # No default budget - must be specified by user
        if not budget:
            return json.dumps({
                "error": "Budget must be specified",
                "message": "Please specify a budget for your hotel search",
                "hotel_tool_used": True
            }, indent=2)
        
        # If no hotels data provided, return error message
        if not hotels_data:
            return json.dumps({
                "error": "No hotel search results provided. Please use hotel_search first to get available hotels.",
                "budget": budget,
                "message": "Use hotel_search tool first, then pass the results to choose_hotel",
                "hotel_tool_used": True
            }, indent=2)
        
        # Filter hotels within budget
        affordable_hotels = []
        for hotel in hotels_data:
            hotel_price = hotel.get('price', 0)
            if hotel_price <= budget:
                affordable_hotels.append(hotel)
        
        # If no hotels within budget, inform the user
        if not affordable_hotels:
            cheapest_hotels = sorted(hotels_data, key=lambda x: x.get('price', 0))[:3]
            
            # Transform to frontend format for cheapest alternatives
            frontend_cheapest = []
            for hotel in cheapest_hotels:
                frontend_cheapest.append({
                    "id": str(hotel.get('id', 'unknown')),
                    "name": hotel.get('name', 'Unknown Hotel'),
                    "location": hotel.get('location', 'Unknown'),
                    "price": hotel.get('price', 0),
                    "rating": hotel.get('rating', 0),
                    "image": _get_hotel_image(hotel.get('category', '')),
                    "type": _transform_category_to_type(hotel.get('category', 'Standard'))
                })
            
            # Store globally for chat service
            _last_hotel_cards = frontend_cheapest
            
            return json.dumps({
                "error": f"No hotels found within your {budget}€ budget",
                "budget": budget,
                "total_found": len(hotels_data),
                "within_budget": 0,
                "cheapest_alternatives": cheapest_hotels,
                "message": f"No hotels available within {budget}€ budget. Cheapest available options start from {cheapest_hotels[0].get('price', 0)}€",
                "frontend_hotel_cards": frontend_cheapest,
                "hotel_tool_used": True
            }, indent=2)
        
        # Sort by rating (descending) and price (ascending)
        affordable_hotels.sort(key=lambda x: (-x.get('rating', 0), x.get('price', 0)))
        
        # Select top 3
        selected_hotels = affordable_hotels[:3]
        
        # Transform to frontend format
        frontend_hotel_cards = []
        for hotel in selected_hotels:
            frontend_hotel_cards.append({
                "id": str(hotel.get('id', 'unknown')),
                "name": hotel.get('name', 'Unknown Hotel'),
                "location": hotel.get('location', 'Unknown'),
                "price": hotel.get('price', 0),
                "rating": hotel.get('rating', 0),
                "image": _get_hotel_image(hotel.get('category', '')),
                "type": _transform_category_to_type(hotel.get('category', 'Standard')),
                "amenities": hotel.get('amenities', ['Wi-Fi', 'Air Conditioning', 'Room Service'])
            })
        
        # Store globally for chat service
        _last_hotel_cards = frontend_hotel_cards
        
        response = {
            "top_hotels": selected_hotels,
            "budget": budget,
            "total_found": len(hotels_data),
            "within_budget": len([h for h in hotels_data if h.get('price', 0) <= budget]),
            "message": f"Found {len(selected_hotels)} hotels within your {budget}€ budget",
            "frontend_hotel_cards": frontend_hotel_cards,
            "hotel_tool_used": True
        }
        
        return json.dumps(response, indent=2)
        
    except Exception as e:
        return f"Error selecting hotels: {str(e)}"

hotel_select_tool = Tool(
    name="choose_hotel",
    description="Choose the top 3 hotels from search results based on budget. Input format: budget=100,hotels=[hotel_search_results]. Pass the actual hotel search results from hotel_search tool.",
    func=select_best_hotel_sync,
)

from langchain_core.tools import tool
from typing import Any
import json
from app.services import hotel_ops

# Global variable to store last hotel search results for frontend
_last_hotel_cards = None

@tool
def search_and_select_hotels(city: str, check_in: str, check_out: str, budget: int) -> str:
    """
    Search for hotels and select the top 3 based on budget in one step.
    
    Args:
        city: City name (e.g., "Barcelona")
        check_in: Check-in date in YYYY-MM-DD format (e.g., "2025-07-29")
        check_out: Check-out date in YYYY-MM-DD format (e.g., "2025-07-30")
        budget: Maximum budget per night in euros (e.g., 140)
    
    Returns:
        JSON string of top 3 selected hotels from actual search results
    """
    global _last_hotel_cards
    import asyncio
    try:
        if not all([city, check_in, check_out, budget > 0]):
            return "Error: Missing required parameters. Please provide city, check_in, check_out, and budget."
        
        # Search for hotels
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        hotels_data = loop.run_until_complete(hotel_ops.search_hotels(city, check_in, check_out))
        loop.close()
        
        if not hotels_data:
            _last_hotel_cards = []
            return json.dumps({
                "error": f"No hotels found for {city}",
                "budget": budget,
                "message": f"No hotels available for {city} on {check_in} to {check_out}",
                "frontend_hotel_cards": [],
                "hotel_tool_used": True
            }, indent=2)
        
        # Filter hotels within budget
        affordable_hotels = []
        for hotel in hotels_data:
            hotel_price = hotel.get('price', 0)
            if hotel_price <= budget:
                affordable_hotels.append(hotel)
        
        # If no hotels within budget, inform the user
        if not affordable_hotels:
            cheapest_hotels = sorted(hotels_data, key=lambda x: x.get('price', 0))[:3]
            
            # Transform to frontend format for cheapest alternatives
            frontend_cheapest = []
            for hotel in cheapest_hotels:
                frontend_cheapest.append({
                    "id": str(hotel.get('id', 'unknown')),
                    "name": hotel.get('name', 'Unknown Hotel'),
                    "location": hotel.get('location', city),
                    "price": hotel.get('price', 0),
                    "rating": hotel.get('rating', 0),
                    "image": _get_hotel_image(hotel.get('category', '')),
                    "type": _transform_category_to_type(hotel.get('category', 'Standard')),
                    "amenities": hotel.get('amenities', [])
                })
            
            # Store globally for chat service
            _last_hotel_cards = frontend_cheapest
            
            return json.dumps({
                "error": f"No hotels found within your {budget}€ budget",
                "budget": budget,
                "total_found": len(hotels_data),
                "within_budget": 0,
                "cheapest_alternatives": cheapest_hotels,
                "message": f"No hotels available within {budget}€ budget. Cheapest available options start from {cheapest_hotels[0].get('price', 0)}€",
                "frontend_hotel_cards": frontend_cheapest,
                "hotel_tool_used": True
            }, indent=2)
        
        # Sort by rating (descending) and price (ascending)
        affordable_hotels.sort(key=lambda x: (-x.get('rating', 0), x.get('price', 0)))
        
        # Select top 3
        selected_hotels = affordable_hotels[:3]
        
        # Transform to frontend format
        frontend_hotel_cards = []
        for hotel in selected_hotels:
            frontend_hotel_cards.append({
                "id": str(hotel.get('id', 'unknown')),
                "name": hotel.get('name', 'Unknown Hotel'),
                "location": hotel.get('location', city),
                "price": hotel.get('price', 0),
                "rating": hotel.get('rating', 0),
                "image": _get_hotel_image(hotel.get('category', '')),
                "type": _transform_category_to_type(hotel.get('category', 'Standard')),
                "amenities": hotel.get('amenities', [])
            })
        
        # Store globally for chat service
        _last_hotel_cards = frontend_hotel_cards
        
        response = {
            "top_hotels": selected_hotels,
            "city": city,
            "dates": f"{check_in} to {check_out}",
            "budget": budget,
            "total_found": len(hotels_data),
            "within_budget": len([h for h in hotels_data if h.get('price', 0) <= budget]),
            "message": f"Found {len(selected_hotels)} hotels in {city} within your {budget}€ budget",
            "frontend_hotel_cards": frontend_hotel_cards,
            "hotel_tool_used": True
        }
        
        return json.dumps(response, indent=2)
        
    except Exception as e:
        return f"Error in hotel search and selection: {str(e)}"

def clear_last_hotel_cards():
    """Clear the global hotel cards storage"""
    global _last_hotel_cards
    _last_hotel_cards = None

def get_last_hotel_cards():
    """Get the last hotel cards for frontend display"""
    return _last_hotel_cards

def get_hotel_details_sync(hotel_id: str) -> dict:
    """Get detailed hotel information by ID - enhanced mock data based on hotel ID"""
    try:
        # Create realistic mock data based on hotel ID
        if "barcelona" in hotel_id.lower():
            name = "Hotel Barcelona Plaza"
            location = "Plaza Catalunya, Barcelona, Spain"
            price = 112
            originalPrice = 135
            description = "Elegant hotel in the heart of Barcelona, steps away from Plaza Catalunya and Gothic Quarter. Features modern amenities and traditional Catalan charm."
        elif "madrid" in hotel_id.lower():
            name = "Madrid Grand Hotel"
            location = "Gran Via, Madrid, Spain"
            price = 98
            originalPrice = 120
            description = "Luxury hotel on Gran Via with stunning city views. Perfect for exploring Madrid's cultural attractions and vibrant nightlife."
        elif "paris" in hotel_id.lower():
            name = "Paris Central Hotel"
            location = "2nd Arrondissement, Paris, France"
            price = 145
            originalPrice = 170
            description = "Charming Parisian hotel near the Louvre with classic French elegance and modern comfort."
        else:
            # Default hotel based on ID
            name = f"Premium Hotel {hotel_id}"
            location = "City Center"
            price = 89
            originalPrice = 120
            description = "A luxurious hotel in the heart of the city with modern amenities and excellent service. Perfect for business travelers and tourists alike."
        
        hotel_details = {
            "id": hotel_id,
            "name": name,
            "location": location,
            "price": price,
            "originalPrice": originalPrice,
            "rating": 4.5,
            "reviews": 1247,
            "images": [
                "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&h=600&fit=crop",
                "https://images.unsplash.com/photo-1521783988139-89397d761dce?w=800&h=600&fit=crop",
                "https://images.unsplash.com/photo-1564501049412-61c2a3083791?w=800&h=600&fit=crop"
            ],
            "type": "4 Star Hotel",
            "description": description,
            "amenities": [
                {"icon": "Wifi", "label": "Free WiFi"},
                {"icon": "Coffee", "label": "Restaurant"},
                {"icon": "Car", "label": "Parking"},
                {"icon": "Shield", "label": "24/7 Security"},
                {"icon": "Dumbbell", "label": "Fitness Center"},
                {"icon": "Swimming", "label": "Pool"},
                {"icon": "Concierge", "label": "Concierge Service"},
                {"icon": "RoomService", "label": "Room Service"}
            ],
            "facilities": [
                "Business Center",
                "Conference Rooms", 
                "Spa & Wellness",
                "Airport Shuttle",
                "Laundry Service",
                "Pet Friendly"
            ],
            "policies": {
                "checkIn": "15:00",
                "checkOut": "11:00",
                "cancellation": "Free cancellation up to 24 hours before check-in"
            }
        }
        
        return hotel_details
        
    except Exception as e:
        return {"error": f"Failed to get hotel details: {str(e)}"}

def _transform_category_to_type(category: str) -> str:
    """Transform hotel category to user-friendly type"""
    if "5 STARS" in category:
        return "5 Star Hotel"
    elif "4 STARS" in category:
        return "4 Star Hotel"
    elif "3 STARS" in category:
        return "3 Star Hotel"
    elif "2 STARS" in category:
        return "2 Star Hotel"
    elif "1 STARS" in category:
        return "1 Star Hotel"
    elif "APARTMENT" in category:
        return "Apartment"
    elif "HOSTAL" in category:
        return "Hostal"
    else:
        return "Hotel"

def _get_hotel_image(category: str) -> str:
    """Get hotel image based on category"""
    if "5 STARS" in category:
        return "https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=400&h=300&fit=crop"
    elif "4 STARS" in category:
        return "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=400&h=300&fit=crop"
    elif "3 STARS" in category:
        return "https://images.unsplash.com/photo-1521783988139-89397d761dce?w=400&h=300&fit=crop"
    elif "APARTMENT" in category:
        return "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=400&h=300&fit=crop"
    else:
        return "https://images.unsplash.com/photo-1564501049412-61c2a3083791?w=400&h=300&fit=crop"

# Hotel details tool
hotel_details_tool = Tool(
    name="get_hotel_details",
    description="Get detailed hotel information by hotel ID. Input format: hotel_id",
    func=get_hotel_details_sync,
)

# Export tools list for LangGraph agent - use the new @tool decorated function
TOOLS = [search_and_select_hotels, hotel_details_tool]
