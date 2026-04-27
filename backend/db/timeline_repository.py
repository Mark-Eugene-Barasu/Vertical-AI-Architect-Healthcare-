import boto3
import os
from datetime import datetime, timezone
from boto3.dynamodb.conditions import Key, Attr

TABLE_NAME = "medimind-patient-timeline"
dynamodb = boto3.resource("dynamodb", region_name=os.getenv("AWS_REGION", "us-east-1"))
table = dynamodb.Table(TABLE_NAME)

VALID_EVENT_TYPES = frozenset(["NOTE", "DRUG_CHECK", "ALERT", "DIAGNOSIS", "MEDICATION", "LAB_RESULT", "VISIT"])

def add_timeline_event(patient_id: str, event_type: str, title: str, data: dict, clinician_id: str) -> dict:
    timestamp = datetime.now(timezone.utc).isoformat()
    item = {
        "patient_id":   patient_id,
        "timestamp":    timestamp,
        "event_type":   event_type,
        "title":        title,
        "data":         data,
        "clinician_id": clinician_id,
    }
    table.put_item(Item=item)
    return item

def get_patient_timeline(patient_id: str, limit: int = 50) -> list[dict]:
    response = table.query(
        KeyConditionExpression=Key("patient_id").eq(patient_id),
        ScanIndexForward=False,
        Limit=min(limit, 100),  # cap at 100 to prevent abuse
    )
    return response.get("Items", [])

def get_timeline_by_type(patient_id: str, event_type: str) -> list[dict]:
    response = table.query(
        KeyConditionExpression=Key("patient_id").eq(patient_id),
        FilterExpression=Attr("event_type").eq(event_type),
        ScanIndexForward=False,
    )
    return response.get("Items", [])
