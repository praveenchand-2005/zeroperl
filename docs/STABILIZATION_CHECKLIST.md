# Stabilization Checklist

## Verified statically

- V1/V2/V3/V4 API modules are present on the feature branch.
- V4 router is registered in the FastAPI application.
- GitHub Actions workflow covers web, API, scraper and worker services.
- Scraper CI installs Chromium for Playwright tests.
- Python service tests receive the repository root through `PYTHONPATH`.
- Public/authorized acquisition remains policy-scoped.

## Known validation limitation

GitHub is currently returning no Actions workflow run/status for the feature branch. The branch is therefore not CI-verified yet.

A clean-network checkout could not be performed from the current execution environment because outbound DNS access to github.com is unavailable.

## Schema hardening item

The `cases.case_number` model currently has a global uniqueness constraint while the application itself performs organization-scoped duplicate checks. For true multi-tenant isolation, the database constraint should be changed to a composite unique constraint on `(organization_id, case_number)` and applied through a real migration. This change must be made against the current file SHA to avoid overwriting concurrent branch updates.

## Production gate

Do not merge PR #1 or label the platform production-ready until:

1. GitHub Actions runs successfully for web/API/scraper/worker jobs.
2. Database migrations are versioned and exercised against a clean PostgreSQL instance.
3. Cross-tenant authorization tests pass.
4. V2 scraper integration tests pass with policy enforcement.
5. V3 evidence/graph/review flows pass integration tests.
6. V4 profile/employment/company routes pass integration tests.
