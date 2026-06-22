from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import UTC, datetime
from time import mktime

import feedparser
import httpx


@dataclass
class ParsedEntry:
    id: str
    link: str
    title: str | None = None
    summary: str | None = None
    content: str | None = None
    author: str | None = None
    published: datetime | None = None


@dataclass
class FeedFetchResult:
    title: str | None = None
    link: str | None = None
    entries: list[ParsedEntry] | None = None
    error: str | None = None


class FeedFetcher:
    async def fetch(self, url: str) -> FeedFetchResult:
        raise NotImplementedError


class HttpFeedFetcher(FeedFetcher):
    async def fetch(self, url: str) -> FeedFetchResult:
        try:
            response = await asyncio.to_thread(
                httpx.get, url, timeout=30, follow_redirects=True
            )
            response.raise_for_status()

            parsed = await asyncio.to_thread(feedparser.parse, response.text)

            if parsed.bozo and not parsed.entries:
                return FeedFetchResult(error="Failed to parse feed")

            title = parsed.feed.get("title")
            link = parsed.feed.get("link")
            entries = [
                e for e in (_parse_entry(e) for e in parsed.entries) if e is not None
            ]

            return FeedFetchResult(title=title, link=link, entries=entries)

        except Exception as e:
            return FeedFetchResult(error=str(e))


def _parse_entry(entry_data) -> ParsedEntry | None:
    try:
        entry_id = entry_data.get("id") or entry_data.get("link")
        if not entry_id:
            return None

        published = None
        if hasattr(entry_data, "published_parsed") and entry_data.published_parsed:
            published = datetime.fromtimestamp(
                mktime(entry_data.published_parsed), tz=UTC
            ).replace(tzinfo=None)

        content = None
        if entry_data.get("content"):
            content = entry_data["content"][0].get("value")

        return ParsedEntry(
            id=entry_id,
            link=entry_data.get("link"),
            title=entry_data.get("title"),
            summary=entry_data.get("summary"),
            content=content,
            author=entry_data.get("author"),
            published=published,
        )

    except Exception:
        return None
