import boto3
import json
import os
from datetime import datetime, timezone
from enum import Enum

sns = boto3.client("sns", region_name=os.getenv("AWS_REGION", "us-east-1"))
ALERT_TOPIC_ARN = os.getenv("SNS_ALERT_TOPIC_ARN")

class AlertSeverity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    INFO = "INFO"

class AlertType(str, Enum):
    DRUG_INTERACTION = "DRUG_INTERACTION"
    ABNORMAL_VITALS = "ABNORMAL_VITALS"
    CRITICAL_LAB = "CRITICAL_LAB"
    ALLERGY_CONFLICT = "ALLERGY_CONFLICT"
    DOSAGE_ERROR = "DOSAGE_ERROR"

def build_alert(
    alert_type: AlertType,
    severity: AlertSeverity,
    patient_id: str,
    clinician_id: str,
    message: str,
    details: dict = None
) -> dict:
    return {
        "alert_type": alert_type,
        "severity": severity,
        "patient_id": patient_id,
        "clinician_id": clinician_id,
        "message": message,
        "details": details or {},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

def publish_sns_alert(alert: dict):
    """Publish critical alerts to SNS for email/SMS notification."""
    if alert["severity"] in (AlertSeverity.CRITICAL, AlertSeverity.HIGH):
        sns.publish(
            TopicArn=ALERT_TOPIC_ARN,
            Subject=f"[MediMind {alert['severity']}] {alert['alert_type']} — Patient {alert['patient_id']}",
            Message=json.dumps(alert, indent=2),
            MessageAttributes={
                "severity": {"DataType": "String", "StringValue": alert["severity"]},
                "alert_type": {"DataType": "String", "StringValue": alert["alert_type"]},
            }
        )
