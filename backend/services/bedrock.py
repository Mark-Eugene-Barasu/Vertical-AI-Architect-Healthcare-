import boto3
import json
import os
import re

bedrock = boto3.client("bedrock-runtime", region_name=os.getenv("AWS_REGION", "us-east-1"))
MODEL_ID = "anthropic.claude-3-5-sonnet-20241022-v2:0"

MAX_TRANSCRIPT_CHARS = 8_000
MAX_CONTEXT_CHARS = 4_000
MAX_QUERY_CHARS = 500

def _sanitize(text: str, max_len: int) -> str:
    """Truncate and strip control characters from user input before prompt interpolation."""
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    return text[:max_len]

async def generate_clinical_note(transcript: str, patient_id: str) -> dict:
    """Generate a structured SOAP clinical note from a conversation transcript."""
    safe_transcript = _sanitize(transcript, MAX_TRANSCRIPT_CHARS)
    prompt = (
        "You are a clinical documentation assistant. "
        "Convert the following doctor-patient conversation into a structured SOAP note.\n\n"
        f"Conversation:\n{safe_transcript}\n\n"
        "Return a JSON object with keys: subjective, objective, assessment, plan, follow_up."
    )
    response = _invoke_bedrock(prompt)
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        return {"raw_note": response}

async def get_clinical_decision_support(patient_context: str, query: str) -> str:
    """Provide evidence-based clinical decision support."""
    safe_context = _sanitize(patient_context, MAX_CONTEXT_CHARS)
    safe_query = _sanitize(query, MAX_QUERY_CHARS)
    prompt = (
        "You are a clinical decision support AI assistant. "
        "Based on the patient context below, answer the clinical query with evidence-based recommendations.\n\n"
        f"Patient Context:\n{safe_context}\n\n"
        f"Clinical Query:\n{safe_query}\n\n"
        "Provide concise, actionable recommendations. "
        "Always recommend consulting relevant specialists when appropriate."
    )
    return _invoke_bedrock(prompt)

def _invoke_bedrock(prompt: str) -> str:
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 2048,
        "messages": [{"role": "user", "content": prompt}]
    })
    response = bedrock.invoke_model(modelId=MODEL_ID, body=body)
    result = json.loads(response["body"].read())
    return result["content"][0]["text"]
