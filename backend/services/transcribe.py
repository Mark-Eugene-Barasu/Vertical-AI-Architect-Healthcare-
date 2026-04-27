import boto3
import uuid
import os
import asyncio
import urllib.request
import json
from fastapi import HTTPException

s3 = boto3.client("s3", region_name=os.getenv("AWS_REGION", "us-east-1"))
transcribe = boto3.client("transcribemed", region_name=os.getenv("AWS_REGION", "us-east-1"))

BUCKET_NAME = os.getenv("TRANSCRIBE_BUCKET")
ALLOWED_CONTENT_TYPES = {"audio/wav", "audio/wave", "audio/mpeg", "audio/mp4", "audio/webm"}
MAX_AUDIO_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB

async def transcribe_audio(audio_file) -> str:
    """Upload audio to S3 and transcribe using Amazon Transcribe Medical."""
    # Validate file type
    content_type = audio_file.content_type or ""
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid audio format. Allowed: {ALLOWED_CONTENT_TYPES}")

    content = await audio_file.read()

    # Validate file size
    if len(content) > MAX_AUDIO_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="Audio file exceeds 25MB limit")

    job_name = f"medimind-{uuid.uuid4()}"
    s3_key = f"audio/{job_name}.wav"

    s3.put_object(Bucket=BUCKET_NAME, Key=s3_key, Body=content)

    transcribe.start_medical_transcription_job(
        MedicalTranscriptionJobName=job_name,
        Media={"MediaFileUri": f"s3://{BUCKET_NAME}/{s3_key}"},
        MediaFormat="wav",
        LanguageCode="en-US",
        Specialty="PRIMARYCARE",
        Type="CONVERSATION",
        OutputBucketName=BUCKET_NAME,
    )

    return await _poll_transcription(job_name)

async def _poll_transcription(job_name: str) -> str:
    """Poll until transcription job completes and return transcript text."""
    for _ in range(60):
        await asyncio.sleep(5)
        response = transcribe.get_medical_transcription_job(MedicalTranscriptionJobName=job_name)
        status = response["MedicalTranscriptionJob"]["TranscriptionJobStatus"]
        if status == "COMPLETED":
            transcript_uri = response["MedicalTranscriptionJob"]["Transcript"]["TranscriptFileUri"]
            return _fetch_transcript(transcript_uri)
        if status == "FAILED":
            raise Exception("Transcription job failed")
    raise Exception("Transcription timed out")

def _fetch_transcript(uri: str) -> str:
    # SSRF guard — only allow S3 presigned URLs
    if not uri.startswith("https://s3.") and not uri.startswith("https://s3-"):
        raise ValueError(f"Unexpected transcript URI origin: {uri}")
    with urllib.request.urlopen(uri, timeout=30) as r:  # nosec B310 — URI validated above
        data = json.loads(r.read())
    return data["results"]["transcripts"][0]["transcript"]
