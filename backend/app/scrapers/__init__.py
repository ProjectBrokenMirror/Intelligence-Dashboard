from app.scrapers.base import NormalizedItem, ScraperBase
from app.scrapers.stub import StubScraper

SCRAPER_REGISTRY: dict[str, type[ScraperBase]] = {
    "stub": StubScraper,
}

__all__ = ["NormalizedItem", "ScraperBase", "SCRAPER_REGISTRY", "StubScraper"]
