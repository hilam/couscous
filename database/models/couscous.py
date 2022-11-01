from datetime import datetime
from typing import Optional, List

from sqlmodel import Field, SQLModel, Relationship


class User(SQLModel, table=True):
    __tablename__ = 'users'

    id: Optional[int] = Field(primary_key=True, default=None)
    name: str = Field(primary_key=True)
    password: str


class Feed(SQLModel, table=True):
    __tablename__ = 'feeds'

    url: str = Field(primary_key=True)
    title: Optional[str]
    link: Optional[str]
    updated: Optional[datetime]
    author: Optional[str]
    subtitle: Optional[str]
    version: Optional[str]
    user_title: Optional[str]
    http_etag: Optional[str]
    http_last_modified: Optional[str]
    data_hash: Optional[str]
    stale: int = Field(nullable=False, default=0)
    updates_enabled: int = Field(nullable=False, default=1)
    last_updated: Optional[datetime]
    added: datetime = Field(nullable=False, default=datetime.now())
    last_exception: Optional[str]

    entries: List["Entry"] = Relationship(back_populates="url_feed")


class Entry(SQLModel, table=True):
    __tablename__ = 'entries'

    id: Optional[int] = Field(primary_key=True, default=None)
    feed: str = Field(primary_key=True, foreign_key='feeds.url')
    title: Optional[str]
    link: Optional[str]
    updated: Optional[datetime]
    author: Optional[str]
    published: Optional[datetime]
    summary: Optional[str]
    content: Optional[str]
    enclosures: Optional[str]
    original_feed: Optional[str]
    data_hash: Optional[str]
    data_hash_changed: Optional[int]
    read: Optional[int] = Field(default=0, nullable=False)
    read_modified: Optional[datetime]
    important: Optional[int] = Field(default=0, nullable=False)
    important_modified: Optional[datetime]
    added_by: str
    last_updated: datetime
    first_updated: datetime
    first_updated_epoch: datetime
    feed_order: int

    url_feed: Feed = Relationship(back_populates='entries')


class FeedMetadata(SQLModel, table=True):
    __tablename__ = 'feed_metadata'

    feed: str = Field(primary_key=True, foreign_key='feeds.url')
    key: str = Field(primary_key=True)
    value: str


class FeedTag(SQLModel, table=True):
    __tablename__ = 'feed_tags'

    feed: str = Field(primary_key=True, foreign_key='feeds.url')
    tag: str = Field(primary_key=True)
