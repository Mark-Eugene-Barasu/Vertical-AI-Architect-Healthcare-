import boto3
import os
import logging
from datetime import datetime, timezone, timedelta
from services.notifications.email import send_trial_expiry_warning, send_usage_alert, send_monthly_report
from services.analytics.metrics import get_org_metrics

dynamodb = boto3.resource("dynamodb", region_name=os.getenv("AWS_REGION", "us-east-1"))
orgs_table = dynamodb.Table("medimind-organizations")
logger = logging.getLogger(__name__)

def _scan_all_orgs() -> list[dict]:
    """Paginated scan — avoids 1MB truncation on large tables."""
    items: list[dict] = []
    kwargs: dict = {}
    while True:
        response = orgs_table.scan(**kwargs)
        items.extend(response.get("Items", []))
        last_key = response.get("LastEvaluatedKey")
        if not last_key:
            break
        kwargs["ExclusiveStartKey"] = last_key
    return items

def run_daily_checks():
    """Run daily notification checks — triggered by EventBridge."""
    orgs = _scan_all_orgs()
    now = datetime.now(timezone.utc)

    for org in orgs:
        if org.get("status") != "active":
            continue

        email = org.get("email")
        name  = org.get("admin_name", "Doctor")
        plan  = org.get("plan", "starter")

        if not email:
            logger.warning("Org missing email", extra={"org_id": org.get("org_id")})
            continue

        # Trial expiry warnings
        trial_start = org.get("created_at")
        if trial_start and not org.get("subscription_id"):
            try:
                start_dt  = datetime.fromisoformat(trial_start)
                days_used = (now - start_dt).days
                days_left = 14 - days_used
                if days_left in (7, 3, 1):
                    send_trial_expiry_warning(email, name, days_left, plan)
            except (ValueError, TypeError) as e:
                logger.error("Trial expiry check failed", extra={"org_id": org.get("org_id"), "error": str(e)})

        # Usage alerts
        try:
            metrics = get_org_metrics(org["org_id"])
            plan_limits = {"starter": 500, "growth": 2000, "enterprise": -1}
            limit = plan_limits.get(plan, 500)
            if limit > 0 and metrics["notes_generated"] > 0:
                usage_pct = int((metrics["notes_generated"] / limit) * 100)
                if usage_pct in range(80, 82) or usage_pct in range(95, 97):
                    send_usage_alert(email, name, usage_pct, plan)
        except Exception as e:
            logger.error("Usage alert check failed", extra={"org_id": org.get("org_id"), "error": str(e)})

def run_monthly_reports():
    """Send monthly summary reports — triggered by EventBridge on 1st of month."""
    orgs = _scan_all_orgs()
    for org in orgs:
        if org.get("status") != "active" or not org.get("email"):
            continue
        try:
            metrics = get_org_metrics(org["org_id"])
            send_monthly_report(
                to=org["email"],
                name=org.get("admin_name", "Doctor"),
                org_name=org.get("name", "Your Organization"),
                metrics=metrics,
            )
        except Exception as e:
            logger.error("Monthly report failed", extra={"org_id": org.get("org_id"), "error": str(e)})

def lambda_handler(event, context):
    """AWS Lambda handler for EventBridge scheduled triggers."""
    rule = event.get("rule", "daily")
    if rule == "daily":
        run_daily_checks()
    elif rule == "monthly":
        run_monthly_reports()
    else:
        logger.warning("Unknown scheduler rule", extra={"rule": rule})
    return {"status": "ok"}
