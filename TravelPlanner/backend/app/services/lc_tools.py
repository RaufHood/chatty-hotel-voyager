from langchain.tools import Tool
from typing import Any
from app.services import hotel_ops

def hotel_search_sync(city: str, check_in: str, check_out: str) -> list[dict]:
    """Synchronous wrapper for hotel search"""
    import asyncio
    try:
        # Run the async function in a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(hotel_ops.search_hotels(city, check_in, check_out))
        loop.close()
        return result
    except Exception as e:
        print(f"Error in hotel search: {e}")
        return []

hotel_search_tool = Tool(
    name="hotel_search",
    description="Search hotels by city and dates; returns a list of hotel dicts.",
    func=hotel_search_sync,
)

def select_best_hotel_sync(hotels: list[dict], budget: int | None = None) -> dict[str, Any]:
    """Pick best hotel using budget & rating heuristics."""
    if not hotels:
        return {}
    sorted_ = sorted(hotels, key=lambda h: (h["price"], -h["rating"]))
    if budget:
        sorted_ = [h for h in sorted_ if h["price"] <= budget]
    return sorted_[0] if sorted_ else {}

hotel_select_tool = Tool(
    name="choose_hotel",
    description="Choose the single best hotel from a list given an optional budget.",
    func=select_best_hotel_sync,
)
