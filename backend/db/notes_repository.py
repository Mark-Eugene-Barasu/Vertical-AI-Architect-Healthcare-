from __future__ import annotations

import boto3
import os
import uuid
from datetime import datetime, timezone
from typing import Optional
from boto3.dynamodb.conditions import Key

TABLE_NAME = "medimind-clinical-notes"
dynamodb = boto3.resource("dynamodb", region_name=os.getenv("AWS_REGION", "us-east-1"))
table = dynamodb.Table(TABLE_NAME)

def save_note(patient_id: str, transcript: str, clinical_note: dict, clinician_id: str) -> str:
    note_id = str(uuid.uuid4())
    table.put_item(Item={
        "patient_id":    patient_id,
        "note_id":       note_id,
        "clinician_id":  clinician_id,
        "transcript":    transcript,
        "clinical_note": clinical_note,
        "created_at":    datetime.now(timezone.utc).isoformat(),
        "status":        "active",
    })
    return note_id

def get_notes(patient_id: str) -> list[dict]:
    response = table.query(
        KeyConditionExpression=Key("patient_id").eq(patient_id)
    )
    return response.get("Items", [])

def get_note(patient_id: str, note_id: str) -> dict | None:
    response = table.get_item(Key={"patient_id": patient_id, "note_id": note_id})
    return response.get("Item")

def update_note(patient_id: str, note_id: str, updated_note: dict) -> bool:
    table.update_item(
        Key={"patient_id": patient_id, "note_id": note_id},
        UpdateExpression="SET clinical_note = :note, updated_at = :ts",
        ExpressionAttributeValues={
            ":note": updated_note,
            ":ts":   datetime.now(timezone.utc).isoformat(),
        }
    )
    return True
