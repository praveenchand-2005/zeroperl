from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .auth import get_current_user
from .db import get_db
from .models import Case, Company, EmploymentRecord, OrganizationRelationship, Profile, User
from .v4_intelligence import ProfileCandidate, profile_match_score, relationship_requires_review, same_company

router = APIRouter(prefix="/api/v4", tags=["v4-intelligence"])


class ProfileCreate(BaseModel):
    case_id: UUID
    platform: str = Field(min_length=2, max_length=80)
    profile_url: str
    username: str | None = None
    display_name: str | None = None
    public_location: str | None = None
    public_company: str | None = None
    public_position: str | None = None
    headline: str | None = None


class CompanyCreate(BaseModel):
    case_id: UUID
    legal_name: str = Field(min_length=2, max_length=300)
    trade_name: str | None = None
    registration_number: str | None = None
    country: str | None = None
    state: str | None = None
    city: str | None = None
    website: str | None = None
    industry: str | None = None


class EmploymentCreate(BaseModel):
    case_id: UUID
    profile_id: UUID | None = None
    company_id: UUID | None = None
    job_title: str | None = None
    status: str = "CURRENT_CANDIDATE"
    confidence: float = 0.0
    evidence_id: UUID | None = None


class RelationshipCreate(BaseModel):
    case_id: UUID
    company_id: UUID | None = None
    source_entity_id: UUID | None = None
    target_entity_id: UUID | None = None
    relationship_type: str
    evidence_id: UUID | None = None
    confidence: float = 0.0


async def authorized_case(case_id: UUID, user: User, db: AsyncSession) -> Case:
    case = await db.scalar(select(Case).where(Case.id == case_id, Case.organization_id == user.organization_id))
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case


@router.get("/cases/{case_id}/profiles")
async def list_profiles(case_id: UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> list[dict]:
    await authorized_case(case_id, user, db)
    rows = await db.scalars(select(Profile).where(Profile.organization_id == user.organization_id, Profile.case_id == case_id).order_by(Profile.last_seen.desc()))
    return [{"id": str(x.id), "platform": x.platform, "profile_url": x.profile_url, "display_name": x.display_name, "location": x.public_location, "company": x.public_company, "position": x.public_position, "confidence": x.confidence, "verification_status": x.verification_status} for x in rows.all()]


@router.post("/cases/{case_id}/profiles", status_code=201)
async def create_profile(case_id: UUID, payload: ProfileCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> dict:
    await authorized_case(case_id, user, db)
    candidate = ProfileCandidate(payload.platform, payload.profile_url, payload.display_name, payload.public_location, payload.public_company, payload.public_position)
    score = profile_match_score((await db.scalar(select(Case.borrower_name).where(Case.id == case_id))).__str__(), None, candidate)
    profile = Profile(organization_id=user.organization_id, case_id=case_id, platform=payload.platform, profile_url=payload.profile_url, username=payload.username, display_name=payload.display_name, public_location=payload.public_location, public_company=payload.public_company, public_position=payload.public_position, headline=payload.headline, confidence=score * 100)
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return {"profile_id": str(profile.id), "confidence": profile.confidence, "verification_status": profile.verification_status}


@router.get("/cases/{case_id}/companies")
async def list_companies(case_id: UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> list[dict]:
    await authorized_case(case_id, user, db)
    rows = await db.scalars(select(Company).where(Company.organization_id == user.organization_id, Company.case_id == case_id).order_by(Company.legal_name))
    return [{"id": str(x.id), "legal_name": x.legal_name, "trade_name": x.trade_name, "registration_number": x.registration_number, "city": x.city, "state": x.state, "country": x.country, "website": x.website, "industry": x.industry, "confidence": x.confidence, "verification_status": x.verification_status} for x in rows.all()]


@router.post("/cases/{case_id}/companies", status_code=201)
async def create_company(case_id: UUID, payload: CompanyCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> dict:
    await authorized_case(case_id, user, db)
    company = Company(organization_id=user.organization_id, case_id=case_id, legal_name=payload.legal_name, trade_name=payload.trade_name, registration_number=payload.registration_number, country=payload.country, state=payload.state, city=payload.city, website=payload.website, industry=payload.industry, confidence=0.0)
    db.add(company)
    await db.commit()
    await db.refresh(company)
    return {"company_id": str(company.id), "verification_status": company.verification_status}


@router.post("/cases/{case_id}/employment", status_code=201)
async def create_employment(case_id: UUID, payload: EmploymentCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> dict:
    await authorized_case(case_id, user, db)
    if payload.profile_id:
        profile = await db.scalar(select(Profile).where(Profile.id == payload.profile_id, Profile.organization_id == user.organization_id, Profile.case_id == case_id))
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
    if payload.company_id:
        company = await db.scalar(select(Company).where(Company.id == payload.company_id, Company.organization_id == user.organization_id, Company.case_id == case_id))
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
    record = EmploymentRecord(organization_id=user.organization_id, case_id=case_id, profile_id=payload.profile_id, company_id=payload.company_id, job_title=payload.job_title, status=payload.status, confidence=payload.confidence, source_evidence_id=payload.evidence_id)
    db.add(record)
    await db.commit()
    return {"employment_id": str(record.id), "status": record.status, "confidence": record.confidence}


@router.get("/cases/{case_id}/employment")
async def list_employment(case_id: UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> list[dict]:
    await authorized_case(case_id, user, db)
    rows = await db.scalars(select(EmploymentRecord).where(EmploymentRecord.organization_id == user.organization_id, EmploymentRecord.case_id == case_id).order_by(EmploymentRecord.id.desc()))
    return [{"id": str(x.id), "profile_id": str(x.profile_id) if x.profile_id else None, "company_id": str(x.company_id) if x.company_id else None, "job_title": x.job_title, "status": x.status, "confidence": x.confidence, "verification_status": x.verification_status} for x in rows.all()]


@router.post("/cases/{case_id}/relationships", status_code=201)
async def create_relationship(case_id: UUID, payload: RelationshipCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> dict:
    await authorized_case(case_id, user, db)
    if relationship_requires_review(payload.confidence, payload.relationship_type):
        raise HTTPException(status_code=422, detail="Relationship requires human review before persistence")
    relationship = OrganizationRelationship(organization_id=user.organization_id, case_id=case_id, company_id=payload.company_id, source_entity_id=payload.source_entity_id, target_entity_id=payload.target_entity_id, relationship_type=payload.relationship_type, evidence_id=payload.evidence_id, confidence=payload.confidence, verification_status="UNVERIFIED")
    db.add(relationship)
    await db.commit()
    return {"relationship_id": str(relationship.id), "relationship_type": relationship.relationship_type, "confidence": relationship.confidence}
