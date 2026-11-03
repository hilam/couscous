import datetime as _dt

from sqlalchemy import Index, desc, text
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(primary_key=True, default=None)
    name: str = Field(unique=True, nullable=False)
    password: str | None
    oauth_provider: str | None = Field(default=None, nullable=True)
    oauth_id: str | None = Field(default=None, nullable=True)
    theme_mode: str | None = Field(default="light", nullable=True)
    font_scale: float | None = Field(default=1.0, nullable=True)
    auto_cleanup_days: int | None = Field(default=None, nullable=True)


class Feed(SQLModel, table=True):
    __tablename__ = "feeds"
    __table_args__ = (Index("idx_feeds_user_id", "user_id"),)

    url: str = Field(primary_key=True)
    user_id: int = Field(foreign_key="users.id", primary_key=True, nullable=False)
    title: str | None
    link: str | None
    updated: _dt.datetime | None
    author: str | None
    subtitle: str | None
    version: str | None
    user_title: str | None
    http_etag: str | None
    http_last_modified: str | None
    data_hash: str | None
    stale: int = Field(nullable=False, default=0)
    updates_enabled: int = Field(nullable=False, default=1)
    last_updated: _dt.datetime | None
    category_id: int | None = Field(
        foreign_key="categories.id", nullable=True, default=None
    )
    added: _dt.datetime = Field(
        nullable=False,
        default_factory=lambda: _dt.datetime.now(_dt.UTC).replace(tzinfo=None),
    )
    last_exception: str | None


class Entry(SQLModel, table=True):
    __tablename__ = "entries"
    __table_args__ = (
        Index("idx_entries_feed_user_published", "feed", "user_id", desc("published")),
        Index("idx_entries_user_published", "user_id", desc("published")),
        Index("idx_entries_user_read", "user_id", "read"),
        Index("idx_entries_link_user", "link", "user_id"),
        Index(
            "uq_entries_feed_user_external_id",
            "feed",
            "user_id",
            "external_id",
            unique=True,
            postgresql_where=text("external_id IS NOT NULL"),
        ),
    )

    id: int | None = Field(primary_key=True, default=None)
    feed: str
    user_id: int = Field(foreign_key="users.id", nullable=False)
    title: str | None
    link: str | None
    external_id: str | None = Field(default=None, nullable=True)
    updated: _dt.datetime | None
    author: str | None
    published: _dt.datetime | None
    summary: str | None
    content: str | None
    enclosures: str | None
    original_feed: str | None
    data_hash: str | None
    data_hash_changed: int | None
    read: int | None = Field(default=0, nullable=False)
    read_modified: _dt.datetime | None
    important: int | None = Field(default=0, nullable=False)
    important_modified: _dt.datetime | None
    added_by: str
    last_updated: _dt.datetime
    first_updated: _dt.datetime
    first_updated_epoch: _dt.datetime
    feed_order: int


class Category(SQLModel, table=True):
    __tablename__ = "categories"
    __table_args__ = (Index("idx_categories_user_id", "user_id"),)

    id: int | None = Field(primary_key=True, default=None)
    user_id: int = Field(foreign_key="users.id", nullable=False)
    name: str = Field(nullable=False)
    parent_id: int | None = Field(
        foreign_key="categories.id", nullable=True, default=None
    )


class EntryTag(SQLModel, table=True):
    __tablename__ = "entry_tags"

    entry_id: int = Field(
        primary_key=True, foreign_key="entries.id", ondelete="CASCADE"
    )
    tag: str = Field(primary_key=True)
    user_id: int = Field(foreign_key="users.id", nullable=False)
