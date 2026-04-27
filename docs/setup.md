# Setup Guide

## Prerequisites
- AWS Account with HIPAA BAA signed
- Python 3.11+
- Node.js 18+
- Terraform 1.5+
- AWS CLI configured

## 1. AWS Setup
```bash
aws configure
# Enter your Access Key, Secret Key, region: us-east-1
```

Enable these AWS services:
- Amazon Bedrock (request Claude 3.5 Sonnet access)
- Amazon Transcribe Medical
- Amazon Comprehend Medical
- Amazon HealthLake

## 2. Infrastructure
```bash
cd infrastructure/terraform
terraform init
terraform apply -var="account_id=YOUR_AWS_ACCOUNT_ID"
```

Copy the outputs — you'll need them for the .env files:
- `healthlake_endpoint`
- `cognito_user_pool_id`
- `cognito_client_id`
- `audio_bucket_name`

## 3. Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
cp .env.example .env         # Fill in values from Terraform outputs
uvicorn main:app --reload
```

API runs at: http://localhost:8000
Swagger docs: http://localhost:8000/docs

## 4. Frontend
```bash
cd frontend
cp .env.example .env         # Fill in Cognito values
npm install
npm run dev
```

App runs at: http://localhost:5173

## 5. API Reference

### Clinical Notes
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/notes/transcribe | Upload audio → SOAP note |
| POST | /api/notes/generate | Text transcript → SOAP note |
| GET  | /api/notes/{patient_id} | List all notes for patient |
| GET  | /api/notes/{patient_id}/{note_id} | Get specific note |
| PUT  | /api/notes/{patient_id}/{note_id} | Update a note |

### Drug Interactions
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/drugs/check | Check drug interactions |
| POST | /api/drugs/extract | Extract meds from text |

### Decision Support
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/decision/suggest | Get AI recommendations |

### EHR / FHIR
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET  | /api/fhir/patient/{id} | Fetch patient from HealthLake |
| POST | /api/fhir/patient | Register new patient |
| POST | /api/fhir/patient/{id}/note | Store note to EHR |
| GET  | /api/fhir/patient/{id}/conditions | Get patient conditions |
| GET  | /api/fhir/patient/{id}/medications | Get patient medications |

## 6. Security & Compliance
- All endpoints require a valid Cognito JWT token
- Data encrypted at rest (AES-256) and in transit (TLS 1.3)
- Full audit trail via AWS CloudTrail
- FHIR R4 compliant via Amazon HealthLake

## 7. Production Deployment

### Prerequisites
- Domain name (e.g. `app.medimind.ai`)
- ACM certificate in `us-east-1` (required for CloudFront)

### Step 1 — Deploy Infrastructure
```bash
cd infrastructure/terraform
terraform apply \
  -var="account_id=YOUR_ACCOUNT_ID" \
  -var="domain_name=app.medimind.ai" \
  -var="acm_certificate_arn=arn:aws:acm:us-east-1:..." \
  -var="alert_email=oncall@yourhospital.com"
```

### Step 2 — Populate Secrets Manager
```bash
aws secretsmanager put-secret-value \
  --secret-id medimind/app-secrets \
  --secret-string '{
    "COGNITO_USER_POOL_ID": "<from-output>",
    "COGNITO_CLIENT_ID": "<from-output>",
    "HEALTHLAKE_ENDPOINT": "<from-output>",
    "SNS_ALERT_TOPIC_ARN": "<from-output>"
  }'
```

### Step 3 — Set GitHub Secrets
In your GitHub repo → Settings → Secrets, add:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_ACCOUNT_ID`
- `CLOUDFRONT_DISTRIBUTION_ID`
- `VITE_API_URL` (e.g. `https://api.medimind.ai`)
- `VITE_WS_URL` (e.g. `wss://api.medimind.ai`)
- `VITE_COGNITO_USER_POOL_ID`
- `VITE_COGNITO_CLIENT_ID`

### Step 4 — Push to Deploy
```bash
git add .
git commit -m "Initial deployment"
git push origin main
```
GitHub Actions will automatically:
1. Build & push Docker image to ECR
2. Deploy new ECS task (zero-downtime rolling update)
3. Build React app & sync to S3
4. Invalidate CloudFront cache

### Architecture
```
Users → CloudFront → S3 (React SPA)
                  → ALB → ECS Fargate (FastAPI)
                              → Bedrock (Claude 3.5)
                              → Transcribe Medical
                              → Comprehend Medical
                              → DynamoDB
                              → HealthLake (FHIR)
                              → SNS (Alerts)
```
