from langchain.tools import Tool
from typing import Any
from app.services import hotel_ops

hotel_search_tool = Tool(
    name="hotel_search",
    description="Search hotels by city and dates; returns a list of hotel dicts.",
    func=None,
    coroutine=hotel_ops.search_hotels,
)

async def select_best_hotel(hotels: list[dict], budget: int | None = None) -> dict[str, Any]:
    """Pick best hotel using budget & rating heuristics."""
    sorted_ = sorted(hotels, key=lambda h: (h["price"], -h["rating"]))
    if budget:
        sorted_ = [h for h in sorted_ if h["price"] <= budget]
    return sorted_[0] if sorted_ else {}

hotel_select_tool = Tool(
    name="choose_hotel",
    description="Choose the single best hotel from a list given an optional budget.",
    func=None,
    coroutine=select_best_hotel,
)
