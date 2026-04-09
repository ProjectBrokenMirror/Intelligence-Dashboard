from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, func, nulls_last
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Item
from app.schemas import ItemOut, item_to_out

router = APIRouter(prefix="/items", tags=["items"])


@router.get("", response_model=list[ItemOut])
def list_items(
    db: Session = Depends(get_db),
    source_id: str | None = Query(None),
    category: str | None = Query(None),
    severity: str | None = Query(None),
    neighborhood: str | None = Query(None, description="Filter by neighborhood slug"),
    placed_only: bool = Query(False, description="Only items with map coordinates"),
    since: datetime | None = Query(None, description="ISO datetime; filter published_at >= since"),
    limit: int = Query(100, ge=1, le=500),
) -> list[ItemOut]:
    q = db.query(Item)
    if source_id:
        q = q.filter(Item.source_id == source_id)
    if category:
        q = q.filter(Item.category == category)
    if severity:
        q = q.filter(Item.severity == severity)
    if neighborhood:
        q = q.filter(Item.neighborhood == neighborhood)
    if placed_only:
        q = q.filter(func.ST_X(Item.geom).isnot(None))
    if since:
        q = q.filter(Item.published_at.isnot(None)).filter(Item.published_at >= since)
    rows = (
        q.order_by(
            nulls_last(desc(Item.published_at)),
            desc(Item.fetched_at),
        )
        .limit(limit)
        .all()
    )
    return [item_to_out(r) for r in rows]
