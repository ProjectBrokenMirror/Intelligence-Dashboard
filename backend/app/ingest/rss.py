from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import feedparser

from app.scrapers.base import NormalizedItem


def _parse_published(entry: object) -> datetime | None:
    published_parsed = getattr(entry, "published_parsed", None)
    if published_parsed:
        return datetime(*published_parsed[:6], tzinfo=timezone.utc)
    updated_parsed = getattr(entry, "updated_parsed", None)
    if updated_parsed:
        return datetime(*updated_parsed[:6], tzinfo=timezone.utc)
    published = getattr(entry, "published", None)
    if published:
        try:
            dt = parsedate_to_datetime(published)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except (TypeError, ValueError):
            pass
    return None


def fetch_rss_items(feed_url: str) -> list[NormalizedItem]:
    parsed = feedparser.parse(feed_url)
    out: list[NormalizedItem] = []
    for entry in parsed.entries:
        link = getattr(entry, "link", None) or None
        if not link:
            links = getattr(entry, "links", None) or []
            if links:
                link = links[0].get("href") if isinstance(links[0], dict) else getattr(links[0], "href", None)
        if not link:
            continue
        title = entry.get("title") or "(no title)"
        summary = entry.get("summary") or entry.get("description")
        if summary and len(summary) > 4000:
            summary = summary[:3997] + "..."
        out.append(
            NormalizedItem(
                title=title.strip(),
                url=link.strip(),
                summary=summary,
                published_at=_parse_published(entry),
            )
        )
    return out
