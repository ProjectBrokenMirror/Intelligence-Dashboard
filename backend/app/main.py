import logging
from contextlib import asynccontextmanager

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import SessionLocal
from app.enrichment.runner import run_enrichment_batch
from app.ingest.runner import run_full_ingest
from app.routers import alerts, enrichment_route, ingest, items, sources, status, weather

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def _scheduled_ingest() -> None:
    db = SessionLocal()
    try:
        result = run_full_ingest(db)
        if result.errors:
            logger.warning("Ingest completed with errors: %s", result.errors)
        else:
            logger.info(
                "Ingest ok: processed=%s upserted=%s",
                result.sources_processed,
                result.items_upserted,
            )
    finally:
        db.close()


def _scheduled_enrichment() -> None:
    db = SessionLocal()
    try:
        n = run_enrichment_batch(db, settings.enrichment_batch_size)
        if n:
            logger.info("Enrichment completed for %s items", n)
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    _scheduled_ingest()
    scheduler.add_job(
        _scheduled_ingest,
        "interval",
        minutes=settings.ingest_interval_minutes,
        id="rss_ingest",
        replace_existing=True,
    )
    scheduler.add_job(
        _scheduled_enrichment,
        "interval",
        minutes=settings.enrichment_interval_minutes,
        id="llm_enrichment",
        replace_existing=True,
    )
    scheduler.start()
    yield
    scheduler.shutdown(wait=False)


app = FastAPI(title="Puerto Vallarta Intelligence API", lifespan=lifespan)

origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sources.router)
app.include_router(items.router)
app.include_router(weather.router)
app.include_router(status.router)
app.include_router(ingest.router)
app.include_router(alerts.router)
app.include_router(enrichment_route.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
