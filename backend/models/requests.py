"""Pydantic models for API request validation."""

from pydantic import BaseModel, Field
from typing import Optional


class NoteGenerateRequest(BaseModel):
    transcript: str = Field(..., min_length=1, max_length=10000, description="Doctor-patient conversation transcript")
    patient_id: str = Field(..., min_length=1, max_length=100, description="Patient identifier")


class NoteUpdateRequest(BaseModel):
    clinical_note: dict = Field(..., description="Updated SOAP note content")


class DrugCheckRequest(BaseModel):
    medications: list[str] = Field(default_factory=list, description="List of medication names")
    clinical_text: Optional[str] = Field(default="", max_length=10000, description="Clinical text to extract medications from")
    patient_id: Optional[str] = Field(default="", max_length=100, description="Patient identifier for timeline logging")


class DrugExtractRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000, description="Clinical text to extract medications from")


class DecisionSupportRequest(BaseModel):
    patient_context: str = Field(..., min_length=1, max_length=5000, description="Patient context (age, symptoms, history)")
    query: str = Field(..., min_length=1, max_length=500, description="Clinical query")


class AlertTriggerRequest(BaseModel):
    alert_type: str = Field(..., description="Type of alert")
    severity: str = Field(..., description="Alert severity level")
    patient_id: str = Field(..., min_length=1, description="Patient identifier")
    message: str = Field(..., min_length=1, max_length=1000, description="Alert message")
    details: dict = Field(default_factory=dict, description="Additional alert details")


class DrugInteractionAlertRequest(BaseModel):
    interactions: list[dict] = Field(default_factory=list, description="List of detected drug interactions")
    patient_id: str = Field(default="", description="Patient identifier")


class TimelineEventRequest(BaseModel):
    event_type: str = Field(..., description="Type of timeline event")
    title: str = Field(..., min_length=1, max_length=500, description="Event title")
    data: dict = Field(default_factory=dict, description="Event data payload")


class SubscribeRequest(BaseModel):
    plan: str = Field(..., description="Subscription plan name")


class BillingPortalRequest(BaseModel):
    return_url: str = Field(default="https://app.medimind.ai", description="URL to redirect to after portal session")
