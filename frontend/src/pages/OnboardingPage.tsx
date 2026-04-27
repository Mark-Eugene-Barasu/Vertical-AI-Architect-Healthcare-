import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { signUp, confirmSignUp } from "aws-amplify/auth";
import axios from "axios";

type Step = "account" | "org" | "verify" | "billing" | "done";

const STEPS: Step[] = ["account", "org", "verify", "billing", "done"];
const STEP_LABELS = ["Account", "Organization", "Verify Email", "Billing", "Done"];

export default function OnboardingPage() {
  const [step, setStep] = useState<Step>("account");
  const [searchParams] = useSearchParams();
  const plan = searchParams.get("plan") || "starter";
  const navigate = useNavigate();

  const [form, setForm] = useState({
    email: "", password: "", confirmPassword: "",
    orgName: "", orgType: "clinic", phone: "",
    verificationCode: "",
    cardComplete: false,
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [clientSecret, setClientSecret] = useState("");

  const set = (key: string, val: string) => setForm((f) => ({ ...f, [key]: val }));
  const stepIndex = STEPS.indexOf(step);

  const handleAccount = async () => {
    if (!form.email || !form.password) return setError("Email and password are required");
    if (form.password !== form.confirmPassword) return setError("Passwords do not match");
    if (form.password.length < 12) return setError("Password must be at least 12 characters");
    setLoading(true); setError("");
    try {
      await signUp({
        username: form.email,
        password: form.password,
        options: { userAttributes: { email: form.email } },
      });
      setStep("org");
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleOrg = async () => {
    if (!form.orgName) return setError("Organization name is required");
    setLoading(true); setError("");
    try {
      await axios.post("/api/org/register", {
        name: form.orgName,
        email: form.email,
        admin_email: form.email,
        org_type: form.orgType,
        phone: form.phone,
      });
      setStep("verify");
    } catch (e: any) {
      setError(e.response?.data?.detail || "Failed to create organization");
    } finally {
      setLoading(false);
    }
  };

  const handleVerify = async () => {
    if (!form.verificationCode) return setError("Verification code is required");
    setLoading(true); setError("");
    try {
      await confirmSignUp({ username: form.email, confirmationCode: form.verificationCode });
      const { data } = await axios.post("/api/billing/subscribe", { plan });
      setClientSecret(data.client_secret);
      setStep("billing");
    } catch (e: any) {
      setError(e.message || "Verification failed");
    } finally {
      setLoading(false);
    }
  };

  const handleBilling = async () => {
    // In production, use Stripe.js to confirm payment with clientSecret
    setStep("done");
  };

  return (
    <div className="onboarding-page">
      <div className="onboarding-card">
        <div className="onboarding-logo">🧠 MediMind AI</div>

        {/* Progress Steps */}
        <div className="onboarding-steps">
          {STEP_LABELS.map((label, i) => (
            <div key={label} className={`onboarding-step ${i <= stepIndex ? "active" : ""} ${i < stepIndex ? "done" : ""}`}>
              <div className="step-circle">{i < stepIndex ? "✓" : i + 1}</div>
              <span>{label}</span>
            </div>
          ))}
        </div>

        {error && <p className="error">{error}</p>}

        {/* Step: Account */}
        {step === "account" && (
          <div className="onboarding-form">
            <h2>Create your account</h2>
            <p className="step-desc">Start your 14-day free trial. No credit card required.</p>
            <input placeholder="Work email" type="email" value={form.email} onChange={(e) => set("email", e.target.value)} />
            <input placeholder="Password (min 12 characters)" type="password" value={form.password} onChange={(e) => set("password", e.target.value)} />
            <input placeholder="Confirm password" type="password" value={form.confirmPassword} onChange={(e) => set("confirmPassword", e.target.value)} />
            <button onClick={handleAccount} disabled={loading}>{loading ? "Creating account..." : "Continue →"}</button>
          </div>
        )}

        {/* Step: Organization */}
        {step === "org" && (
          <div className="onboarding-form">
            <h2>Tell us about your organization</h2>
            <p className="step-desc">This helps us configure MediMind AI for your specific needs.</p>
            <input placeholder="Organization name (e.g. City General Hospital)" value={form.orgName} onChange={(e) => set("orgName", e.target.value)} />
            <select value={form.orgType} onChange={(e) => set("orgType", e.target.value)}>
              <option value="clinic">Private Clinic</option>
              <option value="hospital">Hospital</option>
              <option value="health_system">Health System</option>
              <option value="telehealth">Telehealth Provider</option>
              <option value="specialty">Specialty Practice</option>
            </select>
            <input placeholder="Phone number (optional)" value={form.phone} onChange={(e) => set("phone", e.target.value)} />
            <button onClick={handleOrg} disabled={loading}>{loading ? "Setting up..." : "Continue →"}</button>
          </div>
        )}

        {/* Step: Verify */}
        {step === "verify" && (
          <div className="onboarding-form">
            <h2>Verify your email</h2>
            <p className="step-desc">We sent a 6-digit code to <strong>{form.email}</strong></p>
            <input
              placeholder="Enter verification code"
              value={form.verificationCode}
              onChange={(e) => set("verificationCode", e.target.value)}
              maxLength={6}
              style={{ letterSpacing: "0.3em", textAlign: "center", fontSize: "1.5rem" }}
            />
            <button onClick={handleVerify} disabled={loading}>{loading ? "Verifying..." : "Verify & Continue →"}</button>
          </div>
        )}

        {/* Step: Billing */}
        {step === "billing" && (
          <div className="onboarding-form">
            <h2>Start your free trial</h2>
            <p className="step-desc">
              You're signing up for the <strong style={{ textTransform: "capitalize" }}>{plan}</strong> plan.
              Your 14-day free trial starts today — no charge until {new Date(Date.now() + 14 * 86400000).toLocaleDateString()}.
            </p>
            <div className="billing-notice">
              <span>🔒</span>
              <span>Payment info is securely processed by Stripe. MediMind AI never stores your card details.</span>
            </div>
            {/* In production: mount Stripe Elements here using clientSecret */}
            <div className="stripe-placeholder">
              <p>💳 Stripe payment form loads here</p>
              <small>Integrate with <code>@stripe/react-stripe-js</code> using the clientSecret</small>
            </div>
            <button onClick={handleBilling} disabled={loading}>{loading ? "Processing..." : "Start Free Trial →"}</button>
          </div>
        )}

        {/* Step: Done */}
        {step === "done" && (
          <div className="onboarding-done">
            <div className="done-icon">🎉</div>
            <h2>You're all set!</h2>
            <p>Welcome to MediMind AI. Your account is ready.</p>
            <div className="done-checklist">
              <div className="done-item">✅ Account created</div>
              <div className="done-item">✅ Organization configured</div>
              <div className="done-item">✅ Email verified</div>
              <div className="done-item">✅ 14-day free trial started</div>
            </div>
            <button onClick={() => navigate("/dashboard")}>Go to Dashboard →</button>
            <p className="done-hint">Need help getting started? <a href="mailto:support@medimind.ai">Contact support</a></p>
          </div>
        )}
      </div>
    </div>
  );
}
