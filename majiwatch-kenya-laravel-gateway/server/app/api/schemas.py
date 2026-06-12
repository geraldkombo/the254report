from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class HealthOut(BaseModel):
    ok: bool
    name: str
    env: str


class CountyScoreOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    county_code: str
    year: int
    period: str
    water_access: float
    sanitation: float
    water_quality: float
    utility_performance: float
    governance: float
    climate_resilience: float
    composite: float
    confidence: float
    computed_at: datetime


class AlertOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    county_code: str
    severity: str
    rule: str
    message: str
    triggered_at: datetime
    resolved_at: datetime | None
    pdf_report_url: str | None = None


class ResolveAlertOut(BaseModel):
    id: UUID
    resolved_at: datetime


class ComputeRequest(BaseModel):
    year: int | None = None
    period: str | None = None


class ComputeResponse(BaseModel):
    enqueued: bool
    year: int
    period: str
    task_id: str | None = None


class WaterpointLookupIn(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)


class WaterpointLookupOut(BaseModel):
    id: UUID
    county_code: str | None
    source: str
    type: str
    functionality: str | None
    lat: float
    lng: float
    distance_m: float
