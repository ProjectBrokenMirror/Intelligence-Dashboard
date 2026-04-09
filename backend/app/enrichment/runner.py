import logging
from datetime import datetime, timezone

from sqlalchemy import select, text
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from app.enrichment.llm_client import enrich_text
from app.ingest.geocode import match_neighborhood
from app.models import Item

logger = logging.getLogger(__name__)


def run_enrichment_batch(db: Session, limit: int) -> int:
    """Process up to `limit` items; returns count successfully enriched."""
    if not _llm_configured():
        return 0

    q = (
        select(Item)
        .where(text("(items.meta->>'enriched') IS NULL"))
        .order_by(Item.fetched_at.desc())
        .limit(limit)
    )
    rows = list(db.scalars(q).all())
    done = 0
    for item in rows:
        try:
            data = enrich_text(item.title, item.summary)
            if not data:
                continue
            if se := data.get("summary_en"):
                item.summary_en = str(se)[:2000]
            if se := data.get("summary_es"):
                item.summary_es = str(se)[:2000]
            cat = data.get("category")
            if cat in ("general", "safety", "infrastructure", "event"):
                item.category = cat
            hint = (data.get("neighborhood_hint") or "").strip()
            if hint:
                nh, geom = match_neighborhood(hint, None)
                if nh and geom:
                    item.neighborhood = nh
                    item.geom = geom
            ex = dict(item.extras or {})
            ex["enriched"] = True
            ex["enriched_at"] = datetime.now(timezone.utc).isoformat()
            item.extras = ex
            flag_modified(item, "extras")
            db.commit()
            done += 1
        except Exception as e:  # noqa: BLE001
            db.rollback()
            logger.warning("Enrichment skip item %s: %s", item.id, e)
    return done


def _llm_configured() -> bool:
    from app.config import settings

    return bool(settings.ollama_base_url or settings.groq_api_key)
