from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, nulls_last
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Item
from app.schemas import ItemOut

router = APIRouter(prefix="/items", tags=["items"])


@router.get("", response_model=list[ItemOut])
def list_items(
    db: Session = Depends(get_db),
    source_id: str | None = Query(None),
    since: datetime | None = Query(None, description="ISO datetime; filter published_at >= since"),
    limit: int = Query(100, ge=1, le=500),
) -> list[Item]:
    q = db.query(Item)
    if source_id:
        q = q.filter(Item.source_id == source_id)
    if since:
        q = q.filter(Item.published_at.isnot(None)).filter(Item.published_at >= since)
    return q.order_by(
        nulls_last(desc(Item.published_at)),
        desc(Item.fetched_at),
    ).limit(limit).all()
