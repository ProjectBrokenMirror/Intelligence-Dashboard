from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.alerts.breaking import compute_alerts
from app.database import get_db
from app.schemas import AlertsOut

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=AlertsOut)
def get_alerts(
    db: Session = Depends(get_db),
    hours: int = Query(48, ge=1, le=168),
    limit: int = Query(20, ge=1, le=50),
) -> AlertsOut:
    return compute_alerts(db, hours=hours, limit=limit)
