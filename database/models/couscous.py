import datetime as _dt

from sqlmodel import Field, Relationship, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(primary_key=True, default=None)
    name: str = Field(unique=True, nullable=False)
    password: str


class Feed(SQLModel, table=True):
    __tablename__ = "feeds"

    url: str = Field(primary_key=True)
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
    added: _dt.datetime = Field(
        nullable=False,
        default_factory=lambda: _dt.datetime.now(_dt.UTC).replace(tzinfo=None),
    )
    last_exception: str | None

    entries: list["Entry"] = Relationship(back_populates="url_feed")


class Entry(SQLModel, table=True):
    __tablename__ = "entries"

    id: int | None = Field(primary_key=True, default=None)
    feed: str = Field(foreign_key="feeds.url")
    title: str | None
    link: str | None
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

    url_feed: Feed = Relationship(back_populates="entries")


class FeedMetadata(SQLModel, table=True):
    __tablename__ = "feed_metadata"

    feed: str = Field(primary_key=True, foreign_key="feeds.url")
    key: str = Field(primary_key=True)
    value: str


class FeedTag(SQLModel, table=True):
    __tablename__ = "feed_tags"

    feed: str = Field(primary_key=True, foreign_key="feeds.url")
    tag: str = Field(primary_key=True)
