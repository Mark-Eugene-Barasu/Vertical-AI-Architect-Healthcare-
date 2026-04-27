import logging
import os
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from auth.cognito import verify_token
from services.alerts import build_alert, publish_sns_alert, alert_manager, AlertSeverity, AlertType
from models.requests import AlertTriggerRequest, DrugInteractionAlertRequest
from models.responses import AlertTriggerResponse, DrugInteractionAlertResponse

router = APIRouter()
logger = logging.getLogger("medimind.alerts")

ALLOWED_ORIGINS = set(
    os.getenv("ALLOWED_ORIGINS", "https://app.medimind.ai,https://medimind.ai").split(",")
)


@router.websocket("/ws/{clinician_id}")
async def alerts_websocket(clinician_id: str, websocket: WebSocket):
    """WebSocket endpoint -- clinician connects to receive real-time alerts."""
    origin = websocket.headers.get("origin", "")
    if origin not in ALLOWED_ORIGINS:
        await websocket.close(code=1008)  # Policy Violation
        return
    await alert_manager.connect(clinician_id, websocket)
    logger.info("websocket_connected", extra={"clinician_id": clinician_id})
    try:
        while True:
            await websocket.receive_text()  # keep connection alive (ping/pong)
    except WebSocketDisconnect:
        alert_manager.disconnect(clinician_id)
        logger.info("websocket_disconnected", extra={"clinician_id": clinician_id})


@router.post("/trigger", response_model=AlertTriggerResponse)
async def trigger_alert(
    payload: AlertTriggerRequest,
    claims: dict = Depends(verify_token),
):
    """Manually trigger a clinical alert (e.g. from drug check or vitals monitor)."""
    alert = build_alert(
        alert_type=AlertType(payload.alert_type),
        severity=AlertSeverity(payload.severity),
        patient_id=payload.patient_id,
        clinician_id=claims["sub"],
        message=payload.message,
        details=payload.details,
    )

    await alert_manager.send_alert(claims["sub"], alert)
    publish_sns_alert(alert)
    logger.info("alert_triggered", extra={"alert_type": payload.alert_type, "severity": payload.severity})
    return {"status": "alert_sent", "alert": alert}


@router.post("/drug-interaction", response_model=DrugInteractionAlertResponse)
async def alert_drug_interaction(
    payload: DrugInteractionAlertRequest,
    claims: dict = Depends(verify_token),
):
    """Auto-trigger alert when a drug interaction is detected."""
    for interaction in payload.interactions:
        severity = AlertSeverity.CRITICAL if interaction["severity"] == "HIGH" else AlertSeverity.MEDIUM
        alert = build_alert(
            alert_type=AlertType.DRUG_INTERACTION,
            severity=severity,
            patient_id=payload.patient_id,
            clinician_id=claims["sub"],
            message=interaction["warning"],
            details={"drugs": interaction["drugs"]},
        )
        await alert_manager.send_alert(claims["sub"], alert)
        publish_sns_alert(alert)

    logger.info("drug_interaction_alerts_sent", extra={"count": len(payload.interactions)})
    return {"status": "alerts_sent", "count": len(payload.interactions)}
