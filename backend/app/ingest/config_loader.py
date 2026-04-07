from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

from app.config import settings


class SourceConfig(BaseModel):
    id: str
    name: str
    kind: str
    feed_url: str | None = None
    scraper_module: str | None = None
    enabled: bool = True


class SourcesFile(BaseModel):
    sources: list[SourceConfig] = Field(default_factory=list)


def load_sources_config() -> SourcesFile:
    path = Path(settings.sources_config_path)
    if not path.is_file():
        return SourcesFile(sources=[])
    raw: dict[str, Any] = yaml.safe_load(path.read_text()) or {}
    return SourcesFile.model_validate(raw)
