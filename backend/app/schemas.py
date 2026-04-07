from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SourceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    kind: str
    feed_url: str | None
    scraper_module: str | None = None
    enabled: bool


class ItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source_id: str
    title: str
    url: str
    summary: str | None
    published_at: datetime | None
    fetched_at: datetime


class WeatherCurrentOut(BaseModel):
    temperature_c: float
    windspeed_kmh: float
    weathercode: int
    is_day: int


class WeatherOut(BaseModel):
    latitude: float
    longitude: float
    timezone: str
    current: WeatherCurrentOut


class IngestResultOut(BaseModel):
    sources_processed: int
    items_upserted: int
    errors: list[str]
