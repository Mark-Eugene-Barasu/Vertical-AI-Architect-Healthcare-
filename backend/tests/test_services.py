"""Tests for backend service modules."""

import pytest
from unittest.mock import patch, MagicMock
from services.comprehend_medical import _flag_interactions
from services.alerts.publisher import build_alert, AlertSeverity, AlertType


class TestFlagInteractions:
    """Test the drug interaction flagging logic."""

    def test_warfarin_aspirin_flagged(self):
        concepts = [
            {"medication": "Warfarin", "rxnorm_code": "11289", "description": "Warfarin"},
            {"medication": "Aspirin", "rxnorm_code": "1191", "description": "Aspirin"},
        ]
        result = _flag_interactions(concepts)
        assert len(result) == 1
        assert result[0]["severity"] == "HIGH"
        assert "warfarin" in result[0]["drugs"]
        assert "aspirin" in result[0]["drugs"]

    def test_no_interactions_for_safe_combo(self):
        concepts = [
            {"medication": "Acetaminophen", "rxnorm_code": "161", "description": "Acetaminophen"},
            {"medication": "Ibuprofen", "rxnorm_code": "5640", "description": "Ibuprofen"},
        ]
        result = _flag_interactions(concepts)
        assert len(result) == 0

    def test_empty_input(self):
        result = _flag_interactions([])
        assert result == []

    def test_single_drug_no_interaction(self):
        concepts = [{"medication": "Warfarin", "rxnorm_code": "11289", "description": "Warfarin"}]
        result = _flag_interactions(concepts)
        assert result == []


class TestBuildAlert:
    """Test alert construction."""

    def test_builds_complete_alert(self):
        alert = build_alert(
            alert_type=AlertType.DRUG_INTERACTION,
            severity=AlertSeverity.CRITICAL,
            patient_id="p-123",
            clinician_id="c-456",
            message="Dangerous interaction",
            details={"drugs": ["warfarin", "aspirin"]},
        )
        assert alert["alert_type"] == "DRUG_INTERACTION"
        assert alert["severity"] == "CRITICAL"
        assert alert["patient_id"] == "p-123"
        assert alert["clinician_id"] == "c-456"
        assert alert["message"] == "Dangerous interaction"
        assert alert["details"]["drugs"] == ["warfarin", "aspirin"]
        assert "timestamp" in alert

    def test_default_empty_details(self):
        alert = build_alert(
            alert_type=AlertType.ABNORMAL_VITALS,
            severity=AlertSeverity.HIGH,
            patient_id="p-123",
            clinician_id="c-456",
            message="Abnormal vitals detected",
        )
        assert alert["details"] == {}

    def test_all_severity_levels(self):
        for severity in AlertSeverity:
            alert = build_alert(
                alert_type=AlertType.CRITICAL_LAB,
                severity=severity,
                patient_id="p-1",
                clinician_id="c-1",
                message="Test alert",
            )
            assert alert["severity"] == severity.value

    def test_all_alert_types(self):
        for alert_type in AlertType:
            alert = build_alert(
                alert_type=alert_type,
                severity=AlertSeverity.INFO,
                patient_id="p-1",
                clinician_id="c-1",
                message="Test alert",
            )
            assert alert["alert_type"] == alert_type.value


class TestBedrockSanitize:
    """Test the input sanitization function."""

    def test_strips_control_characters(self):
        from services.bedrock import _sanitize
        text = "Hello\x00World\x7f"
        result = _sanitize(text, 100)
        assert "\x00" not in result
        assert "\x7f" not in result
        assert "HelloWorld" == result

    def test_truncates_to_max_length(self):
        from services.bedrock import _sanitize
        text = "A" * 500
        result = _sanitize(text, 100)
        assert len(result) == 100

    def test_preserves_normal_text(self):
        from services.bedrock import _sanitize
        text = "Normal clinical text with punctuation, numbers 123, and newlines.\n"
        result = _sanitize(text, 1000)
        assert result == text
