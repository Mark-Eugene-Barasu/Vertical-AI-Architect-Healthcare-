import logging
import stripe
from fastapi import APIRouter, HTTPException, Depends, Request
from auth.cognito import verify_token
from services.billing import (
    create_customer, create_subscription, get_subscription,
    cancel_subscription, create_billing_portal, construct_webhook_event,
    get_usage, get_usage_history, PLANS
)
from db.org_repository import get_org, update_org_billing

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/plans")
def list_plans():
    return {"plans": {k: {"notes": v["notes"], "clinicians": v["clinicians"]} for k, v in PLANS.items()}}

@router.post("/subscribe")
def subscribe(payload: dict, claims: dict = Depends(verify_token)):
    plan = payload.get("plan")
    if plan not in PLANS:
        raise HTTPException(status_code=400, detail=f"Invalid plan. Choose from: {list(PLANS.keys())}")
    org_id = claims.get("custom:org_id")
    org = get_org(org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    customer_id = org.get("stripe_customer_id") or create_customer(org_id, org["name"], org["email"])
    result = create_subscription(customer_id, plan)
    update_org_billing(org_id, customer_id, result["subscription_id"], plan)
    return result

@router.get("/subscription")
def subscription_status(claims: dict = Depends(verify_token)):
    org_id = claims.get("custom:org_id")
    org = get_org(org_id)
    if not org or not org.get("subscription_id"):
        return {"status": "no_subscription"}
    return get_subscription(org["subscription_id"])

@router.delete("/subscription")
def cancel(claims: dict = Depends(verify_token)):
    org_id = claims.get("custom:org_id")
    org = get_org(org_id)
    if not org or not org.get("subscription_id"):
        raise HTTPException(status_code=404, detail="No active subscription")
    return cancel_subscription(org["subscription_id"])

@router.post("/portal")
def billing_portal(payload: dict, claims: dict = Depends(verify_token)):
    org_id = claims.get("custom:org_id")
    org = get_org(org_id)
    if not org or not org.get("stripe_customer_id"):
        raise HTTPException(status_code=404, detail="No billing account found")
    url = create_billing_portal(
        org["stripe_customer_id"],
        payload.get("return_url", "https://app.medimind.ai")
    )
    return {"url": url}

@router.get("/usage")
def usage(claims: dict = Depends(verify_token)):
    org_id = claims.get("custom:org_id")
    return {"current_month": get_usage(org_id), "history": get_usage_history(org_id)}

@router.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig = request.headers.get("stripe-signature")
    try:
        event = construct_webhook_event(payload, sig)
    except stripe.error.SignatureVerificationError:
        logger.warning("Stripe webhook signature verification failed")
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    event_type = event["type"]
    obj = event["data"]["object"]

    if event_type == "invoice.payment_succeeded":
        customer_id = obj.get("customer")
        amount = obj.get("amount_paid", 0)
        logger.info("Payment succeeded", extra={"customer_id": customer_id, "amount_cents": amount})

    elif event_type == "invoice.payment_failed":
        customer_id = obj.get("customer")
        logger.warning("Payment failed", extra={"customer_id": customer_id})

    elif event_type == "customer.subscription.deleted":
        subscription_id = obj.get("id")
        customer_id = obj.get("customer")
        logger.info("Subscription cancelled", extra={"subscription_id": subscription_id, "customer_id": customer_id})

    elif event_type == "customer.subscription.updated":
        subscription_id = obj.get("id")
        status = obj.get("status")
        logger.info("Subscription updated", extra={"subscription_id": subscription_id, "status": status})

    else:
        logger.debug("Unhandled Stripe event", extra={"event_type": event_type})

    return {"status": "ok"}
