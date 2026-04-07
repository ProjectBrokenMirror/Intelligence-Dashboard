from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.ingest.runner import run_full_ingest
from app.schemas import IngestResultOut

router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.post("/run", response_model=IngestResultOut)
def trigger_ingest(db: Session = Depends(get_db)) -> IngestResultOut:
    return run_full_ingest(db)
