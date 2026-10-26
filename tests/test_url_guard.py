from app.services.url_guard import is_safe_launch_url


def test_javascript_scheme_rejected():
    assert is_safe_launch_url("javascript:alert(1)") is False


def test_https_case_insensitive_accepted():
    assert is_safe_launch_url("HTTPS://ex.com") is True


def test_http_accepted():
    assert is_safe_launch_url("http://ex.com") is True


def test_https_accepted():
    assert is_safe_launch_url("https://ex.com/rss") is True


def test_mailto_accepted():
    assert is_safe_launch_url("mailto:a@b.c") is True


def test_none_rejected():
    assert is_safe_launch_url(None) is False


def test_empty_rejected():
    assert is_safe_launch_url("") is False


def test_data_scheme_rejected():
    assert is_safe_launch_url("data:text/html,<script>alert(1)</script>") is False


def test_ftp_scheme_rejected():
    assert is_safe_launch_url("ftp://ex.com") is False


def test_schemeless_rejected():
    assert is_safe_launch_url("ex.com/rss") is False
