from langchain.tools import StructuredTool
from pydantic import BaseModel, Field
from typing import Any, Literal, Optional
from app.services import hotel_ops

'''
hotel_search_tool = Tool(
    name="hotel_search",
    description="Search hotels by city and dates; returns a list of hotel dicts.",
    func=None,
    coroutine=hotel_ops.search_hotels,
)
'''
class SelectHotelIsInput(BaseModel):
    hotels: list[dict] = Field(..., description="List of hotels from which best hotel is to be selected")
    budget: int = Field(..., description="Budget for the booking")

async def select_best_hotel(hotels: list[dict], budget: int | None = None) -> dict[str, Any]:
    """Pick best hotel using budget & rating heuristics."""
    sorted_ = sorted(hotels, key=lambda h: (h["price"], -h["rating"]))
    if budget:
        sorted_ = [h for h in sorted_ if h["price"] <= budget]
    return sorted_[0] if sorted_ else {}

hotel_select_tool = StructuredTool.from_function(
    name="choose_hotel",
    description="Choose the single best hotel from a list given an optional budget.",
    func=None,
    coroutine=select_best_hotel,
    args_schema=SelectHotelIsInput,
)
class BestRatedHotelIsInput(BaseModel):
    dest: str = Field(..., description="Destination city code")
    cin: str = Field(..., description="Check-in date (YYYY-MM-DD)")
    cout: str = Field(..., description="Check-out date (YYYY-MM-DD)")
    top_n: int = Field(10, description="Number of hotels to return")

hotel_highest_rated_tool = StructuredTool.from_function(
    name="get_highest_rated_hotel",
    description="Get the top-n hotels with highest rating with availability in the given dates and location.",
    func=None,
    coroutine=hotel_ops.hotels_highest_rating,
    args_schema=BestRatedHotelIsInput,
)

class CheapestHotelsInput(BaseModel):
    dest: str = Field(..., description="Destination city code")
    cin: str = Field(..., description="Check-in date (YYYY-MM-DD)")
    cout: str = Field(..., description="Check-out date (YYYY-MM-DD)")
    top_n: int = Field(10, description="Number of hotels to return")

hotel_cheapest_tool = StructuredTool.from_function(
    name="get_cheapest_hotels",
    description="Get the hotels with the cheapest rates with availability in the given dates and location.",
    func=None,
    coroutine=hotel_ops.hotels_lowest_prices,
    args_schema=CheapestHotelsInput,
)

class HotelsWithCxlPolicyInput(BaseModel):
    dest: str = Field(..., description="Destination city code")
    cin: str = Field(..., description="Check-in date (YYYY-MM-DD)")
    cout: str = Field(..., description="Check-out date (YYYY-MM-DD)")
    policy: Literal["NRF", "FREE", "BEFORE_DATE"] = Field(..., description="Cancellation policy type")
    deadline: Optional[str] = Field(None, description="Deadline date (YYYY-MM-DD) for BEFORE_DATE policy")

hotel_cxl_policy_tool = StructuredTool.from_function(
    name="get_hotels_with_compatible_cancellation",
    description="Get hotels with matching cancellation policy as mentioned in user prompt with availability in the given dates and location. Available cancellation policies are FREE=cancellationPolicies is empty; NRF=rateClass ‘NRF’; BEFORE_DATE=first policy date>deadline.",
    func=None,
    coroutine=hotel_ops.hotels_with_cxl_policy,
    args_schema=HotelsWithCxlPolicyInput
)

