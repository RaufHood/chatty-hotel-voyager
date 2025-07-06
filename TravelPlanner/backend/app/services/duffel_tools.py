# duffel_tools.py – Duffel API v2 helper tools for LangChain agents
from __future__ import annotations

import os
import sys
import requests
import urllib.parse as _urlparse
from typing import Dict, List, Optional

from langchain_core.tools import tool

###############################################################################
# Configuration
###############################################################################

DUFFEL_API_KEY: Optional[str] = os.getenv("DUFFEL_API_KEY")
if not DUFFEL_API_KEY:
    sys.stderr.write("[ERROR] DUFFEL_API_KEY environment variable not set.\n")
    sys.exit(1)

BASE_URL: str = "https://api.duffel.com"
HEADERS: Dict[str, str] = {
    "Authorization": f"Bearer {DUFFEL_API_KEY}",
    "Duffel-Version": "v2",  # use Duffel API v2 for all requests
    "Accept": "application/json",
    "Content-Type": "application/json",
}

###############################################################################
# Internal utilities
###############################################################################

def _duffel_request(
    method: str,
    endpoint: str,
    *,
    json_data: Optional[dict] = None,
    timeout: int = 30,
) -> Dict:
    """Thin wrapper around ``requests`` that standardises error handling.

    Args:
        method: HTTP verb ("GET", "POST", ...).
        endpoint: Path starting with '/'. May include query parameters.
        json_data: JSON body for POST/PATCH requests, provided **without** Duffel's
            wrapper. This helper automatically wraps payloads in {"data": ...}
            when necessary.
        timeout: Request timeout in seconds.

    Returns:
        On success      – the *data* object (Duffel wraps everything in a top‑level
                          ``data`` field).
        On HTTP error   – ``{"error": "API Request Failed", "details": <body>}``
                          so the LLM agent can inspect codes/messages.
    """
    url: str = f"{BASE_URL}{endpoint}"

    try:
        resp = requests.request(method, url, headers=HEADERS, json=json_data, timeout=timeout)
        resp.raise_for_status()
        body = resp.json()
        # Almost every Duffel endpoint responds with a {"data": ...} wrapper; if
        # it's not present just return the body untouched.
        return body.get("data", body)

    except requests.exceptions.HTTPError as exc:
        err_body: Dict = {}
        try:
            err_body = exc.response.json()
        except Exception:
            err_body = {"message": exc.response.text}
        sys.stderr.write(f"API Error: {exc.response.status_code} – {err_body}\n")
        return {"error": "API Request Failed", "details": err_body}

###############################################################################
# Public LangChain tools
###############################################################################

@tool
def list_airports(query: str) -> List[Dict]:
    """Return airports or cities that match *query*.

    This wraps Duffel's *Place Suggestions* endpoint. Typical usage is to
    convert user‑friendly city names into IATA codes before a search.
    """
    q = _urlparse.quote(query)
    return _duffel_request("GET", f"/places/suggestions?query={q}")


@tool
def search_flights(
    origin: str,
    destination: str,
    departure_date: str,
    *,
    return_date: Optional[str] = None,
    adults: int = 1,
    cabin_class: str = "economy",
) -> Dict:
    """Search for flight offers.

    Args:
        origin: IATA code of departure airport (e.g. "LHR").
        destination: IATA code of arrival airport (e.g. "JFK").
        departure_date: Date of outbound flight (YYYY‑MM‑DD).
        return_date: Optional – date of inbound flight for return searches.
        adults: Number of adult passengers.
        cabin_class: "economy" (default), "premium_economy", "business", or "first".

    The function performs a synchronous search by calling ``/air/offer_requests``
    with the default ``return_offers=true`` query parameter so that a list of
    offers is returned immediately in the response.
    """
    if adults < 1:
        return {"error": "At least one adult passenger is required."}

    slices: List[Dict[str, str]] = [
        {
            "origin": origin.upper(),
            "destination": destination.upper(),
            "departure_date": departure_date,
        }
    ]
    if return_date:
        slices.append(
            {
                "origin": destination.upper(),
                "destination": origin.upper(),
                "departure_date": return_date,
            }
        )

    payload: Dict = {
        "slices": slices,
        "cabin_class": cabin_class,
        "passengers": [{"type": "adult"} for _ in range(adults)],
    }

    # ``return_offers=true`` as query param makes the search synchronous.
    endpoint: str = "/air/offer_requests?return_offers=true"
    return _duffel_request("POST", endpoint, json_data={"data": payload})


@tool
def retrieve_offer(offer_id: str) -> Dict:
    """Fetch the latest details for a flight offer by *offer_id*."""
    return _duffel_request("GET", f"/air/offers/{offer_id}")


@tool
def book_flight(offer_id: str, passengers: List[Dict[str, str]]) -> Dict:
    """Create an order (i.e. book a flight) for the specified offer.

    Args:
        offer_id: ID of the offer returned by ``search_flights``.
        passengers: List of passenger dictionaries. Each dictionary **must**
            contain these keys:
              - given_name
              - family_name
              - born_on        (YYYY‑MM‑DD)
              - gender         ('m' or 'f')
              - title          ('mr', 'mrs', 'ms', etc.)
              - email
              - phone_number   (E.164 format, e.g. "+447911123456")

    Returns:
        The created order object on success, or a structured error payload.
    """
    # ---------------------------------------------------------------------
    # 1) Retrieve latest offer to confirm price + get passenger IDs
    # ---------------------------------------------------------------------
    offer = _duffel_request("GET", f"/air/offers/{offer_id}")
    if "error" in offer:
        return {"error": "Failed to fetch offer before booking.", "details": offer}

    offer_passengers: List[Dict] = offer.get("passengers", [])
    if len(passengers) != len(offer_passengers):
        return {
            "error": "Passenger count mismatch",
            "details": f"Offer expects {len(offer_passengers)} passenger(s); {len(passengers)} provided."
        }

    # ---------------------------------------------------------------------
    # 2) Build passengers section for the order payload
    # ---------------------------------------------------------------------
    booking_passengers: List[Dict[str, str]] = []
    required_fields = {
        "given_name", "family_name", "born_on", "gender", "title", "email", "phone_number"
    }
    for idx, (user_p, offer_p) in enumerate(zip(passengers, offer_passengers)):
        missing = required_fields - user_p.keys()
        if missing:
            return {
                "error": f"Missing field(s) for passenger {idx}: {', '.join(sorted(missing))}"}

        passenger_payload: Dict[str, str] = {
            "id": offer_p.get("id"),  # link to offer passenger id
            "given_name": user_p["given_name"],
            "family_name": user_p["family_name"],
            "born_on": user_p["born_on"],
            "gender": user_p["gender"],
            "title": user_p["title"],
            "email": user_p["email"],
            "phone_number": user_p["phone_number"],
        }
        booking_passengers.append(passenger_payload)

    # ---------------------------------------------------------------------
    # 3) Payment via Duffel balance (instant order)
    # ---------------------------------------------------------------------
    total_amount: str = offer.get("total_amount")
    total_currency: str = offer.get("total_currency")

    order_payload: Dict = {
        "type": "instant",
        "selected_offers": [offer_id],
        "payments": [
            {
                "type": "balance",
                "amount": total_amount,
                "currency": total_currency,
            }
        ],
        "passengers": booking_passengers,
    }

    return _duffel_request("POST", "/air/orders", json_data={"data": order_payload})
