from datetime import datetime, timezone
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .auth import create_access_token, get_current_user, hash_password, require_roles, verify_password
from .db import engine, get_db
from .models import AuditLog, Base, Case, Organization, User

app = FastAPI(title="Recovery Intelligence API", version="0.2.0")


class HealthResponse(BaseModel):
    status: str
    version: str


class RegisterRequest(BaseModel):
    organization_name: str = Field(min_length=2, max_length=200)
    organization_slug: str = Field(pattern=r"^[a-z0-9-]{2,80}$")
    full_name: str = Field(min_length=2, max_length=200)
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class CaseCreate(BaseModel):
    case_number: str = Field(min_length=2, max_length=80)
    borrower_name: str = Field(min_length=2, max_length=200)
    status: str = "INVESTIGATION"
    priority: str = "MEDIUM"
    known_phone: str | None = None
    known_email: EmailStr | None = None
    known_address: str | None = None


class CaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    case_number: str
    borrower_name: str
    status: str
    priority: str
    known_phone: str | None
    known_email: str | None
    known_address: str | None


class InvestigationRequest(BaseModel):
    case_id: str
    depth: str = "STANDARD"
    fields: list[str] = []


@app.on_event("startup")
async def startup() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", version="0.2.0")


@app.post("/api/v1/auth/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    existing = await db.scalar(select(User).where(User.email == payload.email))
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    org = Organization(name=payload.organization_name, slug=payload.organization_slug)
    db.add(org)
    await db.flush()

    user = User(
        organization_id=org.id,
        email=payload.email,
        full_name=payload.full_name,
        password_hash=hash_password(payload.password),
        role="organization_admin",
    )
    db.add(user)
    await db.flush()

    db.add(AuditLog(organization_id=org.id, user_id=user.id, action="REGISTER"))
    await db.commit()
    return TokenResponse(access_token=create_access_token(user.id, org.id, user.role))


@app.post("/api/v1/auth/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    user = await db.scalar(select(User).where(User.email == payload.email))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    db.add(AuditLog(organization_id=user.organization_id, user_id=user.id, action="LOGIN"))
    await db.commit()
    return TokenResponse(access_token=create_access_token(user.id, user.organization_id, user.role))


@app.get("/api/v1/me")
async def me(user: User = Depends(get_current_user)) -> dict:
    return {
        "user_id": str(user.id),
        "organization_id": str(user.organization_id),
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
    }


@app.get("/api/v1/cases", response_model=list[CaseResponse])
async def list_cases(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[CaseResponse]:
    result = await db.scalars(
        select(Case).where(Case.organization_id == user.organization_id).order_by(Case.created_at.desc())
    )
    return list(result.all())


@app.post("/api/v1/cases", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
async def create_case(
    payload: CaseCreate,
    user: User = Depends(require_roles("organization_admin", "recovery_manager")),
    db: AsyncSession = Depends(get_db),
) -> CaseResponse:
    duplicate = await db.scalar(select(Case).where(Case.case_number == payload.case_number))
    if duplicate:
        raise HTTPException(status_code=409, detail="Case number already exists")
    case = Case(
        organization_id=user.organization_id,
        case_number=payload.case_number,
        borrower_name=payload.borrower_name,
        status=payload.status,
        priority=payload.priority,
        known_phone=payload.known_phone,
        known_email=str(payload.known_email) if payload.known_email else None,
        known_address=payload.known_address,
    )
    db.add(case)
    await db.flush()
    db.add(AuditLog(organization_id=user.organization_id, user_id=user.id, case_id=case.id, action="CASE_CREATE"))
    await db.commit()
    await db.refresh(case)
    return CaseResponse.model_validate(case)


@app.post("/api/v3/investigations")
async def create_investigation(
    request: InvestigationRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    try:
        case_id = UUID(request.case_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid case_id") from exc

    case = await db.scalar(
        select(Case).where(Case.id == case_id, Case.organization_id == user.organization_id)
    )
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    investigation_id = f"INV-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"
    db.add(
        AuditLog(
            organization_id=user.organization_id,
            user_id=user.id,
            case_id=case.id,
            action="INVESTIGATION_QUEUED",
            details=f"depth={request.depth};fields={','.join(request.fields)}",
        )
    )
    await db.commit()
    return {
        "investigation_id": investigation_id,
        "case_id": str(case.id),
        "depth": request.depth,
        "fields": request.fields,
        "status": "QUEUED",
    }
