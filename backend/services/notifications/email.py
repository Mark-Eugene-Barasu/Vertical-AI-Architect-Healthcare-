import boto3
import os
import html
from datetime import datetime

ses = boto3.client("ses", region_name=os.getenv("AWS_REGION", "us-east-1"))
FROM_EMAIL = os.getenv("SES_FROM_EMAIL", "noreply@medimind.ai")

def _e(value: str) -> str:
    """HTML-escape a user-supplied string before embedding in email HTML."""
    return html.escape(str(value), quote=True)

def _send(to: str, subject: str, body_html: str):
    ses.send_email(
        Source=FROM_EMAIL,
        Destination={"ToAddresses": [to]},
        Message={
            "Subject": {"Data": subject},
            "Body": {"Html": {"Data": body_html}},
        },
    )

def send_welcome_email(to: str, name: str, org_name: str, plan: str):
    _send(to, "Welcome to MediMind AI 🧠", f"""
    <div style="font-family:sans-serif;max-width:600px;margin:0 auto;padding:2rem">
      <h1 style="color:#1a365d">Welcome to MediMind AI, {_e(name)}! 🧠</h1>
      <p>Your <strong>{_e(org_name)}</strong> account is ready on the
         <strong style="color:#2b6cb0;text-transform:capitalize">{_e(plan)}</strong> plan.</p>
      <p>Your 14-day free trial starts today. Here's how to get started:</p>
      <ol style="line-height:2">
        <li>Generate your first clinical note</li>
        <li>Run a drug interaction check</li>
        <li>Connect your EHR via FHIR</li>
        <li>Invite your colleagues</li>
      </ol>
      <a href="https://app.medimind.ai/dashboard"
         style="display:inline-block;background:#2b6cb0;color:white;padding:0.875rem 2rem;border-radius:8px;text-decoration:none;font-weight:700;margin-top:1rem">
        Go to Dashboard →
      </a>
      <p style="color:#718096;font-size:0.85rem;margin-top:2rem">
        Questions? Reply to this email or visit <a href="https://app.medimind.ai">app.medimind.ai</a>
      </p>
    </div>
    """)

def send_trial_expiry_warning(to: str, name: str, days_left: int, plan: str):
    _send(to, f"Your MediMind AI trial ends in {days_left} days", f"""
    <div style="font-family:sans-serif;max-width:600px;margin:0 auto;padding:2rem">
      <h2 style="color:#1a365d">Your free trial ends in {_e(str(days_left))} days</h2>
      <p>Hi {_e(name)}, your 14-day free trial of MediMind AI is almost over.</p>
      <p>To keep saving 15+ hours per week and protecting your patients from drug errors, upgrade now.</p>
      <a href="https://app.medimind.ai/pricing"
         style="display:inline-block;background:#2b6cb0;color:white;padding:0.875rem 2rem;border-radius:8px;text-decoration:none;font-weight:700;margin-top:1rem">
        Upgrade to {_e(plan.capitalize())} →
      </a>
      <p style="color:#718096;font-size:0.85rem;margin-top:2rem">Cancel anytime. No lock-in contracts.</p>
    </div>
    """)

def send_usage_alert(to: str, name: str, usage_pct: int, plan: str):
    _send(to, f"MediMind AI: You've used {usage_pct}% of your monthly notes", f"""
    <div style="font-family:sans-serif;max-width:600px;margin:0 auto;padding:2rem">
      <h2 style="color:#dd6b20">⚠️ You've used {_e(str(usage_pct))}% of your note limit</h2>
      <p>Hi {_e(name)}, your {_e(plan.capitalize())} plan is at {_e(str(usage_pct))}% capacity this month.</p>
      <p>Upgrade now to avoid interruptions or overage charges.</p>
      <a href="https://app.medimind.ai/pricing"
         style="display:inline-block;background:#dd6b20;color:white;padding:0.875rem 2rem;border-radius:8px;text-decoration:none;font-weight:700;margin-top:1rem">
        Upgrade Plan →
      </a>
    </div>
    """)

def send_critical_alert_email(to: str, clinician_name: str, alert: dict):
    _send(to, f"[CRITICAL] Drug Interaction Alert — Patient {_e(alert.get('patient_id', ''))}", f"""
    <div style="font-family:sans-serif;max-width:600px;margin:0 auto;padding:2rem">
      <div style="background:#fff5f5;border-left:4px solid #e53e3e;padding:1rem;border-radius:4px;margin-bottom:1.5rem">
        <h2 style="color:#c53030;margin:0">🚨 Critical Clinical Alert</h2>
      </div>
      <p>Hi Dr. {_e(clinician_name)},</p>
      <p><strong>Patient:</strong> {_e(alert.get('patient_id', ''))}</p>
      <p><strong>Alert Type:</strong> {_e(str(alert.get('alert_type', '')).replace('_', ' '))}</p>
      <p><strong>Message:</strong> {_e(alert.get('message', ''))}</p>
      <p><strong>Time:</strong> {_e(alert.get('timestamp', ''))}</p>
      <a href="https://app.medimind.ai/dashboard"
         style="display:inline-block;background:#e53e3e;color:white;padding:0.875rem 2rem;border-radius:8px;text-decoration:none;font-weight:700;margin-top:1rem">
        View in Dashboard →
      </a>
      <p style="color:#718096;font-size:0.8rem;margin-top:2rem">
        This is an automated alert from MediMind AI. Always apply clinical judgment.
      </p>
    </div>
    """)

def send_monthly_report(to: str, name: str, org_name: str, metrics: dict):
    _send(to, f"MediMind AI Monthly Report — {datetime.now().strftime('%B %Y')}", f"""
    <div style="font-family:sans-serif;max-width:600px;margin:0 auto;padding:2rem">
      <h2 style="color:#1a365d">📊 Your Monthly MediMind AI Report</h2>
      <p>Hi {_e(name)}, here's what MediMind AI did for <strong>{_e(org_name)}</strong> this month:</p>
      <table style="width:100%;border-collapse:collapse;margin:1.5rem 0">
        <tr style="background:#ebf8ff">
          <td style="padding:0.75rem;font-weight:700">Notes Generated</td>
          <td style="padding:0.75rem;text-align:right;font-weight:700;color:#2b6cb0">{_e(str(metrics.get('notes_generated', 0)))}</td>
        </tr>
        <tr>
          <td style="padding:0.75rem">Drug Checks Performed</td>
          <td style="padding:0.75rem;text-align:right">{_e(str(metrics.get('drug_checks_performed', 0)))}</td>
        </tr>
        <tr style="background:#f7fafc">
          <td style="padding:0.75rem">Hours Saved</td>
          <td style="padding:0.75rem;text-align:right;color:#38a169;font-weight:700">{_e(str(metrics.get('estimated_time_saved_hours', 0)))} hrs</td>
        </tr>
        <tr>
          <td style="padding:0.75rem">Errors Prevented</td>
          <td style="padding:0.75rem;text-align:right;color:#e53e3e;font-weight:700">{_e(str(metrics.get('estimated_errors_prevented', 0)))}</td>
        </tr>
      </table>
      <a href="https://app.medimind.ai/dashboard"
         style="display:inline-block;background:#2b6cb0;color:white;padding:0.875rem 2rem;border-radius:8px;text-decoration:none;font-weight:700">
        View Full Analytics →
      </a>
    </div>
    """)
