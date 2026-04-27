import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from middleware.request_id import RequestIdMiddleware
from middleware.error_handler import ErrorHandlerMiddleware
from api.notes import router as notes_router
from api.drugs import router as drugs_router
from api.decision_support import router as decision_router
from api.fhir.router import router as fhir_router
from api.alerts.router import router as alerts_router
from api.timeline import router as timeline_router
from api.billing.router import router as billing_router
from api.analytics.router import router as analytics_router
from api.org.router import router as org_router
from api.compliance.router import router as compliance_router
from api.admin.router import router as admin_router

# ── Structured logging ────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s | %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger("medimind")

# ── App ───────────────────────────────────────────────────────────────────────
VERSION = os.getenv("APP_VERSION", "1.1.0")

app = FastAPI(
    title="MediMind AI",
    description="AI Clinical Co-Pilot -- HIPAA-compliant clinical assistant",
    version=VERSION,
    docs_url="/docs" if os.getenv("ENABLE_DOCS", "false").lower() == "true" else None,
    redoc_url=None,
)

# ── Middleware (order matters: outermost first) ───────────────────────────────
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "https://app.medimind.ai,https://medimind.ai",
).split(",")

app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(RequestIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in ALLOWED_ORIGINS],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)

# ── Routes ────────────────────────────────────────────────────────────────────
app.include_router(notes_router,      prefix="/api/notes",      tags=["Clinical Notes"])
app.include_router(drugs_router,      prefix="/api/drugs",      tags=["Drug Interactions"])
app.include_router(decision_router,   prefix="/api/decision",   tags=["Decision Support"])
app.include_router(fhir_router,       prefix="/api/fhir",       tags=["EHR / FHIR"])
app.include_router(alerts_router,     prefix="/api/alerts",     tags=["Real-Time Alerts"])
app.include_router(timeline_router,   prefix="/api/timeline",   tags=["Patient Timeline"])
app.include_router(billing_router,    prefix="/api/billing",    tags=["Billing"])
app.include_router(analytics_router,  prefix="/api/analytics",  tags=["Analytics"])
app.include_router(org_router,        prefix="/api/org",        tags=["Organization"])
app.include_router(compliance_router, prefix="/api/compliance", tags=["Compliance"])
app.include_router(admin_router,      prefix="/api/admin",      tags=["Admin"])


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
def health_check():
    """Basic liveness probe."""
    return {"status": "healthy", "service": "MediMind AI", "version": VERSION}


@app.get("/health/ready", tags=["Health"])
def readiness_check():
    """Readiness probe that checks downstream dependencies."""
    import time
    checks: dict = {}

    # DynamoDB check
    try:
        import boto3
        start = time.monotonic()
        client = boto3.client("dynamodb", region_name=os.getenv("AWS_REGION", "us-east-1"))
        client.describe_table(TableName="medimind-clinical-notes")
        latency = round((time.monotonic() - start) * 1000, 1)
        checks["dynamodb"] = {"status": "ok", "latency_ms": latency}
    except Exception as e:
        checks["dynamodb"] = {"status": "degraded", "error": str(e)}

    overall = "healthy" if all(c["status"] == "ok" for c in checks.values()) else "degraded"
    return {"status": overall, "service": "MediMind AI", "version": VERSION, "dependencies": checks}
