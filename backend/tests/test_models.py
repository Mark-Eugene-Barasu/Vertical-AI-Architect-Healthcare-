"""Tests for Pydantic request/response models."""

import pytest
from pydantic import ValidationError
from models.requests import (
    NoteGenerateRequest,
    NoteUpdateRequest,
    DrugCheckRequest,
    DrugExtractRequest,
    DecisionSupportRequest,
    AlertTriggerRequest,
    TimelineEventRequest,
    SubscribeRequest,
)


class TestNoteGenerateRequest:
    def test_valid_request(self):
        req = NoteGenerateRequest(transcript="Patient reports headache", patient_id="p-123")
        assert req.transcript == "Patient reports headache"
        assert req.patient_id == "p-123"

    def test_missing_transcript_raises(self):
        with pytest.raises(ValidationError):
            NoteGenerateRequest(transcript="", patient_id="p-123")

    def test_missing_patient_id_raises(self):
        with pytest.raises(ValidationError):
            NoteGenerateRequest(transcript="Some text", patient_id="")


class TestDrugCheckRequest:
    def test_valid_with_medications(self):
        req = DrugCheckRequest(medications=["aspirin", "warfarin"])
        assert len(req.medications) == 2

    def test_valid_with_clinical_text(self):
        req = DrugCheckRequest(clinical_text="Patient takes aspirin and ibuprofen")
        assert req.clinical_text == "Patient takes aspirin and ibuprofen"

    def test_defaults(self):
        req = DrugCheckRequest()
        assert req.medications == []
        assert req.clinical_text == ""
        assert req.patient_id == ""


class TestDrugExtractRequest:
    def test_valid(self):
        req = DrugExtractRequest(text="Patient is on metformin 500mg")
        assert "metformin" in req.text

    def test_empty_text_raises(self):
        with pytest.raises(ValidationError):
            DrugExtractRequest(text="")


class TestDecisionSupportRequest:
    def test_valid(self):
        req = DecisionSupportRequest(
            patient_context="65-year-old male with diabetes",
            query="What is the recommended HbA1c target?"
        )
        assert req.patient_context
        assert req.query

    def test_missing_context_raises(self):
        with pytest.raises(ValidationError):
            DecisionSupportRequest(patient_context="", query="What treatment?")

    def test_missing_query_raises(self):
        with pytest.raises(ValidationError):
            DecisionSupportRequest(patient_context="Patient info", query="")


class TestAlertTriggerRequest:
    def test_valid(self):
        req = AlertTriggerRequest(
            alert_type="DRUG_INTERACTION",
            severity="CRITICAL",
            patient_id="p-123",
            message="Dangerous drug interaction detected",
        )
        assert req.alert_type == "DRUG_INTERACTION"
        assert req.details == {}

    def test_missing_message_raises(self):
        with pytest.raises(ValidationError):
            AlertTriggerRequest(
                alert_type="DRUG_INTERACTION",
                severity="HIGH",
                patient_id="p-123",
                message="",
            )


class TestTimelineEventRequest:
    def test_valid(self):
        req = TimelineEventRequest(event_type="NOTE", title="Clinical note generated")
        assert req.event_type == "NOTE"
        assert req.data == {}

    def test_missing_title_raises(self):
        with pytest.raises(ValidationError):
            TimelineEventRequest(event_type="NOTE", title="")


class TestSubscribeRequest:
    def test_valid(self):
        req = SubscribeRequest(plan="starter")
        assert req.plan == "starter"
