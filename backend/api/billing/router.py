import logging
import stripe
from fastapi import APIRouter, HTTPException, Depends, Request
from auth.cognito import verify_token
from services.billing import (
    create_customer, create_subscription, get_subscription,
    cancel_subscription, create_billing_portal, construct_webhook_event,
    get_usage, get_usage_history, PLANS,
)
from db.org_repository import get_org, update_org_billing
from models.requests import SubscribeRequest, BillingPortalRequest

router = APIRouter()
logger = logging.getLogger("medimind.billing")


@router.get("/plans")
def list_plans():
    """List available subscription plans."""
    return {"plans": {k: {"notes": v["notes"], "clinicians": v["clinicians"]} for k, v in PLANS.items()}}


@router.post("/subscribe")
def subscribe(payload: SubscribeRequest, claims: dict = Depends(verify_token)):
    """Subscribe an organization to a plan."""
    if payload.plan not in PLANS:
        raise HTTPException(status_code=400, detail=f"Invalid plan. Choose from: {list(PLANS.keys())}")
    org_id = claims.get("custom:org_id")
    org = get_org(org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    customer_id = org.get("stripe_customer_id") or create_customer(org_id, org["name"], org["email"])
    result = create_subscription(customer_id, payload.plan)
    update_org_billing(org_id, customer_id, result["subscription_id"], payload.plan)
    logger.info("subscription_created", extra={"org_id": org_id, "plan": payload.plan})
    return result


@router.get("/subscription")
def subscription_status(claims: dict = Depends(verify_token)):
    """Get current subscription status."""
    org_id = claims.get("custom:org_id")
    org = get_org(org_id)
    if not org or not org.get("subscription_id"):
        return {"status": "no_subscription"}
    return get_subscription(org["subscription_id"])


@router.delete("/subscription")
def cancel(claims: dict = Depends(verify_token)):
    """Cancel the current subscription."""
    org_id = claims.get("custom:org_id")
    org = get_org(org_id)
    if not org or not org.get("subscription_id"):
        raise HTTPException(status_code=404, detail="No active subscription")
    logger.info("subscription_cancelled", extra={"org_id": org_id})
    return cancel_subscription(org["subscription_id"])


@router.post("/portal")
def billing_portal(payload: BillingPortalRequest, claims: dict = Depends(verify_token)):
    """Create a Stripe billing portal session."""
    org_id = claims.get("custom:org_id")
    org = get_org(org_id)
    if not org or not org.get("stripe_customer_id"):
        raise HTTPException(status_code=404, detail="No billing account found")
    url = create_billing_portal(org["stripe_customer_id"], payload.return_url)
    return {"url": url}


@router.get("/usage")
def usage(claims: dict = Depends(verify_token)):
    """Get usage metrics for the current organization."""
    org_id = claims.get("custom:org_id")
    return {"current_month": get_usage(org_id), "history": get_usage_history(org_id)}


@router.post("/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events."""
    payload = await request.body()
    sig = request.headers.get("stripe-signature")
    try:
        event = construct_webhook_event(payload, sig)
    except stripe.error.SignatureVerificationError:
        logger.warning("stripe_webhook_signature_failed")
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    event_type = event["type"]
    obj = event["data"]["object"]

    if event_type == "invoice.payment_succeeded":
        customer_id = obj.get("customer")
        amount = obj.get("amount_paid", 0)
        logger.info("payment_succeeded", extra={"customer_id": customer_id, "amount_cents": amount})

    elif event_type == "invoice.payment_failed":
        customer_id = obj.get("customer")
        logger.warning("payment_failed", extra={"customer_id": customer_id})

    elif event_type == "customer.subscription.deleted":
        subscription_id = obj.get("id")
        customer_id = obj.get("customer")
        logger.info("subscription_deleted", extra={"subscription_id": subscription_id, "customer_id": customer_id})

    elif event_type == "customer.subscription.updated":
        subscription_id = obj.get("id")
        status = obj.get("status")
        logger.info("subscription_updated", extra={"subscription_id": subscription_id, "status": status})

    else:
        logger.debug("unhandled_stripe_event", extra={"event_type": event_type})

    return {"status": "ok"}
