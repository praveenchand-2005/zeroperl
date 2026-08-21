from pathlib import Path

from .main import app


def test_api_exposes_v1_v2_v3_v4_surfaces() -> None:
    paths = {route.path for route in app.routes}
    assert "/health" in paths
    assert "/api/v1/auth/register" in paths
    assert "/api/v1/cases" in paths
    assert "/api/v2/sources" in paths
    assert "/api/v3/investigations" in paths
    assert "/api/v4/cases/{case_id}/profiles" in paths
    assert "/api/v4/cases/{case_id}/companies" in paths
    assert "/api/v4/cases/{case_id}/employment" in paths


def test_tenant_case_number_migration_contract() -> None:
    migration = Path(__file__).parents[1] / "alembic" / "versions" / "0001_tenant_case_number.py"
    source = migration.read_text(encoding="utf-8")
    assert "uq_cases_organization_case_number" in source
    assert "UNIQUE (organization_id, case_number)" in source
