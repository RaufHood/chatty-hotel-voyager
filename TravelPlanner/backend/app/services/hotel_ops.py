"""Wrapper around the HotelOperations external API"""

import httpx
from typing import List, Literal, Dict, Any, Tuple
import logging
import time 
import hashlib 
import json 
import asyncio 
import datetime
from async_lru import alru_cache   
from app.core.settings import settings 
from collections import defaultdict
from operator import itemgetter

logger = logging.getLogger(__name__)

    # async‑aware LRU cache  🡅

API_KEY    = settings.hotelbeds_api_key
API_SECRET = settings.hotelbeds_api_secret
BASE_URL   = "https://api.test.hotelbeds.com"

# --- pooled async client -----------------------------------------
_http: httpx.AsyncClient | None = None          # created lazily
_LIMIT = asyncio.Semaphore(45)      

def _signature() -> str:
    now = int(time.time())
    return hashlib.sha256(f"{API_KEY}{API_SECRET}{now}".encode()).hexdigest()

def _headers() -> dict[str, str]:
    return {
        "Api-key": API_KEY,
        "X-Signature": _signature(),
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

async def _client() -> httpx.AsyncClient:
    global _http
    if _http is None:
        _http = httpx.AsyncClient(base_url=BASE_URL, timeout=20.0)
    return _http

# --- availability && helper functions-------------------------------------------------
async def availability(dest: str, cin: str, cout: str,
                       rooms: int = 1, adults: int = 2,
                       children: int = 0) -> dict:
    body = {
        "stay": {"checkIn": cin, "checkOut": cout},
        "occupancies": [{"rooms": rooms, "adults": adults, "children": children}],
        "destination": {"code": dest}
    }
    async with _LIMIT:                                      # guard concurrency
        r = await (await _client()).post(
            "/hotel-api/1.0/hotels", headers=_headers(), json=body
        )
    r.raise_for_status()
    try:
        data = r.json()
    except Exception as e:
        print(f"Error parsing JSON: {e}, response text: {r.text}")
        raise
    return data


async def _flatten_rates(raw: dict):
    if not isinstance(raw, dict):
        print(f"Expected dict, got {type(raw)}: {raw}")
        raise ValueError("Expected a dict as input to _flatten_rates")
    out = []
    for h in raw.get("hotels", []):
        for room in h.get("rooms", []):
            for rate in room.get("rates", []):
                rate["hotelCode"] = h["code"]
                out.append(rate)
    return out

@alru_cache(maxsize=1024, ttl=60*60)                         # 1‑hour TTL
async def hotel_static(*codes: Tuple[str, ...]) -> Dict[str, dict]:
    query = ",".join(codes)
    async with _LIMIT:
        r = await (await _client()).get(
            "/hotel-content-api/1.0/hotels",
            headers=_headers(),
            params={"fields": "code,name,category", "codes": query, "language": "ENG"}
        )
    r.raise_for_status()
    hotels = r.json().get("hotels", [])
    return {h["code"]: h for h in hotels}

# --- business functions for agent tools-------------------------------------------------


async def hotels_lowest_prices(dest, cin, cout, top_n=10):
    flat = await _flatten_rates(await availability(dest, cin, cout))
    return sorted(flat, key=lambda r: float(r["net"]))[:top_n]

async def hotels_highest_rating(dest, cin, cout, top_n=5):
    flat   = await _flatten_rates(await availability(dest, cin, cout))
    codes  = tuple({r["hotelCode"] for r in flat})
    static = await hotel_static(*codes)
    rated  = sorted(static.values(),
                    key=lambda h: int(h["category"]["simpleCode"]), reverse=True)
    return rated[:top_n]

async def hotels_with_cxl_policy(dest: str, cin: str, cout: str,
                            policy: Literal["NRF", "FREE", "BEFORE_DATE"],
                            deadline: str | None = None):
    """FREE = cancellationPolicies is empty; NRF = rateClass ‘NRF’;
       BEFORE_DATE = first policy date > deadline."""
    flat = await _flatten_rates(await availability(dest, cin, cout))
    if policy == "NRF":
        return [r for r in flat if r["rateClass"] == "NRF"]
    if policy == "FREE":
        return [r for r in flat if not r.get("cancellationPolicies")]
    if policy == "BEFORE_DATE":
        dt = datetime.fromisoformat(deadline)
        def ok(r):
            cps = r.get("cancellationPolicies", [])
            return all(datetime.fromisoformat(c["from"]) > dt for c in cps)
        return [r for r in flat if ok(r)]
    raise ValueError("Unknown policy flag")


async def hotels_best_promo_board(dest: str, cin: str, cout: str,
                            board: str = "BB", top_n: int = 10):
    flat = await _flatten_rates(await availability(dest, cin, cout))
    filtered = [r for r in flat if r["boardCode"] == board]
    scored   = sorted(filtered,
                      key=lambda r: len(r.get("promotions", [])),
                      reverse=True)
    return scored[:top_n]

print(_signature())