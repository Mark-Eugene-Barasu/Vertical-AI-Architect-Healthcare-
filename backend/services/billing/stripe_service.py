import stripe
import os

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

PLANS = {
    "starter":    {"price_id": os.getenv("STRIPE_PRICE_STARTER"),    "notes": 500,  "clinicians": 5},
    "growth":     {"price_id": os.getenv("STRIPE_PRICE_GROWTH"),     "notes": 2000, "clinicians": 25},
    "enterprise": {"price_id": os.getenv("STRIPE_PRICE_ENTERPRISE"), "notes": -1,   "clinicians": -1},
}

def create_customer(org_id: str, org_name: str, email: str) -> str:
    customer = stripe.Customer.create(
        email=email,
        name=org_name,
        metadata={"org_id": org_id}
    )
    return customer.id

def create_subscription(customer_id: str, plan: str) -> dict:
    price_id = PLANS[plan]["price_id"]
    sub = stripe.Subscription.create(
        customer=customer_id,
        items=[{"price": price_id}],
        payment_behavior="default_incomplete",
        expand=["latest_invoice.payment_intent"],
    )
    return {
        "subscription_id": sub.id,
        "client_secret": sub.latest_invoice.payment_intent.client_secret,
        "status": sub.status,
    }

def get_subscription(subscription_id: str) -> dict:
    sub = stripe.Subscription.retrieve(subscription_id)
    return {"status": sub.status, "current_period_end": sub.current_period_end}

def cancel_subscription(subscription_id: str) -> dict:
    sub = stripe.Subscription.cancel(subscription_id)
    return {"status": sub.status}

def create_billing_portal(customer_id: str, return_url: str) -> str:
    session = stripe.billing_portal.Session.create(
        customer=customer_id,
        return_url=return_url,
    )
    return session.url

def construct_webhook_event(payload: bytes, sig_header: str) -> stripe.Event:
    return stripe.Webhook.construct_event(
        payload, sig_header, os.getenv("STRIPE_WEBHOOK_SECRET")
    )
