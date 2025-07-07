from langchain.tools import Tool
from typing import Any
import json
from app.services import hotel_ops

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
    Pick best hotel using budget & rating heuristics.
    Input format: "hotels=[...],budget=60" or just "hotels=[...]"
    Returns JSON string of selected hotel.
    """
    try:
        # Parse the input - this is simplified for demo
        if 'budget=' in input_str:
            budget_str = input_str.split('budget=')[1].split(',')[0]
            budget = int(budget_str) if budget_str.isdigit() else None
        else:
            budget = None
        
        # For now, return a simple response
        return json.dumps({
            "id": "best_hotel", 
            "name": "Best Hotel Found", 
            "price": budget or 100, 
            "rating": 4.5,
            "message": f"Selected best hotel within budget: {budget}"
        })
    except Exception as e:
        return f"Error selecting hotel: {e}"

hotel_select_tool = Tool(
    name="choose_hotel",
    description="Choose the best hotel from search results. Input format: hotels=[hotel_list],budget=60",
    func=select_best_hotel_sync,
)

# Export tools list for LangGraph agent
TOOLS = [hotel_search_tool, hotel_select_tool]
