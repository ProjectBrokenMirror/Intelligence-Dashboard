from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Item, Source
from pydantic import BaseModel


class StatusOut(BaseModel):
    source_count: int
    item_count: int
    last_fetched_at: datetime | None


router = APIRouter(prefix="/status", tags=["status"])


@router.get("", response_model=StatusOut)
def get_status(db: Session = Depends(get_db)) -> StatusOut:
    source_count = db.scalar(select(func.count()).select_from(Source)) or 0
    item_count = db.scalar(select(func.count()).select_from(Item)) or 0
    last_fetched_at = db.scalar(select(func.max(Item.fetched_at)))
    return StatusOut(
        source_count=int(source_count),
        item_count=int(item_count),
        last_fetched_at=last_fetched_at,
    )
