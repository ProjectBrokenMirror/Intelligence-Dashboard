from app.scrapers.base import NormalizedItem, ScraperBase


class StubScraper(ScraperBase):
    """Template scraper: returns no items. Copy this file, implement fetch(), add to SCRAPER_REGISTRY."""

    def fetch(self) -> list[NormalizedItem]:
        return []
