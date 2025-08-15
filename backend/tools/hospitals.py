import os
import httpx
from typing import List, Dict

PLACES_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

async def nearby_hospitals(latitude: float, longitude: float, radius_m: int = 5000, max_results: int = 5) -> List[Dict]:
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_MAPS_API_KEY not set")

    params = {
        "key": api_key,
        "location": f"{latitude},{longitude}",
        "radius": radius_m,
        "type": "hospital",
        "opennow": "true",
    }

    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(PLACES_URL, params=params)
        r.raise_for_status()
        data = r.json()

    out = []
    for place in data.get("results", [])[:max_results]:
        out.append({
            "name": place.get("name"),
            "address": place.get("vicinity"),
            "rating": place.get("rating"),
            "user_ratings_total": place.get("user_ratings_total"),
            "location": place.get("geometry", {}).get("location"),
            "place_id": place.get("place_id"),
            "maps_url": f"https://www.google.com/maps/place/?q=place_id:{place.get('place_id')}",
            "open_now": place.get("opening_hours", {}).get("open_now"),
        })
    return out
