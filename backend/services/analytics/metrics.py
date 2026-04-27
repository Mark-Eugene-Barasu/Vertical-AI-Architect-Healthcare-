import boto3
import os
from datetime import datetime, timezone, timedelta
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource("dynamodb", region_name=os.getenv("AWS_REGION", "us-east-1"))
timeline_table = dynamodb.Table("medimind-patient-timeline")
usage_table    = dynamodb.Table("medimind-usage")

def get_org_metrics(org_id: str) -> dict:
    """Aggregate key clinical metrics for an organization."""
    month = datetime.now(timezone.utc).strftime("%Y-%m")
    usage = usage_table.get_item(Key={"org_id": org_id, "month": month}).get("Item", {})

    notes_generated  = int(usage.get("note_generated", 0))
    drug_checks      = int(usage.get("drug_check", 0))
    decision_queries = int(usage.get("decision_support", 0))
    transcriptions   = int(usage.get("transcription", 0))
    time_saved_hours = round((notes_generated * 15 + drug_checks * 5) / 60, 1)

    return {
        "month":                       month,
        "notes_generated":             notes_generated,
        "drug_checks_performed":       drug_checks,
        "decision_queries":            decision_queries,
        "transcriptions":              transcriptions,
        "estimated_time_saved_hours":  time_saved_hours,
        "estimated_errors_prevented":  round(drug_checks * 0.12),
    }

def get_usage_trend(org_id: str, months: int = 6) -> list[dict]:
    """Get monthly usage trend for the last N months."""
    trend = []
    for i in range(min(months, 24)):  # cap at 24 months
        dt = datetime.now(timezone.utc) - timedelta(days=30 * i)
        month = dt.strftime("%Y-%m")
        item = usage_table.get_item(Key={"org_id": org_id, "month": month}).get("Item", {})
        trend.append({
            "month":           month,
            "notes":           int(item.get("note_generated", 0)),
            "drug_checks":     int(item.get("drug_check", 0)),
            "decision_queries": int(item.get("decision_support", 0)),
        })
    return list(reversed(trend))

def get_alert_summary(org_id: str) -> dict:
    """Summarize alerts scoped to this org from the timeline table."""
    response = timeline_table.query(
        IndexName="org_id-event_type-index",
        KeyConditionExpression=Key("org_id").eq(org_id) & Key("event_type").eq("ALERT"),
    ) if False else timeline_table.scan(  # fallback until GSI is provisioned
        FilterExpression=Attr("event_type").eq("ALERT") & Attr("clinician_id").begins_with(org_id[:8])
    )
    items = response.get("Items", [])
    critical = sum(1 for i in items if i.get("data", {}).get("severity") == "CRITICAL")
    high     = sum(1 for i in items if i.get("data", {}).get("severity") == "HIGH")
    return {
        "total_alerts": len(items),
        "critical":     critical,
        "high":         high,
        "medium":       max(0, len(items) - critical - high),
    }
