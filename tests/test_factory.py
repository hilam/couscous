from datetime import datetime, timezone

from app.services.user_service import register
from database.models.couscous import Entry, Feed

RSS_XML_TEMPLATE = '''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/">
<channel>
<title>{title}</title>
<link>{link}</link>
{items}
</channel>
</rss>'''

RSS_ITEM = '''<item>
<title>{title}</title>
<link>{link}</link>
<guid>{guid}</guid>
<description>{description}</description>
<author>{author}</author>
<pubDate>{pub_date}</pubDate>
{content_encoded}
</item>'''

ATOM_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
<title>{title}</title>
<link href="{link}"/>
{entries}
</feed>'''

ATOM_ENTRY = '''<entry>
<title>{title}</title>
<link href="{link}"/>
<id>{id}</id>
<summary>{summary}</summary>
<author><name>{author}</name></author>
<published>{published}</published>
</entry>'''


def rss_feed_xml(title="Test RSS Feed", link="https://example.com", num_entries=3):
    items = []
    for i in range(1, num_entries + 1):
        content = f"<content:encoded><![CDATA[<p>Content {i}</p>]]></content:encoded>"
        items.append(RSS_ITEM.format(
            title=f"Article {i}",
            link=f"https://example.com/article{i}",
            guid=f"https://example.com/article{i}",
            description=f"Summary {i}",
            author=f"Author {i}",
            pub_date=f"Mon, 0{i} Jan 2024 00:00:00 GMT",
            content_encoded=content,
        ))
    return RSS_XML_TEMPLATE.format(title=title, link=link, items="".join(items))


def rss_feed_xml_no_content(num_entries=3):
    items = []
    for i in range(1, num_entries + 1):
        items.append(RSS_ITEM.format(
            title=f"Article {i}",
            link=f"https://example.com/article{i}",
            guid=f"https://example.com/article{i}",
            description=f"Summary {i}",
            author=f"Author {i}",
            pub_date=f"Mon, 0{i} Jan 2024 00:00:00 GMT",
            content_encoded="",
        ))
    return RSS_XML_TEMPLATE.format(title="Test Feed", link="https://example.com", items="".join(items))


def atom_feed_xml(title="Atom Feed", link="https://example.com/atom"):
    entries = ATOM_ENTRY.format(
        title="Atom Article 1",
        link="https://example.com/atom1",
        id="https://example.com/atom1",
        summary="Atom Summary 1",
        author="Atom Author",
        published="2024-01-01T00:00:00Z",
    )
    return ATOM_XML.format(title=title, link=link, entries=entries)


def rss_xml_missing_items(num_valid=2, num_missing=1):
    items = []
    for i in range(1, num_valid + 1):
        items.append(RSS_ITEM.format(
            title=f"Valid Article {i}",
            link=f"https://example.com/valid{i}",
            guid=f"https://example.com/valid{i}",
            description=f"Valid Summary {i}",
            author=f"Author {i}",
            pub_date=f"Mon, 0{i} Jan 2024 00:00:00 GMT",
            content_encoded="",
        ))
    for i in range(1, num_missing + 1):
        items.append(f"<item>\n<title>Article Missing Link</title>\n</item>")
    return RSS_XML_TEMPLATE.format(title="Test Feed", link="https://example.com", items="".join(items))


async def make_user(session, name="testuser", password="pass"):
    return await register(session, name, password)


async def make_feed(session, url="https://example.com/rss", user_id=1):
    feed = Feed(url=url, user_id=user_id)
    session.add(feed)
    await session.commit()
    return feed


async def make_entry(session, feed_url="https://example.com/rss", user_id=1, **overrides):
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    kwargs = dict(
        feed=feed_url,
        user_id=user_id,
        title="Test Article",
        link="https://example.com/article1",
        summary="Test summary",
        published=now,
        last_updated=now,
        first_updated=now,
        first_updated_epoch=now,
        added_by="test",
        feed_order=0,
    )
    kwargs.update(overrides)
    entry = Entry(**kwargs)
    session.add(entry)
    await session.commit()
    return entry


async def create_feed_and_entry(session, user_id, url="https://example.com/rss", **overrides):
    """Create a feed + entry in one call. Returns (feed, entry)."""
    feed = await make_feed(session, url, user_id)
    entry = await make_entry(session, feed_url=url, user_id=user_id, **overrides)
    return feed, entry
