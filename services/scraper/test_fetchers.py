import pytest

from fetchers import is_allowed_url


def test_allowed_domain_exact():
    assert is_allowed_url("https://example.gov/page", ["example.gov"])


def test_allowed_domain_subdomain():
    assert is_allowed_url("https://records.example.gov/page", ["example.gov"])


def test_disallowed_domain():
    assert not is_allowed_url("https://example.com/page", ["example.gov"])


def test_non_http_scheme_rejected():
    assert not is_allowed_url("file:///etc/passwd", ["example.gov"])


@pytest.mark.parametrize("url", ["http://example.gov", "https://example.gov"])
def test_supported_schemes(url):
    assert is_allowed_url(url, ["example.gov"])
