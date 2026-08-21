from pathlib import Path

from sqlalchemy import UniqueConstraint

from .main import app
from .models import Case


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


def test_case_metadata_is_tenant_scoped() -> None:
    constraints = [
        constraint
        for constraint in Case.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    ]
    names = {constraint.name for constraint in constraints}
    assert "uq_cases_organization_case_number" in names
    assert all(
        list(constraint.columns) != [Case.__table__.c.case_number]
        for constraint in constraints
        if constraint.name != "uq_cases_organization_case_number"
    )
    tenant_constraint = next(
        constraint
        for constraint in constraints
        if constraint.name == "uq_cases_organization_case_number"
    )
    assert [column.name for column in tenant_constraint.columns] == [
        "organization_id",
        "case_number",
    ]
