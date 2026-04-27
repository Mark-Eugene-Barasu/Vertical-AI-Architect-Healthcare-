from __future__ import annotations

import boto3
import os
import uuid
from datetime import datetime, timezone
from typing import Optional

TABLE_NAME = "medimind-organizations"
dynamodb = boto3.resource("dynamodb", region_name=os.getenv("AWS_REGION", "us-east-1"))
table = dynamodb.Table(TABLE_NAME)

def create_org(name: str, email: str, admin_id: str) -> dict:
    org_id = str(uuid.uuid4())
    item = {
        "org_id":     org_id,
        "name":       name,
        "email":      email,
        "admin_id":   admin_id,
        "plan":       "starter",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status":     "active",
    }
    table.put_item(Item=item)
    return item

def get_org(org_id: str) -> dict | None:
    response = table.get_item(Key={"org_id": org_id})
    return response.get("Item")

def update_org_billing(org_id: str, customer_id: str, subscription_id: str, plan: str):
    table.update_item(
        Key={"org_id": org_id},
        UpdateExpression="SET stripe_customer_id = :cid, subscription_id = :sid, plan = :plan, updated_at = :ts",
        ExpressionAttributeValues={
            ":cid":  customer_id,
            ":sid":  subscription_id,
            ":plan": plan,
            ":ts":   datetime.now(timezone.utc).isoformat(),
        }
    )
