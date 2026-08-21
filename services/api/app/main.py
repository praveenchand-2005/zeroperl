from fastapi import FastAPI
from pydantic import BaseModel
from typing import Literal
from datetime import datetime, timezone

app = FastAPI(title="Recovery Intelligence API", version="0.1.0")

class HealthResponse(BaseModel):
    status: str
    version: str

class InvestigationRequest(BaseModel):
    case_id: str
    depth: Literal["QUICK", "STANDARD", "DEEP"] = "STANDARD"
    fields: list[str] = []

@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", version="0.1.0")

@app.get("/api/v1/cases")
def list_cases() -> dict:
    return {"items": [], "total": 0}

@app.post("/api/v3/investigations")
def create_investigation(request: InvestigationRequest) -> dict:
    return {
        "investigation_id": f"INV-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        "case_id": request.case_id,
        "depth": request.depth,
        "fields": request.fields,
        "status": "QUEUED",
    }
