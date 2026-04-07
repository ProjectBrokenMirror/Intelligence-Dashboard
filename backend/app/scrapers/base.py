from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass
class NormalizedItem:
    title: str
    url: str
    summary: str | None = None
    published_at: datetime | None = None


class ScraperBase(ABC):
    """One module per news site; implement fetch() and register in SCRAPER_REGISTRY."""

    def __init__(self, source_id: str) -> None:
        self.source_id = source_id

    @abstractmethod
    def fetch(self) -> list[NormalizedItem]:
        raise NotImplementedError
