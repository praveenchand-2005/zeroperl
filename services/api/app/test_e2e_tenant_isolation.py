from __future__ import annotations

from uuid import UUID

import pytest
from httpx import ASGITransport, AsyncClient

from .main import app


async def register(client: AsyncClient, slug: str, email: str) -> str:
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "organization_name": slug.title(),
            "organization_slug": slug,
            "full_name": "Synthetic Test User",
            "email": email,
            "password": "Synthetic-Test-Password-123!",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_cross_tenant_case_isolation_and_case_number_scope() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        token_a = await register(client, "tenant-a", "tenant-a@example.test")
        token_b = await register(client, "tenant-b", "tenant-b@example.test")

        case_payload = {
            "case_number": "CASE-001",
            "borrower_name": "Synthetic Borrower A",
            "known_phone": "+10000000001",
        }
        created_a = await client.post(
            "/api/v1/cases",
            headers={"Authorization": f"Bearer {token_a}"},
            json=case_payload,
        )
        assert created_a.status_code == 201, created_a.text
        case_a = created_a.json()

        created_b = await client.post(
            "/api/v1/cases",
            headers={"Authorization": f"Bearer {token_b}"},
            json={**case_payload, "borrower_name": "Synthetic Borrower B"},
        )
        assert created_b.status_code == 201, created_b.text
        case_b = created_b.json()
        assert case_a["case_number"] == case_b["case_number"] == "CASE-001"
        assert case_a["id"] != case_b["id"]

        duplicate_a = await client.post(
            "/api/v1/cases",
            headers={"Authorization": f"Bearer {token_a}"},
            json=case_payload,
        )
        assert duplicate_a.status_code == 409, duplicate_a.text

        cases_as_a = await client.get(
            "/api/v1/cases",
            headers={"Authorization": f"Bearer {token_a}"},
        )
        assert cases_as_a.status_code == 200
        assert {row["id"] for row in cases_as_a.json()} == {case_a["id"]}

        cases_as_b = await client.get(
            "/api/v1/cases",
            headers={"Authorization": f"Bearer {token_b}"},
        )
        assert cases_as_b.status_code == 200
        assert {row["id"] for row in cases_as_b.json()} == {case_b["id"]}

        a_profiles_seen_by_b = await client.get(
            f"/api/v4/cases/{case_a['id']}/profiles",
            headers={"Authorization": f"Bearer {token_b}"},
        )
        assert a_profiles_seen_by_b.status_code == 404

        assert UUID(case_a["id"])
        assert UUID(case_b["id"])
