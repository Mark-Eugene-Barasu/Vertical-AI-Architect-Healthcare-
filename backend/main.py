from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

app = FastAPI(
    title="MediMind AI",
    description="AI Clinical Co-Pilot — HIPAA-compliant clinical assistant",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.medimind.ai", "https://medimind.ai"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "MediMind AI"}
