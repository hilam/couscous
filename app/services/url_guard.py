from urllib.parse import urlparse

_SAFE_SCHEMES = ("http", "https", "mailto")


def is_safe_launch_url(url: str | None) -> bool:
    if not url:
        return False
    return urlparse(url).scheme.casefold() in _SAFE_SCHEMES
