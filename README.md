# 🧠 MediMind AI — Clinical Co-Pilot

> A production-grade, HIPAA-compliant AI platform that eliminates clinical burnout and prevents medical errors — built entirely on AWS.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![HIPAA Compliant](https://img.shields.io/badge/HIPAA-Compliant-green.svg)](docs/security/soc2-readiness.md)
[![AWS](https://img.shields.io/badge/Cloud-AWS-orange.svg)](infrastructure/terraform)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](backend)
[![React](https://img.shields.io/badge/Frontend-React%20%2B%20TypeScript-61DAFB.svg)](frontend)

---

## 🩺 The Problem

- **63%** of US physicians report burnout — documentation is the #1 cause
- Doctors spend **50%+ of their time on paperwork**, not patients
- Medical errors are the **3rd leading cause of death** in the US — 250,000 deaths/year
- Drug interaction errors kill **125,000 Americans annually** — most are preventable
- **4.5 billion people** have no access to specialist-level care

## 💡 The Solution

MediMind AI is an AI Clinical Co-Pilot that sits at the point of care and handles the cognitive overhead that burns doctors out — so they can focus entirely on their patients.

---

## ✨ Features

### 🎙️ AI Clinical Note Generation
- Records and transcribes doctor-patient conversations using **Amazon Transcribe Medical**
- Generates structured **SOAP notes** (Subjective, Objective, Assessment, Plan, Follow-up) in under 10 seconds
- Supports both audio upload and raw text transcript input
- Notes are saved to DynamoDB and synced to the patient's EHR via FHIR
- Full edit and update support — clinicians always stay in control

### 💊 Real-Time Drug Interaction Checker
- Extracts medication entities from clinical text using **Amazon Comprehend Medical**
- Cross-references against **RxNorm** codes to identify known interactions
- Flags high-risk drug combinations (warfarin + aspirin, SSRIs + MAOIs, digoxin + amiodarone, and more)
- Automatically triggers real-time alerts when dangerous interactions are detected
- Logs every drug check to the patient's history timeline

### 🧠 AI Decision Support
- Provides evidence-based clinical recommendations at point of care
- Powered by **Claude 3.5 Sonnet** via **Amazon Bedrock**
- Accepts patient context and clinical queries in natural language
- Returns concise, actionable recommendations with specialist referral guidance
- Input sanitized and length-capped to prevent prompt injection

### 🚨 Real-Time Clinical Alerts
- WebSocket-based alert delivery — clinicians receive alerts instantly without refreshing
- Origin-validated WebSocket connections (no unauthorized cross-origin access)
- Alert severity levels: CRITICAL, HIGH, MEDIUM, INFO
- Critical and High alerts also published to **Amazon SNS** for email/SMS delivery
- Alert types: Drug Interaction, Abnormal Vitals, Critical Lab, Allergy Conflict, Dosage Error
- Full alert history stored in the patient timeline

### 📅 Patient History Timeline
- Chronological event log for every patient
- Automatically populated by note generation, drug checks, and alerts
- Supports manual event logging (visits, diagnoses, lab results, medications)
- Filterable by event type
- Visual timeline UI with color-coded event icons

### 🏥 EHR Integration (FHIR R4)
- Full **FHIR R4** compliance via **Amazon HealthLake**
- Patient registration, retrieval, conditions, and medications
- Clinical notes stored as FHIR DocumentReference resources
- Compatible with Epic, Cerner, and any FHIR R4-compliant EHR system
- SigV4-signed requests with connection timeouts and SSL verification

### 🔐 Authentication & Multi-Tenancy
- **Amazon Cognito** with enforced TOTP MFA for all clinician accounts
- JWT tokens fully validated — signature, expiry, issuer, audience, and token_use
- Role-based access control: `clinician`, `admin`, `super_admin`
- Complete org-level data isolation — no cross-tenant data leakage
- Clinician invite/disable flow managed via Cognito admin APIs

### 📊 Analytics Dashboard
- Per-organization monthly metrics: notes generated, drug checks, decisions, transcriptions
- Estimated time saved and errors prevented per month
- 6-month usage trend chart (up to 24 months)
- Alert summary breakdown by severity
- All metrics scoped to the authenticated organization

### 🛡️ HIPAA Compliance & Audit Reports
- Auto-generated HIPAA audit reports from **AWS CloudTrail** events
- Tracks PHI access, writes, and deletions across S3 and DynamoDB
- Compliance status dashboard with 8 real-time checks
- Full SOC 2 Type II readiness checklist included (`docs/security/soc2-readiness.md`)
- Automated security scanner with 10 pre-deployment checks (`docs/security/security_scan.py`)

### 💳 Billing & Subscriptions
- **Stripe**-powered subscription management
- Three plans: Starter ($499/mo), Growth ($1,499/mo), Enterprise (custom)
- Usage tracking per organization per month
- Stripe Customer Portal for self-serve billing management
- Webhook handling for payment events with structured audit logging
- Trial expiry and usage alert email sequences via **Amazon SES**

### 🏢 Admin Portal
- Super admin dashboard for platform-wide management
- Organization overview: total orgs, active orgs, MRR, ARR
- Plan distribution visualization
- Per-org status and plan override controls
- Sensitive billing fields stripped from all admin responses

### 📱 Mobile App (React Native / Expo)
- iOS and Android support via **Expo**
- Cognito authentication with secure token storage
- Audio recording and SOAP note generation at bedside
- Drug interaction checker on mobile
- Shares the same backend API as the web app

### 🌐 Marketing & Onboarding
- Full public-facing **landing page** with hero, features, testimonials, and trust badges
- **Pricing page** with monthly/annual toggle, ROI calculator, and FAQ
- **5-step onboarding flow**: account creation → org setup → email verification → billing → dashboard
- In-app **onboarding checklist** with progress tracking (persisted in localStorage)
- Floating **Help Center** with searchable FAQ articles
- Contextual **Tooltip** component for in-app guidance

### 📧 Notification System
- Welcome email on signup
- Trial expiry warnings at 7, 3, and 1 day remaining
- Usage alerts at 80% and 95% of plan limit
- Critical clinical alert emails with patient context
- Monthly summary reports with key metrics
- All emails HTML-escaped to prevent injection attacks
- Scheduled via **AWS EventBridge** + **AWS Lambda** (daily + monthly triggers)

### 🚀 Production Infrastructure (Terraform)
- **VPC** with public/private subnets across 2 Availability Zones
- **ECS Fargate** with auto-scaling (2–10 tasks), deployment circuit breaker, and rollback
- **Application Load Balancer** with TLS 1.3, HTTP→HTTPS redirect
- **CloudFront** CDN for the React frontend with WAF protection
- **AWS WAF** with OWASP Common Rule Set and IP-based rate limiting (2,000 req/5min)
- **Amazon ECR** with immutable image tags and scan-on-push
- **IAM** least-privilege policies — every action scoped to specific resource ARNs
- **AWS Secrets Manager** for all runtime secrets (no env vars in task definitions)
- **CloudWatch** log groups with 90-day retention
- **DynamoDB** tables with encryption at rest and Point-in-Time Recovery
- **Amazon HealthLake** FHIR R4 datastore with AWS-managed KMS encryption
- **SNS** alert topic with KMS encryption
- **SES** email identity for transactional emails

### ⚙️ CI/CD Pipeline (GitHub Actions)
- Security scan gate — deployment blocked if any check fails
- Docker image build, tag with commit SHA, and push to ECR
- Zero-downtime ECS rolling deployment with stability wait
- React app build with environment variable injection
- S3 sync with correct cache headers (`immutable` for assets, `no-cache` for `index.html`)
- CloudFront cache invalidation on every deploy

---

## 🏗️ Architecture

```
                        ┌─────────────────────────────────┐
                        │     CloudFront + WAF (CDN)       │
                        │   DDoS Protection + OWASP Rules  │
                        └────────────┬────────────────────┘
                                     │
               ┌─────────────────────┴──────────────────────┐
               │                                            │
       ┌───────▼────────┐                        ┌──────────▼──────────┐
       │  React + TS    │                        │   FastAPI Backend   │
       │  (S3 + CDN)    │                        │   (ECS Fargate)     │
       └────────────────┘                        └──────────┬──────────┘
                                                            │
              ┌─────────────────────────────────────────────┤
              │              │              │               │
   ┌──────────▼──┐  ┌────────▼───┐  ┌──────▼──────┐  ┌────▼──────────┐
   │   Bedrock   │  │ Transcribe │  │  Comprehend  │  │  HealthLake   │
   │ Claude 3.5  │  │  Medical   │  │   Medical    │  │   FHIR R4     │
   └─────────────┘  └────────────┘  └─────────────┘  └───────────────┘
              │
   ┌──────────┴──────────────────────────────────────────────────────┐
   │  DynamoDB  │  Cognito  │  SNS  │  SES  │  S3  │  CloudTrail    │
   └────────────┴───────────┴───────┴───────┴──────┴────────────────┘
```

---

## 📁 Project Structure

```
medimind-ai/
├── backend/                        # FastAPI backend
│   ├── api/
│   │   ├── admin/                  # Super admin endpoints
│   │   ├── alerts/                 # WebSocket + REST alert endpoints
│   │   ├── analytics/              # Metrics and usage trend endpoints
│   │   ├── billing/                # Stripe subscription + webhook endpoints
│   │   ├── compliance/             # HIPAA audit report endpoints
│   │   ├── fhir/                   # EHR / FHIR R4 endpoints
│   │   ├── org/                    # Organization + clinician management
│   │   ├── decision_support.py     # AI decision support endpoint
│   │   ├── drugs.py                # Drug interaction endpoints
│   │   ├── notes.py                # Clinical note endpoints
│   │   └── timeline.py             # Patient timeline endpoints
│   ├── auth/
│   │   ├── cognito.py              # JWT verification middleware
│   │   └── tenant.py               # Multi-tenancy + RBAC middleware
│   ├── db/
│   │   ├── notes_repository.py     # DynamoDB CRUD for clinical notes
│   │   ├── org_repository.py       # DynamoDB CRUD for organizations
│   │   └── timeline_repository.py  # DynamoDB CRUD for patient timeline
│   ├── services/
│   │   ├── alerts/                 # WebSocket manager + SNS publisher
│   │   ├── analytics/              # Metrics aggregation service
│   │   ├── billing/                # Stripe + usage tracking services
│   │   ├── compliance/             # CloudTrail audit service
│   │   ├── notifications/          # SES email templates + Lambda scheduler
│   │   ├── bedrock.py              # Amazon Bedrock (Claude 3.5) integration
│   │   ├── comprehend_medical.py   # Amazon Comprehend Medical integration
│   │   ├── fhir.py                 # Amazon HealthLake FHIR integration
│   │   └── transcribe.py           # Amazon Transcribe Medical integration
│   ├── Dockerfile
│   ├── main.py                     # FastAPI app entry point
│   └── requirements.txt
│
├── frontend/                       # React + TypeScript web app
│   └── src/
│       ├── components/
│       │   ├── onboarding/         # Checklist, Tooltip, HelpCenter
│       │   ├── AlertBanner.tsx     # Real-time alert display
│       │   ├── AnalyticsDashboard.tsx
│       │   ├── ComplianceReport.tsx
│       │   ├── DecisionSupport.tsx
│       │   ├── DrugChecker.tsx
│       │   ├── NoteGenerator.tsx
│       │   └── PatientTimeline.tsx
│       ├── hooks/
│       │   └── useAlerts.ts        # WebSocket alert subscription hook
│       ├── pages/
│       │   ├── admin/              # Super admin portal
│       │   ├── marketing/          # Landing page + pricing page
│       │   ├── Dashboard.tsx       # Main clinician dashboard
│       │   ├── Login.tsx
│       │   └── OnboardingPage.tsx  # 5-step onboarding flow
│       └── services/
│           ├── api.ts              # Typed API client with auto-auth
│           └── auth.ts             # Amplify auth configuration
│
├── mobile/                         # React Native (Expo) mobile app
│   └── src/
│       ├── screens/
│       │   ├── LoginScreen.tsx
│       │   ├── NoteScreen.tsx      # Audio recording + note generation
│       │   └── DrugScreen.tsx      # Drug interaction checker
│       └── services/
│           └── api.ts
│
├── infrastructure/
│   └── terraform/
│       ├── main.tf                 # S3, DynamoDB, Cognito, CloudTrail
│       ├── ecs.tf                  # VPC, ECR, ECS, ALB, IAM, auto-scaling
│       ├── cloudfront.tf           # CloudFront, WAF, S3 frontend hosting
│       ├── healthlake.tf           # Amazon HealthLake FHIR datastore
│       ├── sns_dynamodb.tf         # SNS alerts + patient timeline table
│       ├── tables.tf               # Usage + organizations DynamoDB tables
│       ├── notifications.tf        # SES, Lambda, EventBridge schedules
│       └── variables.tf
│
├── docs/
│   ├── api/
│   │   └── api-reference.md        # Full API reference for all endpoints
│   ├── pitch-deck/
│   │   ├── pitch-deck.md           # 14-slide investor pitch deck
│   │   └── executive-summary.md    # One-page investor summary
│   ├── security/
│   │   ├── security_scan.py        # Automated pre-deployment security scanner
│   │   └── soc2-readiness.md       # SOC 2 Type II readiness checklist
│   ├── github-push.md              # Step-by-step GitHub push guide
│   └── setup.md                    # Full local + production setup guide
│
├── .github/
│   └── workflows/
│       └── deploy.yml              # CI/CD: security scan → ECS + S3/CloudFront
│
├── .gitignore                      # Blocks secrets, tfstate, node_modules
└── README.md
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Cloud | AWS (HIPAA-eligible) |
| AI — Note Generation | Amazon Bedrock (Claude 3.5 Sonnet) |
| AI — Transcription | Amazon Transcribe Medical |
| AI — Drug Extraction | Amazon Comprehend Medical (RxNorm) |
| Backend | Python 3.11, FastAPI, Uvicorn |
| Frontend | React 18, TypeScript, Vite |
| Mobile | React Native, Expo |
| Auth | Amazon Cognito (MFA enforced) |
| Database | Amazon DynamoDB (encrypted + PITR) |
| EHR / FHIR | Amazon HealthLake (FHIR R4) |
| Alerts | WebSocket + Amazon SNS |
| Email | Amazon SES |
| Billing | Stripe |
| Infrastructure | Terraform |
| Container Registry | Amazon ECR (immutable tags) |
| Compute | Amazon ECS Fargate (auto-scaling) |
| CDN | Amazon CloudFront + WAF |
| Secrets | AWS Secrets Manager |
| Audit Logging | AWS CloudTrail |
| Scheduling | AWS EventBridge + Lambda |
| CI/CD | GitHub Actions |

---

## 🔒 Security

- **JWT validation** — signature, expiry, issuer, audience, and token_use all verified
- **Input sanitization** — all user inputs sanitized and length-capped before AI/AWS calls
- **HTML escaping** — all user values escaped in email templates
- **SSRF protection** — transcript URIs validated before fetch
- **File upload validation** — MIME type allowlist + 25MB size cap on audio uploads
- **WebSocket origin validation** — unauthorized origins rejected with code 1008
- **IAM least privilege** — every action scoped to specific resource ARNs
- **ECR immutable tags** — prevents silent image overwrites
- **WAF** — OWASP Common Rule Set + IP rate limiting
- **Encryption at rest** — AES-256 on all S3 buckets, DynamoDB tables, and HealthLake
- **Encryption in transit** — TLS 1.3 enforced end-to-end
- **MFA** — TOTP enforced for all clinician accounts via Cognito
- **Secrets** — all runtime secrets in AWS Secrets Manager, never in code or env vars
- **Audit trail** — full CloudTrail logging with HIPAA event tracking

---

## 🚀 Getting Started

### Prerequisites
- AWS Account with HIPAA BAA signed
- Python 3.11+
- Node.js 18+
- Terraform 1.5+
- AWS CLI configured (`aws configure`)

### 1. Deploy Infrastructure
```bash
cd infrastructure/terraform
cp terraform.tfvars.example terraform.tfvars   # fill in your values
terraform init
terraform apply
```

Copy the outputs — you'll need them for the next steps:
- `healthlake_endpoint`
- `cognito_user_pool_id`
- `cognito_client_id`
- `sns_alert_topic_arn`
- `alb_dns_name`
- `cloudfront_domain`

### 2. Populate Secrets Manager
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

### 3. Run the Backend Locally
```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS/Linux
pip install -r requirements.txt
cp .env.example .env           # fill in values
uvicorn main:app --reload
```

- API: http://localhost:8000
- Swagger docs: http://localhost:8000/docs

### 4. Run the Frontend Locally
```bash
cd frontend
cp .env.example .env           # fill in Cognito values
npm install
npm run dev
```

- App: http://localhost:5173

### 5. Run the Mobile App
```bash
cd mobile
cp .env.example .env
npm install
npx expo start
```

### 6. Deploy to Production
Push to `main` — GitHub Actions handles everything:
```bash
git add .
git commit -m "deploy"
git push origin main
```

See [docs/github-push.md](docs/github-push.md) for the full GitHub setup guide.

---

## 📡 API Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/notes/generate` | Text transcript → SOAP note |
| POST | `/api/notes/transcribe` | Audio file → SOAP note |
| GET | `/api/notes/{patient_id}` | List all notes for a patient |
| PUT | `/api/notes/{patient_id}/{note_id}` | Update a note |
| POST | `/api/drugs/check` | Check drug interactions |
| POST | `/api/drugs/extract` | Extract medications from text |
| POST | `/api/decision/suggest` | Get AI clinical recommendations |
| GET | `/api/fhir/patient/{id}` | Fetch patient from HealthLake |
| POST | `/api/fhir/patient/{id}/note` | Store note to EHR |
| WS | `/api/alerts/ws/{clinician_id}` | Real-time alert WebSocket |
| GET | `/api/timeline/{patient_id}` | Get patient history timeline |
| GET | `/api/analytics/metrics` | Get org usage metrics |
| GET | `/api/compliance/audit-report` | Generate HIPAA audit report |
| POST | `/api/billing/subscribe` | Subscribe to a plan |
| GET | `/api/admin/overview` | Platform-wide admin metrics |

Full API reference: [docs/api/api-reference.md](docs/api/api-reference.md)

---

## 📊 Business Model

| Plan | Price | Clinicians | Notes/Month |
|------|-------|-----------|-------------|
| Starter | $499/mo | Up to 5 | 500 |
| Growth | $1,499/mo | Up to 25 | 2,000 |
| Enterprise | Custom | Unlimited | Unlimited |

- **LTV:CAC ratio**: 37:1
- **Gross margin**: 82%
- **Payback period**: 1.6 months
- **TAM**: $50B+ (clinical documentation + AI in healthcare)

Investor materials: [docs/pitch-deck/pitch-deck.md](docs/pitch-deck/pitch-deck.md)

---

## 📋 Compliance

| Standard | Status |
|----------|--------|
| HIPAA | ✅ AWS BAA + HIPAA-eligible services only |
| Encryption at rest | ✅ AES-256 on all data stores |
| Encryption in transit | ✅ TLS 1.3 enforced end-to-end |
| MFA | ✅ TOTP enforced via Cognito |
| Audit logging | ✅ CloudTrail multi-region trail |
| Data backup | ✅ DynamoDB PITR on all tables |
| WAF / DDoS | ✅ AWS WAF + Shield Standard |
| SOC 2 Type II | 🔲 Readiness checklist in [docs/security/soc2-readiness.md](docs/security/soc2-readiness.md) |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'feat: add your feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request — the security scan must pass before merging

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 📬 Contact

- 🌐 Website: [medimind.ai](https://medimind.ai)
- 📧 General: hello@medimind.ai
- 💼 Investors: investors@medimind.ai
- 🏥 Enterprise Sales: sales@medimind.ai
- 🛠️ API Support: api-support@medimind.ai

---

<div align="center">
  <strong>Built with ❤️ to save lives and give doctors their time back.</strong>
</div>
