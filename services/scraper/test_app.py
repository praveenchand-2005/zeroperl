from app import allowed_url, SourcePolicy


def test_allowed_url_uses_source_policy() -> None:
    policy = SourcePolicy(source_id="example", allowed_domains=["example.com"])
    assert allowed_url("https://example.com/page", policy)
    assert allowed_url("https://sub.example.com/page", policy)
    assert not allowed_url("https://not-example.com/page", policy)
    assert not allowed_url("file:///tmp/test.html", policy)
