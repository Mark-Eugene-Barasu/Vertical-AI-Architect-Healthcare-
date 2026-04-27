# Pushing MediMind AI to GitHub

## 1. Create the GitHub Repository

Go to https://github.com/new and create a **private** repository named `medimind-ai`.
- Visibility: **Private** (HIPAA codebase — never public)
- Do NOT initialize with README, .gitignore, or license (we have our own)

## 2. Initialize Git Locally

```bash
cd "c:\Users\mark0\OneDrive\Desktop\Billion-Dollar Vertical AI Architect"

git init
git add .
git status   # verify no .env or *.tfstate files appear
git commit -m "feat: initial MediMind AI platform"
```

## 3. Verify No Secrets Are Staged

Before pushing, run this check:
```bash
git diff --cached --name-only | grep -E "\.(env|tfstate|pem|key|tfvars)$"
```
This should return nothing. If it returns any files, run `git reset HEAD <file>` on each.

## 4. Connect and Push

```bash
git remote add origin https://github.com/<your-username>/medimind-ai.git
git branch -M main
git push -u origin main
```

## 5. Set GitHub Repository Secrets

Go to: GitHub repo → Settings → Secrets and variables → Actions

Add these secrets for the CI/CD pipeline:
```
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_ACCOUNT_ID
CLOUDFRONT_DISTRIBUTION_ID
VITE_API_URL
VITE_WS_URL
VITE_COGNITO_USER_POOL_ID
VITE_COGNITO_CLIENT_ID
```

## 6. Enable Branch Protection

Go to: Settings → Branches → Add rule for `main`:
- ✅ Require pull request reviews before merging
- ✅ Require status checks to pass (security-scan job)
- ✅ Require branches to be up to date
- ✅ Do not allow bypassing the above settings

## 7. Enable GitHub Security Features

Go to: Settings → Security:
- ✅ Enable Dependabot alerts
- ✅ Enable Dependabot security updates
- ✅ Enable secret scanning
- ✅ Enable code scanning (CodeQL)

## Files Confirmed Safe to Push

| File | Safe? | Reason |
|------|-------|--------|
| backend/.env.example | ✅ | Placeholders only |
| frontend/.env.example | ✅ | Placeholders only |
| mobile/.env.example | ✅ | Placeholders only |
| infrastructure/terraform/terraform.tfvars.example | ✅ | Placeholders only |
| backend/.env | 🚫 | Gitignored |
| infrastructure/terraform/*.tfstate | 🚫 | Gitignored |
| infrastructure/terraform/terraform.tfvars | 🚫 | Gitignored |
| **/.terraform/ | 🚫 | Gitignored |
