# MediMind AI — API Documentation

**Base URL:** `https://api.medimind.ai`
**Version:** v1.0
**Auth:** Bearer token (Cognito JWT) — include in all requests:
```
Authorization: Bearer <your-jwt-token>
```

---

## Authentication

### Get a Token
```bash
POST https://cognito-idp.us-east-1.amazonaws.com/
Content-Type: application/x-amz-json-1.1
X-Amz-Target: AWSCognitoIdentityProviderService.InitiateAuth

{
  "AuthFlow": "USER_PASSWORD_AUTH",
  "ClientId": "<your-client-id>",
  "AuthParameters": {
    "USERNAME": "clinician@hospital.com",
    "PASSWORD": "your-password"
  }
}
```

**Response:**
```json
{
  "AuthenticationResult": {
    "IdToken": "eyJhbGci...",
    "AccessToken": "eyJhbGci...",
    "ExpiresIn": 3600
  }
}
```

Use the `IdToken` as your Bearer token.

---

## Clinical Notes

### Generate Note from Transcript
```
POST /api/notes/generate
```
**Request:**
```json
{
  "transcript": "Doctor: How are you feeling today? Patient: I have chest pain...",
  "patient_id": "PAT-001"
}
```
**Response:**
```json
{
  "patient_id": "PAT-001",
  "note_id": "uuid-here",
  "clinical_note": {
    "subjective": "Patient presents with chest pain...",
    "objective": "Vitals stable. BP 130/85...",
    "assessment": "Possible angina. Rule out ACS...",
    "plan": "Order ECG, troponin levels...",
    "follow_up": "Return in 48 hours or sooner if symptoms worsen"
  }
}
```

### Transcribe Audio + Generate Note
```
POST /api/notes/transcribe
Content-Type: multipart/form-data
```
**Form fields:** `audio` (WAV file), `patient_id` (string)

### List Patient Notes
```
GET /api/notes/{patient_id}
```

### Get Specific Note
```
GET /api/notes/{patient_id}/{note_id}
```

### Update Note
```
PUT /api/notes/{patient_id}/{note_id}
```
```json
{ "clinical_note": { "subjective": "Updated text..." } }
```

---

## Drug Interactions

### Check Interactions
```
POST /api/drugs/check
```
```json
{
  "clinical_text": "Patient is on warfarin 5mg and aspirin 81mg",
  "patient_id": "PAT-001"
}
```
**Response:**
```json
{
  "medications": ["warfarin", "aspirin"],
  "interactions": [
    {
      "severity": "HIGH",
      "drugs": ["warfarin", "aspirin"],
      "warning": "Potential interaction between warfarin and aspirin. Review dosing carefully."
    }
  ]
}
```

### Extract Medications from Text
```
POST /api/drugs/extract
```
```json
{ "text": "Patient takes metformin 500mg twice daily and lisinopril 10mg" }
```

---

## Decision Support

### Get AI Recommendations
```
POST /api/decision/suggest
```
```json
{
  "patient_context": "68-year-old male, hypertension, diabetes type 2, eGFR 45",
  "query": "What is the recommended first-line antihypertensive?"
}
```
**Response:**
```json
{
  "query": "What is the recommended first-line antihypertensive?",
  "suggestions": "For a patient with hypertension, diabetes, and CKD (eGFR 45), ACE inhibitors or ARBs are the recommended first-line agents per JNC 8 and ADA guidelines..."
}
```

---

## EHR / FHIR Integration

### Get Patient (FHIR)
```
GET /api/fhir/patient/{patient_id}
```

### Register Patient
```
POST /api/fhir/patient
```
```json
{ "name": "John Smith", "dob": "1956-03-15", "gender": "male" }
```

### Store Note to EHR
```
POST /api/fhir/patient/{patient_id}/note
```
```json
{ "note_text": "SOAP note content here..." }
```

### Get Patient Conditions
```
GET /api/fhir/patient/{patient_id}/conditions
```

### Get Patient Medications
```
GET /api/fhir/patient/{patient_id}/medications
```

---

## Patient Timeline

### Get Timeline
```
GET /api/timeline/{patient_id}?limit=50
```

### Get Timeline by Event Type
```
GET /api/timeline/{patient_id}/{event_type}
```
Event types: `NOTE`, `DRUG_CHECK`, `ALERT`, `DIAGNOSIS`, `MEDICATION`, `LAB_RESULT`, `VISIT`

### Add Timeline Event
```
POST /api/timeline/{patient_id}/event
```
```json
{
  "event_type": "VISIT",
  "title": "Annual physical examination",
  "data": { "visit_type": "annual", "location": "Main Clinic" }
}
```

---

## Real-Time Alerts

### WebSocket Connection
```
WS wss://api.medimind.ai/api/alerts/ws/{clinician_id}
```
Connect to receive real-time alerts. Messages are JSON:
```json
{
  "alert_type": "DRUG_INTERACTION",
  "severity": "CRITICAL",
  "patient_id": "PAT-001",
  "message": "Potential interaction between warfarin and aspirin",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

### Trigger Manual Alert
```
POST /api/alerts/trigger
```
```json
{
  "alert_type": "ABNORMAL_VITALS",
  "severity": "HIGH",
  "patient_id": "PAT-001",
  "message": "BP 180/110 — hypertensive urgency"
}
```

---

## Analytics

### Get Org Metrics
```
GET /api/analytics/metrics
```

### Get Usage Trend
```
GET /api/analytics/trend?months=6
```

---

## Compliance

### Get Compliance Status
```
GET /api/compliance/compliance-status
```

### Generate Audit Report
```
GET /api/compliance/audit-report?days=30
```

---

## Error Codes

| Code | Meaning |
|------|---------|
| 400 | Bad Request — missing or invalid parameters |
| 401 | Unauthorized — invalid or expired JWT token |
| 403 | Forbidden — insufficient permissions |
| 404 | Not Found — resource does not exist |
| 429 | Rate Limited — slow down requests |
| 500 | Internal Server Error — contact support |

---

## Rate Limits

| Endpoint | Limit |
|----------|-------|
| Note generation | 60 req/min per org |
| Drug checks | 120 req/min per org |
| Decision support | 30 req/min per org |
| All other endpoints | 300 req/min per org |

---

## SDKs & Integration Examples

### Python
```python
import requests

BASE_URL = "https://api.medimind.ai"
TOKEN = "your-jwt-token"
headers = {"Authorization": f"Bearer {TOKEN}"}

# Generate a clinical note
response = requests.post(f"{BASE_URL}/api/notes/generate", headers=headers, json={
    "transcript": "Doctor: How are you? Patient: I have a headache...",
    "patient_id": "PAT-001"
})
note = response.json()
print(note["clinical_note"]["assessment"])
```

### JavaScript
```javascript
const BASE_URL = "https://api.medimind.ai";
const token = "your-jwt-token";

const response = await fetch(`${BASE_URL}/api/drugs/check`, {
  method: "POST",
  headers: { "Authorization": `Bearer ${token}`, "Content-Type": "application/json" },
  body: JSON.stringify({ clinical_text: "Patient on warfarin and aspirin", patient_id: "PAT-001" })
});
const { interactions } = await response.json();
```

### FHIR Webhook Integration
For EHR systems that push FHIR resources to MediMind AI, configure your FHIR server to POST to:
```
POST https://api.medimind.ai/api/fhir/webhook
Authorization: Bearer <service-account-token>
Content-Type: application/fhir+json
```

---

## Support
- 📧 Technical support: api-support@medimind.ai
- 📖 Interactive docs (Swagger): https://api.medimind.ai/docs
- 🔔 Status page: https://status.medimind.ai
