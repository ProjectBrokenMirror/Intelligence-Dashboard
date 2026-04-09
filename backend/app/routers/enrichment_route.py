from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.enrichment.runner import _llm_configured, run_enrichment_batch
from pydantic import BaseModel


class EnrichmentRunOut(BaseModel):
    processed: int
    llm_configured: bool


router = APIRouter(prefix="/enrichment", tags=["enrichment"])


@router.post("/run", response_model=EnrichmentRunOut)
def trigger_enrichment(db: Session = Depends(get_db)) -> EnrichmentRunOut:
    n = run_enrichment_batch(db, settings.enrichment_batch_size)
    return EnrichmentRunOut(processed=n, llm_configured=_llm_configured())
