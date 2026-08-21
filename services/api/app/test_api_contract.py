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


def test_case_number_is_tenant_scoped() -> None:
    constraint_names = {constraint.name for constraint in Case.__table__.constraints}
    assert "uq_cases_organization_case_number" in constraint_names
