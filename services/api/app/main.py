from datetime import datetime, timezone
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .auth import create_access_token, get_current_user, hash_password, require_roles, verify_password
from .db import engine, get_db
from .models import AuditLog, Base, Case, Evidence, Investigation, Organization, ScraperJob, SourceRegistry, User

app = FastAPI(title="Recovery Intelligence API", version="0.3.0")


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
    fields: list[str] = Field(default_factory=list)
    urls: list[str] = Field(default_factory=list)


class SourceCreate(BaseModel):
    source_id: str = Field(min_length=2, max_length=120)
    source_name: str = Field(min_length=2, max_length=200)
    source_type: str = Field(min_length=2, max_length=60)
    base_url: str | None = None
    allowed_domains: list[str] = Field(default_factory=list)
    allowed_fields: list[str] = Field(default_factory=list)
    rate_limit_per_minute: int = Field(default=30, ge=1, le=10000)
    enabled: bool = True


class SourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    source_id: str
    source_name: str
    source_type: str
    base_url: str | None
    allowed_domains: list
    allowed_fields: list
    rate_limit_per_minute: int
    enabled: bool


class EvidenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    source_name: str
    source_type: str
    source_reference: str | None
    source_url: str | None
    entity_type: str | None
    field_name: str | None
    normalized_value: str | None
    verification_status: str
    confidence: float | None
    content_hash: str | None
    extraction_method: str | None
    retrieved_at: datetime


@app.on_event("startup")
async def startup() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", version="0.3.0")


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
    return {"user_id": str(user.id), "organization_id": str(user.organization_id), "email": user.email, "full_name": user.full_name, "role": user.role}


@app.get("/api/v1/cases", response_model=list[CaseResponse])
async def list_cases(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> list[CaseResponse]:
    result = await db.scalars(select(Case).where(Case.organization_id == user.organization_id).order_by(Case.created_at.desc()))
    return list(result.all())


@app.post("/api/v1/cases", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
async def create_case(payload: CaseCreate, user: User = Depends(require_roles("organization_admin", "recovery_manager")), db: AsyncSession = Depends(get_db)) -> CaseResponse:
    duplicate = await db.scalar(select(Case).where(Case.organization_id == user.organization_id, Case.case_number == payload.case_number))
    if duplicate:
        raise HTTPException(status_code=409, detail="Case number already exists")
    case = Case(organization_id=user.organization_id, case_number=payload.case_number, borrower_name=payload.borrower_name, status=payload.status, priority=payload.priority, known_phone=payload.known_phone, known_email=str(payload.known_email) if payload.known_email else None, known_address=payload.known_address)
    db.add(case)
    await db.flush()
    db.add(AuditLog(organization_id=user.organization_id, user_id=user.id, case_id=case.id, action="CASE_CREATE"))
    await db.commit()
    await db.refresh(case)
    return CaseResponse.model_validate(case)


@app.get("/api/v2/sources", response_model=list[SourceResponse])
async def list_sources(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> list[SourceResponse]:
    result = await db.scalars(select(SourceRegistry).where((SourceRegistry.organization_id == user.organization_id) | (SourceRegistry.organization_id.is_(None)), SourceRegistry.enabled.is_(True)).order_by(SourceRegistry.source_name))
    return list(result.all())


@app.post("/api/v2/sources", response_model=SourceResponse, status_code=status.HTTP_201_CREATED)
async def create_source(payload: SourceCreate, user: User = Depends(require_roles("organization_admin")), db: AsyncSession = Depends(get_db)) -> SourceResponse:
    existing = await db.scalar(select(SourceRegistry).where(SourceRegistry.organization_id == user.organization_id, SourceRegistry.source_id == payload.source_id))
    if existing:
        raise HTTPException(status_code=409, detail="Source already exists for this organization")
    source = SourceRegistry(organization_id=user.organization_id, **payload.model_dump())
    db.add(source)
    await db.flush()
    db.add(AuditLog(organization_id=user.organization_id, user_id=user.id, action="SOURCE_REGISTER", details=f"source_id={source.source_id}"))
    await db.commit()
    await db.refresh(source)
    return SourceResponse.model_validate(source)


@app.post("/api/v3/investigations")
async def create_investigation(request: InvestigationRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> dict:
    try:
        case_id = UUID(request.case_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid case_id") from exc
    case = await db.scalar(select(Case).where(Case.id == case_id, Case.organization_id == user.organization_id))
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    investigation = Investigation(organization_id=user.organization_id, case_id=case.id, requested_by=user.id, depth=request.depth, status="QUEUED")
    db.add(investigation)
    await db.flush()
    for url in request.urls:
        db.add(ScraperJob(organization_id=user.organization_id, investigation_id=investigation.id, job_type="PUBLIC_FETCH", status="QUEUED", requested_url=url, requested_fields=request.fields))
    db.add(AuditLog(organization_id=user.organization_id, user_id=user.id, case_id=case.id, action="INVESTIGATION_QUEUED", details=f"investigation={investigation.id};depth={request.depth};jobs={len(request.urls)}"))
    await db.commit()
    return {"investigation_id": str(investigation.id), "case_id": str(case.id), "depth": request.depth, "fields": request.fields, "job_count": len(request.urls), "status": "QUEUED"}


@app.get("/api/v3/investigations/{investigation_id}")
async def investigation_progress(investigation_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> dict:
    try:
        inv_id = UUID(investigation_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid investigation_id") from exc
    investigation = await db.scalar(select(Investigation).where(Investigation.id == inv_id, Investigation.organization_id == user.organization_id))
    if not investigation:
        raise HTTPException(status_code=404, detail="Investigation not found")
    job_rows = list((await db.scalars(select(ScraperJob).where(ScraperJob.investigation_id == investigation.id))).all())
    counts: dict[str, int] = {}
    for job in job_rows:
        counts[job.status] = counts.get(job.status, 0) + 1
    total = len(job_rows)
    completed = counts.get("COMPLETED", 0)
    progress = 100 if total == 0 and investigation.status == "COMPLETED" else (round(completed / total * 100, 1) if total else 0)
    return {"investigation_id": str(investigation.id), "status": investigation.status, "depth": investigation.depth, "progress_percent": progress, "jobs": counts, "job_total": total}


@app.get("/api/v3/cases/{case_id}/evidence", response_model=list[EvidenceResponse])
async def case_evidence(case_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> list[EvidenceResponse]:
    try:
        cid = UUID(case_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid case_id") from exc
    case = await db.scalar(select(Case).where(Case.id == cid, Case.organization_id == user.organization_id))
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    rows = await db.scalars(select(Evidence).where(Evidence.organization_id == user.organization_id, Evidence.case_id == cid).order_by(Evidence.retrieved_at.desc()))
    return list(rows.all())
