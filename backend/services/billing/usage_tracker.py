import boto3
import os
from datetime import datetime, timezone
from boto3.dynamodb.conditions import Key

TABLE_NAME = "medimind-usage"
dynamodb = boto3.resource("dynamodb", region_name=os.getenv("AWS_REGION", "us-east-1"))
table = dynamodb.Table(TABLE_NAME)

USAGE_TYPES = ["note_generated", "drug_check", "decision_support", "transcription"]

def record_usage(org_id: str, usage_type: str, clinician_id: str, count: int = 1):
    month = datetime.now(timezone.utc).strftime("%Y-%m")
    table.update_item(
        Key={"org_id": org_id, "month": month},
        UpdateExpression="ADD #ut :count SET last_updated = :ts",
        ExpressionAttributeNames={"#ut": usage_type},
        ExpressionAttributeValues={":count": count, ":ts": datetime.now(timezone.utc).isoformat()},
    )

def get_usage(org_id: str, month: str = None) -> dict:
    month = month or datetime.now(timezone.utc).strftime("%Y-%m")
    response = table.get_item(Key={"org_id": org_id, "month": month})
    return response.get("Item", {"org_id": org_id, "month": month})

def get_usage_history(org_id: str) -> list[dict]:
    response = table.query(KeyConditionExpression=Key("org_id").eq(org_id))
    return response.get("Items", [])
