from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models import Item


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
    category: str = "general"
    severity: str = "normal"
    language: str | None = None
    summary_en: str | None = None
    summary_es: str | None = None
    neighborhood: str | None = None
    meta: dict = Field(default_factory=dict)
    lat: float | None = None
    lng: float | None = None


def item_to_out(item: Item) -> ItemOut:
    lat: float | None = None
    lng: float | None = None
    if item.geom is not None:
        try:
            from geoalchemy2.shape import to_shape

            shp = to_shape(item.geom)
            lat, lng = float(shp.y), float(shp.x)
        except Exception:
            pass
    return ItemOut(
        id=item.id,
        source_id=item.source_id,
        title=item.title,
        url=item.url,
        summary=item.summary,
        published_at=item.published_at,
        fetched_at=item.fetched_at,
        category=item.category,
        severity=item.severity,
        language=item.language,
        summary_en=item.summary_en,
        summary_es=item.summary_es,
        neighborhood=item.neighborhood,
        meta=dict(item.extras) if getattr(item, "extras", None) else {},
        lat=lat,
        lng=lng,
    )


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


class BreakingItemOut(BaseModel):
    id: int
    title: str
    url: str
    severity: str
    category: str
    published_at: datetime | None


class AlertsOut(BaseModel):
    high_alert: bool
    breaking: list[BreakingItemOut]
