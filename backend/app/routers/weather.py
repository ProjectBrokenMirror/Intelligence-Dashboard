from fastapi import APIRouter

from app.services.weather import fetch_pv_weather
from app.schemas import WeatherOut

router = APIRouter(prefix="/weather", tags=["weather"])


@router.get("", response_model=WeatherOut)
async def get_weather() -> WeatherOut:
    return await fetch_pv_weather()
