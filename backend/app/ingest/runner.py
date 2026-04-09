import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ingest.classify import classify_headline, detect_language_hint
from app.ingest.config_loader import load_sources_config
from app.ingest.geocode import match_neighborhood
from app.ingest.rss import fetch_rss_items
from app.models import Item, Source
from app.schemas import IngestResultOut
from app.scrapers import SCRAPER_REGISTRY
from app.scrapers.base import NormalizedItem

logger = logging.getLogger(__name__)


def _upsert_source(db: Session, cfg) -> Source:
    row = db.get(Source, cfg.id)
    if row is None:
        row = Source(id=cfg.id)
        db.add(row)
    row.name = cfg.name
    row.kind = cfg.kind
    row.feed_url = cfg.feed_url
    row.scraper_module = cfg.scraper_module
    row.enabled = cfg.enabled
    return row


def _apply_monitor_fields(item: Item, title: str, summary: str | None) -> None:
    cat, sev = classify_headline(title)
    item.category = cat
    item.severity = sev
    item.language = detect_language_hint(title, summary)
    nh, geom = match_neighborhood(title, summary)
    item.neighborhood = nh
    item.geom = geom


def _upsert_item(db: Session, source_id: str, title: str, url: str, summary: str | None, published_at) -> bool:
    """Returns True if a new row was inserted."""
    existing = db.scalar(select(Item).where(Item.url == url))
    now = datetime.now(timezone.utc)
    if existing:
        existing.title = title
        existing.summary = summary
        existing.published_at = published_at
        existing.fetched_at = now
        _apply_monitor_fields(existing, title, summary)
        return False
    row = Item(
        source_id=source_id,
        title=title,
        url=url,
        summary=summary,
        published_at=published_at,
        fetched_at=now,
        extras={},
    )
    _apply_monitor_fields(row, title, summary)
    db.add(row)
    return True


def run_full_ingest(db: Session) -> IngestResultOut:
    file_cfg = load_sources_config()
    errors: list[str] = []
    upserted = 0
    processed = 0

    for cfg in file_cfg.sources:
        _upsert_source(db, cfg)
    db.commit()

    for cfg in file_cfg.sources:
        if not cfg.enabled:
            continue
        processed += 1
        try:
            items: list[NormalizedItem] = []
            if cfg.kind == "rss":
                if not cfg.feed_url:
                    errors.append(f"{cfg.id}: rss source missing feed_url")
                    continue
                items = fetch_rss_items(cfg.feed_url)
            elif cfg.kind == "scraper":
                mod = cfg.scraper_module or ""
                cls = SCRAPER_REGISTRY.get(mod)
                if not cls:
                    errors.append(f"{cfg.id}: unknown scraper_module {mod!r}")
                    continue
                scraper = cls(cfg.id)
                items = scraper.fetch()
            else:
                errors.append(f"{cfg.id}: unsupported kind {cfg.kind!r}")
                continue

            for it in items:
                inserted = _upsert_item(db, cfg.id, it.title, it.url, it.summary, it.published_at)
                if inserted:
                    upserted += 1
            db.commit()
        except Exception as e:  # noqa: BLE001
            db.rollback()
            logger.exception("Ingest failed for %s", cfg.id)
            errors.append(f"{cfg.id}: {e}")

    return IngestResultOut(sources_processed=processed, items_upserted=upserted, errors=errors)
