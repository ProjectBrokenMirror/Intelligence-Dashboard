from datetime import datetime, timezone

from geoalchemy2 import Geometry
from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    kind: Mapped[str] = mapped_column(String(32), nullable=False)  # rss | scraper | api
    feed_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    scraper_module: Mapped[str | None] = mapped_column(String(128), nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    items: Mapped[list["Item"]] = relationship("Item", back_populates="source")


class Item(Base):
    __tablename__ = "items"
    __table_args__ = (UniqueConstraint("url", name="uq_items_url"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source_id: Mapped[str] = mapped_column(String(64), ForeignKey("sources.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    category: Mapped[str] = mapped_column(String(64), nullable=False, default="general")
    severity: Mapped[str] = mapped_column(String(32), nullable=False, default="normal")
    language: Mapped[str | None] = mapped_column(String(8), nullable=True)
    summary_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary_es: Mapped[str | None] = mapped_column(Text, nullable=True)
    neighborhood: Mapped[str | None] = mapped_column(String(128), nullable=True)
    extras: Mapped[dict] = mapped_column(
        "meta",
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
    )
    geom: Mapped[object | None] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326, dimension=2),
        nullable=True,
    )

    source: Mapped["Source"] = relationship("Source", back_populates="items")
