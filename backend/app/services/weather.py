import httpx

from app.config import settings
from app.schemas import WeatherCurrentOut, WeatherOut


async def fetch_pv_weather() -> WeatherOut:
    lat = settings.weather_latitude
    lon = settings.weather_longitude
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&current=temperature_2m,weather_code,wind_speed_10m,is_day"
        "&wind_speed_unit=kmh"
        "&timezone=America%2FMexico_City"
    )
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.get(url)
        r.raise_for_status()
        data = r.json()
    cur = data["current"]
    return WeatherOut(
        latitude=data["latitude"],
        longitude=data["longitude"],
        timezone=data.get("timezone") or "America/Mexico_City",
        current=WeatherCurrentOut(
            temperature_c=float(cur["temperature_2m"]),
            windspeed_kmh=float(cur["wind_speed_10m"]),
            weathercode=int(cur["weather_code"]),
            is_day=int(cur["is_day"]),
        ),
    )
