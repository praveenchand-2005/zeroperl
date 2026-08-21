from __future__ import annotations

from sqlalchemy import UniqueConstraint

from .models import Case


TENANT_CASE_CONSTRAINT = "uq_cases_organization_case_number"


def normalize_case_constraints() -> None:
    table = Case.__table__
    case_number = table.c.case_number

    # Remove the legacy global UNIQUE(case_number) emitted by the prototype model.
    for constraint in list(table.constraints):
        if not isinstance(constraint, UniqueConstraint):
            continue
        columns = list(constraint.columns)
        if columns == [case_number]:
            table.constraints.remove(constraint)

    case_number.unique = False

    # Install the tenant-scoped uniqueness contract in SQLAlchemy metadata.
    if not any(
        isinstance(constraint, UniqueConstraint)
        and constraint.name == TENANT_CASE_CONSTRAINT
        for constraint in table.constraints
    ):
        table.append_constraint(
            UniqueConstraint(
                "organization_id",
                "case_number",
                name=TENANT_CASE_CONSTRAINT,
            )
        )


normalize_case_constraints()
