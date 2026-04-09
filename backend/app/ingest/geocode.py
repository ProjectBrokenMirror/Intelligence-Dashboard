from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from geoalchemy2.elements import WKTElement


@lru_cache
def _load_neighborhoods() -> list[dict[str, Any]]:
    path = Path(__file__).resolve().parent.parent.parent / "config" / "neighborhoods.yaml"
    if not path.is_file():
        return []
    data = yaml.safe_load(path.read_text()) or {}
    return list(data.get("neighborhoods") or [])


def match_neighborhood(title: str, summary: str | None) -> tuple[str | None, WKTElement | None]:
    """Return (slug, WKT point) if any neighborhood key matches."""
    blob = f" {title} {summary or ''} ".lower()
    for n in _load_neighborhoods():
        for key in n.get("keys") or []:
            if key.lower() in blob:
                lat, lng = float(n["lat"]), float(n["lng"])
                slug = str(n.get("slug") or key)
                wkt = WKTElement(f"POINT({lng} {lat})", srid=4326)
                return slug, wkt
    return None, None


def set_item_point_sql(lat: float, lng: float) -> WKTElement:
    return WKTElement(f"POINT({lng} {lat})", srid=4326)
