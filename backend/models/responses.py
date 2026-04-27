"""Pydantic models for API response serialization."""

from pydantic import BaseModel
from typing import Optional


class DependencyStatus(BaseModel):
    status: str
    latency_ms: Optional[float] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    dependencies: dict[str, DependencyStatus]


class SOAPNoteSchema(BaseModel):
    subjective: str = ""
    objective: str = ""
    assessment: str = ""
    plan: str = ""
    follow_up: str = ""


class NoteResponse(BaseModel):
    patient_id: str
    note_id: str
    transcript: Optional[str] = None
    clinical_note: dict
    clinician_id: Optional[str] = None
    created_at: Optional[str] = None
    status: Optional[str] = None


class NoteListResponse(BaseModel):
    patient_id: str
    notes: list[dict]


class DrugInteractionSchema(BaseModel):
    severity: str
    drugs: list[str]
    warning: str


class DrugCheckResponse(BaseModel):
    medications: list[str]
    interactions: list[DrugInteractionSchema]


class MedicationExtractResponse(BaseModel):
    medications: list[str]


class DecisionSupportResponse(BaseModel):
    query: str
    suggestions: str


class AlertResponse(BaseModel):
    alert_type: str
    severity: str
    patient_id: str
    clinician_id: str
    message: str
    details: dict
    timestamp: str


class AlertTriggerResponse(BaseModel):
    status: str
    alert: AlertResponse


class DrugInteractionAlertResponse(BaseModel):
    status: str
    count: int


class TimelineEventSchema(BaseModel):
    patient_id: str
    timestamp: str
    event_type: str
    title: str
    data: dict
    clinician_id: str


class TimelineResponse(BaseModel):
    patient_id: str
    timeline: list[TimelineEventSchema]


class TimelineFilteredResponse(BaseModel):
    patient_id: str
    event_type: str
    timeline: list[TimelineEventSchema]
