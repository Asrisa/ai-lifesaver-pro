import os
import httpx

OW_URL = "https://api.openweathermap.org/data/2.5/weather"

async def current_weather(lat: float, lon: float):
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENWEATHER_API_KEY not set")

    params = {"lat": lat, "lon": lon, "appid": api_key, "units": "metric"}
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(OW_URL, params=params)
        r.raise_for_status()
        j = r.json()
    # small curated summary
    main = j.get("weather", [{}])[0].get("main")
    desc = j.get("weather", [{}])[0].get("description")
    temp = j.get("main", {}).get("temp")
    feels = j.get("main", {}).get("feels_like")
    humidity = j.get("main", {}).get("humidity")
    wind = j.get("wind", {}).get("speed")
    return {
        "summary": main,
        "description": desc,
        "temp_c": temp,
        "feels_like_c": feels,
        "humidity_pct": humidity,
        "wind_mps": wind,
    }
