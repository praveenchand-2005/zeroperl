def test_application_imports_and_exposes_expected_versions() -> None:
    from .main import app

    routes = {route.path for route in app.routes}
    assert "/health" in routes
    assert any(path.startswith("/api/v3/") for path in routes)
    assert any(path.startswith("/api/v4/") for path in routes)
