import boto3
import json
import os
import requests

REGION = os.getenv("AWS_REGION", "us-east-1")
HEALTHLAKE_ENDPOINT = os.getenv("HEALTHLAKE_ENDPOINT")

session = boto3.Session(region_name=REGION)
credentials = session.get_credentials()

FHIR_TIMEOUT = (5, 30)  # (connect timeout, read timeout) in seconds

def _signed_request(method: str, path: str, body: dict = None) -> dict:
    """Make a SigV4-signed request to Amazon HealthLake."""
    from botocore.auth import SigV4Auth
    from botocore.awsrequest import AWSRequest

    url = f"{HEALTHLAKE_ENDPOINT}/r4/{path}"
    data = json.dumps(body) if body else None
    headers = {"Content-Type": "application/fhir+json"}

    request = AWSRequest(method=method, url=url, data=data, headers=headers)
    SigV4Auth(credentials, "healthlake", REGION).add_auth(request)

    response = requests.request(
        method, url,
        headers=dict(request.headers),
        data=data,
        timeout=FHIR_TIMEOUT,
        verify=True,
    )
    response.raise_for_status()
    return response.json()

def get_patient(patient_id: str) -> dict:
    return _signed_request("GET", f"Patient/{patient_id}")

def create_patient(name: str, dob: str, gender: str) -> dict:
    resource = {
        "resourceType": "Patient",
        "name": [{"use": "official", "text": name}],
        "birthDate": dob,
        "gender": gender,
    }
    return _signed_request("POST", "Patient", resource)

def create_clinical_note_document(patient_id: str, note_text: str, clinician_id: str) -> dict:
    """Store a clinical note as a FHIR DocumentReference."""
    import base64
    resource = {
        "resourceType": "DocumentReference",
        "status": "current",
        "type": {"coding": [{"system": "http://loinc.org", "code": "11506-3", "display": "Progress note"}]},
        "subject": {"reference": f"Patient/{patient_id}"},
        "author": [{"reference": f"Practitioner/{clinician_id}"}],
        "content": [{
            "attachment": {
                "contentType": "text/plain",
                "data": base64.b64encode(note_text.encode()).decode(),
            }
        }],
    }
    return _signed_request("POST", "DocumentReference", resource)

def get_patient_conditions(patient_id: str) -> dict:
    return _signed_request("GET", f"Condition?patient={patient_id}")

def get_patient_medications(patient_id: str) -> dict:
    return _signed_request("GET", f"MedicationRequest?patient={patient_id}")
