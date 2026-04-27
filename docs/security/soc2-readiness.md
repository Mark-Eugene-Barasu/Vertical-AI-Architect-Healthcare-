# MediMind AI — SOC 2 Type II Readiness Checklist

## Trust Service Criteria Coverage

---

## CC1 — Control Environment

| Control | Status | Evidence |
|---------|--------|----------|
| Security policies documented | ✅ | This document + security_scan.py |
| Roles and responsibilities defined | ✅ | Cognito RBAC (admin, clinician, super_admin) |
| Background checks for employees | 🔲 | HR process required |
| Security awareness training | 🔲 | Annual training program required |
| Code of conduct policy | 🔲 | Legal document required |

---

## CC2 — Communication & Information

| Control | Status | Evidence |
|---------|--------|----------|
| Security incident response plan | 🔲 | Document required |
| Vulnerability disclosure policy | 🔲 | security@medimind.ai mailbox |
| Data classification policy | ✅ | PHI tagged in all DynamoDB tables |
| Customer data handling documented | ✅ | HIPAA policy + BAA |

---

## CC3 — Risk Assessment

| Control | Status | Evidence |
|---------|--------|----------|
| Annual risk assessment | 🔲 | Schedule with security firm |
| Threat modeling documented | ✅ | Architecture docs + WAF rules |
| Vendor risk assessment | ✅ | AWS HIPAA BAA, Stripe PCI DSS |
| Penetration testing | 🔲 | Schedule annual pen test |

---

## CC6 — Logical & Physical Access

| Control | Status | Evidence |
|---------|--------|----------|
| MFA enforced for all users | ✅ | Cognito MFA = ON (TOTP) |
| Least privilege access | ✅ | IAM roles scoped per service |
| Access reviews (quarterly) | 🔲 | Process required |
| Session timeout configured | ✅ | Cognito token expiry = 1hr |
| Privileged access monitoring | ✅ | CloudTrail + CloudWatch |
| Offboarding process | ✅ | Cognito admin_disable_user API |

---

## CC7 — System Operations

| Control | Status | Evidence |
|---------|--------|----------|
| Vulnerability scanning | ✅ | security_scan.py + ECR scan on push |
| Patch management process | ✅ | Dependabot + pip-audit in CI/CD |
| Incident detection & alerting | ✅ | CloudWatch alarms + SNS |
| Backup & recovery | ✅ | DynamoDB PITR enabled |
| Disaster recovery plan | 🔲 | Document RTO/RPO targets |
| Change management process | ✅ | GitHub PR reviews + CI/CD gates |

---

## CC8 — Change Management

| Control | Status | Evidence |
|---------|--------|----------|
| Code review required | ✅ | GitHub branch protection rules |
| Automated testing in CI/CD | ✅ | GitHub Actions pipeline |
| Security scan in CI/CD | ✅ | security_scan.py in deploy.yml |
| Rollback capability | ✅ | ECS deployment circuit breaker |
| Staging environment | 🔲 | Create staging AWS account |

---

## CC9 — Risk Mitigation

| Control | Status | Evidence |
|---------|--------|----------|
| Encryption at rest | ✅ | AES-256 on S3, DynamoDB, HealthLake |
| Encryption in transit | ✅ | TLS 1.3 enforced via CloudFront |
| DDoS protection | ✅ | AWS WAF + Shield Standard |
| Rate limiting | ✅ | WAF rate limit: 2000 req/IP/5min |
| Data loss prevention | ✅ | S3 versioning + DynamoDB PITR |

---

## A1 — Availability

| Control | Status | Evidence |
|---------|--------|----------|
| SLA defined (99.9%) | ✅ | Enterprise contracts |
| Multi-AZ deployment | ✅ | ECS across 2 AZs |
| Auto-scaling configured | ✅ | ECS auto-scaling 2-10 tasks |
| Health checks configured | ✅ | ALB health check /health |
| Uptime monitoring | 🔲 | Set up StatusPage.io |

---

## C1 — Confidentiality

| Control | Status | Evidence |
|---------|--------|----------|
| Data classification | ✅ | PHI identified and tagged |
| PHI access logging | ✅ | CloudTrail + audit reports |
| Data retention policy | 🔲 | Define retention periods |
| Secure data deletion | 🔲 | Document deletion procedures |
| NDA for employees | 🔲 | Legal document required |

---

## P — Privacy (HIPAA Alignment)

| Control | Status | Evidence |
|---------|--------|----------|
| BAA with AWS | ✅ | AWS HIPAA BAA signed |
| BAA with customers | ✅ | BAA in enterprise contracts |
| PHI minimization | ✅ | Only necessary PHI stored |
| Patient consent tracking | 🔲 | Consent management system |
| Right to deletion | 🔲 | Data deletion API endpoint |
| Privacy policy published | 🔲 | Legal document required |

---

## Pre-Audit Action Items

### Must Complete Before SOC 2 Audit
1. 🔲 Hire security firm for penetration test
2. 🔲 Document incident response plan
3. 🔲 Create staging environment
4. 🔲 Set up StatusPage.io for uptime monitoring
5. 🔲 Implement quarterly access reviews
6. 🔲 Draft privacy policy, terms of service, data retention policy
7. 🔲 Security awareness training program
8. 🔲 Employee background check process
9. 🔲 Disaster recovery plan with RTO/RPO targets
10. 🔲 Consent management system for PHI

### Recommended Auditors
- Vanta (automated SOC 2 compliance platform)
- Drata (continuous compliance monitoring)
- A-LIGN (SOC 2 audit firm)

### Estimated Timeline
- Months 1-2: Complete action items above
- Month 3: Observation period begins (SOC 2 Type II requires 6 months)
- Month 9: Audit + report issued

### Estimated Cost
- Vanta/Drata platform: ~$15,000/year
- Pen test: ~$20,000
- SOC 2 audit firm: ~$30,000-$50,000
- **Total: ~$65,000-$85,000**
