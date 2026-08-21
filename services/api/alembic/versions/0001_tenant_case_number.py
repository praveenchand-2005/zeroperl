"""Make case numbers unique per organization rather than globally.

Revision ID: 0001_tenant_case_number
Revises:
"""
from alembic import op

revision = "0001_tenant_case_number"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE cases DROP CONSTRAINT IF EXISTS cases_case_number_key")
    op.execute(
        "ALTER TABLE cases ADD CONSTRAINT uq_cases_organization_case_number "
        "UNIQUE (organization_id, case_number)"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE cases DROP CONSTRAINT IF EXISTS uq_cases_organization_case_number")
    op.execute("ALTER TABLE cases ADD CONSTRAINT cases_case_number_key UNIQUE (case_number)")
