"""Breaking / high-alert signals from recent items (keyword + severity heuristics)."""

from datetime import datetime, timedelta, timezone

from sqlalchemy import desc, or_, select
from sqlalchemy.orm import Session

from app.models import Item
from app.schemas import AlertsOut, BreakingItemOut

_HIGH = ("high", "elevated")
_BREAKING_CATEGORIES = ("safety", "infrastructure")


def compute_alerts(db: Session, hours: int = 48, limit: int = 20) -> AlertsOut:
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    q = (
        select(Item)
        .where(Item.published_at.isnot(None))
        .where(Item.published_at >= since)
        .where(
            or_(
                Item.severity.in_(_HIGH),
                Item.category.in_(_BREAKING_CATEGORIES),
            )
        )
        .order_by(desc(Item.published_at))
        .limit(limit)
    )
    rows = list(db.scalars(q).all())
    high_alert = any(i.severity == "high" for i in rows)
    breaking = [
        BreakingItemOut(
            id=i.id,
            title=i.title,
            url=i.url,
            severity=i.severity,
            category=i.category,
            published_at=i.published_at,
        )
        for i in rows
    ]
    return AlertsOut(high_alert=high_alert, breaking=breaking)
