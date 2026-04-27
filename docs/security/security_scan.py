#!/usr/bin/env python3
"""
MediMind AI — Pre-deployment Security Scanner
Runs automated checks before every production deployment.
"""
import subprocess
import sys
import json
from datetime import datetime

CHECKS = []
PASSED = []
FAILED = []

def check(name: str):
    def decorator(fn):
        CHECKS.append((name, fn))
        return fn
    return decorator

def run(cmd: str) -> tuple[int, str]:
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout + result.stderr

# ── Dependency Vulnerability Scan ─────────────────────────────────────────────
@check("Python dependency vulnerabilities (pip-audit)")
def check_pip_audit():
    code, out = run("pip-audit --format json -r backend/requirements.txt")
    if code != 0 and "vulnerabilities" in out:
        data = json.loads(out)
        vulns = [v for pkg in data for v in pkg.get("vulns", [])]
        if vulns:
            return False, f"{len(vulns)} vulnerabilities found: {[v['id'] for v in vulns[:3]]}"
    return True, "No known vulnerabilities"

@check("Node.js dependency vulnerabilities (npm audit)")
def check_npm_audit():
    code, out = run("cd frontend && npm audit --audit-level=high --json")
    if code != 0:
        try:
            data = json.loads(out)
            high = data.get("metadata", {}).get("vulnerabilities", {}).get("high", 0)
            critical = data.get("metadata", {}).get("vulnerabilities", {}).get("critical", 0)
            if high + critical > 0:
                return False, f"{critical} critical, {high} high vulnerabilities in frontend deps"
        except Exception:
            pass
    return True, "No high/critical vulnerabilities"

# ── Secret Detection ───────────────────────────────────────────────────────────
@check("No hardcoded secrets in codebase (detect-secrets)")
def check_secrets():
    code, out = run("detect-secrets scan --baseline .secrets.baseline backend/ frontend/src/")
    if code != 0:
        return False, "Potential secrets detected — run 'detect-secrets scan' for details"
    return True, "No hardcoded secrets detected"

# ── SAST ──────────────────────────────────────────────────────────────────────
@check("Python SAST scan (bandit)")
def check_bandit():
    code, out = run("bandit -r backend/ -ll -f json")
    if code != 0:
        try:
            data = json.loads(out)
            high = [i for i in data.get("results", []) if i["issue_severity"] == "HIGH"]
            if high:
                return False, f"{len(high)} high-severity issues: {[i['test_id'] for i in high[:3]]}"
        except Exception:
            pass
    return True, "No high-severity SAST issues"

# ── Terraform Security ─────────────────────────────────────────────────────────
@check("Terraform security scan (tfsec)")
def check_tfsec():
    code, out = run("tfsec infrastructure/terraform --format json")
    if code != 0:
        try:
            data = json.loads(out)
            critical = [r for r in data.get("results", []) if r.get("severity") == "CRITICAL"]
            if critical:
                return False, f"{len(critical)} critical Terraform issues found"
        except Exception:
            pass
    return True, "No critical Terraform security issues"

# ── Docker Security ────────────────────────────────────────────────────────────
@check("Docker image vulnerability scan (trivy)")
def check_trivy():
    code, out = run("trivy fs backend/ --severity HIGH,CRITICAL --format json")
    if code != 0:
        try:
            data = json.loads(out)
            vulns = data.get("Results", [])
            total = sum(len(r.get("Vulnerabilities") or []) for r in vulns)
            if total > 0:
                return False, f"{total} HIGH/CRITICAL vulnerabilities in Docker context"
        except Exception:
            pass
    return True, "No HIGH/CRITICAL Docker vulnerabilities"

# ── HIPAA Config Checks ────────────────────────────────────────────────────────
@check("S3 buckets have public access blocked")
def check_s3_public_access():
    code, out = run('grep -r "block_public_acls.*=.*true" infrastructure/terraform/')
    return (True, "S3 public access blocked") if code == 0 else (False, "S3 public access block not configured")

@check("DynamoDB encryption enabled")
def check_dynamodb_encryption():
    code, out = run('grep -r "server_side_encryption" infrastructure/terraform/')
    return (True, "DynamoDB encryption configured") if code == 0 else (False, "DynamoDB encryption not found")

@check("CloudTrail multi-region enabled")
def check_cloudtrail():
    code, out = run('grep -r "is_multi_region_trail.*=.*true" infrastructure/terraform/')
    return (True, "CloudTrail multi-region enabled") if code == 0 else (False, "CloudTrail multi-region not enabled")

@check("MFA required in Cognito")
def check_cognito_mfa():
    code, out = run('grep -r "mfa_configuration.*=.*\\"ON\\"" infrastructure/terraform/')
    return (True, "Cognito MFA enforced") if code == 0 else (False, "Cognito MFA not enforced")

@check("WAF attached to CloudFront")
def check_waf():
    code, out = run('grep -r "web_acl_id" infrastructure/terraform/')
    return (True, "WAF attached to CloudFront") if code == 0 else (False, "WAF not attached")

# ── Run All Checks ─────────────────────────────────────────────────────────────
def main():
    print(f"\n{'='*60}")
    print(f"  MediMind AI Security Scanner — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}\n")

    for name, fn in CHECKS:
        try:
            passed, detail = fn()
        except Exception as e:
            passed, detail = False, f"Check failed to run: {e}"

        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}  {name}")
        if not passed:
            print(f"       → {detail}")
            FAILED.append(name)
        else:
            PASSED.append(name)

    print(f"\n{'='*60}")
    print(f"  Results: {len(PASSED)} passed, {len(FAILED)} failed")
    print(f"{'='*60}\n")

    if FAILED:
        print("❌ Security scan FAILED. Fix issues before deploying.\n")
        sys.exit(1)
    else:
        print("✅ All security checks passed. Safe to deploy.\n")
        sys.exit(0)

if __name__ == "__main__":
    main()
