from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends
from auth.cognito import verify_token
from services.alerts import build_alert, publish_sns_alert, alert_manager, AlertSeverity, AlertType

router = APIRouter()

ALLOWED_ORIGINS = {"https://app.medimind.ai", "https://medimind.ai"}

@router.websocket("/ws/{clinician_id}")
async def alerts_websocket(clinician_id: str, websocket: WebSocket):
    """WebSocket endpoint — clinician connects to receive real-time alerts."""
    origin = websocket.headers.get("origin", "")
    if origin not in ALLOWED_ORIGINS:
        await websocket.close(code=1008)  # Policy Violation
        return
    await alert_manager.connect(clinician_id, websocket)
    try:
        while True:
            await websocket.receive_text()  # keep connection alive (ping/pong)
    except WebSocketDisconnect:
        alert_manager.disconnect(clinician_id)

@router.post("/trigger")
async def trigger_alert(payload: dict, claims: dict = Depends(verify_token)):
    """Manually trigger a clinical alert (e.g. from drug check or vitals monitor)."""
    required = ["alert_type", "severity", "patient_id", "message"]
    if not all(payload.get(k) for k in required):
        raise HTTPException(status_code=400, detail=f"Required fields: {required}")

    alert = build_alert(
        alert_type=AlertType(payload["alert_type"]),
        severity=AlertSeverity(payload["severity"]),
        patient_id=payload["patient_id"],
        clinician_id=claims["sub"],
        message=payload["message"],
        details=payload.get("details", {}),
    )

    await alert_manager.send_alert(claims["sub"], alert)
    publish_sns_alert(alert)
    return {"status": "alert_sent", "alert": alert}

@router.post("/drug-interaction")
async def alert_drug_interaction(payload: dict, claims: dict = Depends(verify_token)):
    """Auto-trigger alert when a drug interaction is detected."""
    interactions = payload.get("interactions", [])
    patient_id = payload.get("patient_id", "")

    for interaction in interactions:
        severity = AlertSeverity.CRITICAL if interaction["severity"] == "HIGH" else AlertSeverity.MEDIUM
        alert = build_alert(
            alert_type=AlertType.DRUG_INTERACTION,
            severity=severity,
            patient_id=patient_id,
            clinician_id=claims["sub"],
            message=interaction["warning"],
            details={"drugs": interaction["drugs"]},
        )
        await alert_manager.send_alert(claims["sub"], alert)
        publish_sns_alert(alert)

    return {"status": "alerts_sent", "count": len(interactions)}
