import { useState } from "react";
import { useNavigate } from "react-router-dom";

const PLANS = [
  {
    name: "Starter",
    price: { monthly: 499, annual: 399 },
    description: "Perfect for small clinics getting started with AI documentation.",
    features: [
      "Up to 5 clinicians",
      "500 AI-generated notes/month",
      "Drug interaction checker",
      "Basic decision support",
      "Email support",
      "HIPAA-compliant storage",
    ],
    cta: "Start Free Trial",
    highlight: false,
    plan_key: "starter",
  },
  {
    name: "Growth",
    price: { monthly: 1499, annual: 1199 },
    description: "For growing practices that need more power and integrations.",
    features: [
      "Up to 25 clinicians",
      "2,000 AI-generated notes/month",
      "Drug interaction checker",
      "Advanced decision support",
      "EHR integration (FHIR R4)",
      "Real-time alerts & SMS",
      "Patient history timeline",
      "Analytics dashboard",
      "Priority support",
    ],
    cta: "Start Free Trial",
    highlight: true,
    plan_key: "growth",
  },
  {
    name: "Enterprise",
    price: { monthly: null, annual: null },
    description: "For hospital systems and large health networks.",
    features: [
      "Unlimited clinicians",
      "Unlimited AI notes",
      "Full EHR integration suite",
      "Custom AI model fine-tuning",
      "Multi-site deployment",
      "HIPAA audit reports",
      "Dedicated success manager",
      "SLA guarantee (99.9% uptime)",
      "Custom contracts & BAA",
    ],
    cta: "Contact Sales",
    highlight: false,
    plan_key: "enterprise",
  },
];

const FAQS = [
  { q: "Is MediMind AI HIPAA compliant?", a: "Yes. We run exclusively on HIPAA-eligible AWS services, sign a Business Associate Agreement (BAA) with every customer, and enforce end-to-end encryption (AES-256 at rest, TLS 1.3 in transit)." },
  { q: "Can I try it before paying?", a: "Absolutely. Every plan includes a 14-day free trial with no credit card required." },
  { q: "How does EHR integration work?", a: "We use FHIR R4 APIs via Amazon HealthLake, compatible with Epic, Cerner, and any FHIR-compliant EHR system." },
  { q: "What happens if I exceed my note limit?", a: "You'll receive an alert at 80% usage. Overages are billed at $0.50 per note, or you can upgrade your plan at any time." },
  { q: "Can I cancel anytime?", a: "Yes. No lock-in contracts on Starter and Growth plans. Cancel anytime from your billing portal." },
];

export default function PricingPage() {
  const [annual, setAnnual] = useState(false);
  const navigate = useNavigate();

  const handleCTA = (plan: typeof PLANS[0]) => {
    if (plan.plan_key === "enterprise") {
      window.location.href = "mailto:sales@medimind.ai?subject=Enterprise Inquiry";
    } else {
      navigate(`/onboarding?plan=${plan.plan_key}`);
    }
  };

  return (
    <div className="marketing-page">
      {/* Header */}
      <header className="marketing-header">
        <div className="marketing-nav">
          <span className="marketing-logo">🧠 MediMind AI</span>
          <button className="nav-signin" onClick={() => navigate("/")}>Sign In</button>
        </div>
      </header>

      {/* Hero */}
      <section className="pricing-hero">
        <h1>Simple, Transparent Pricing</h1>
        <p>Save 15+ hours per clinician per week. Pay a fraction of what you save.</p>
        <div className="billing-toggle">
          <span className={!annual ? "active" : ""}>Monthly</span>
          <div className={`toggle ${annual ? "on" : ""}`} onClick={() => setAnnual(!annual)} />
          <span className={annual ? "active" : ""}>Annual <span className="save-badge">Save 20%</span></span>
        </div>
      </section>

      {/* Plans */}
      <section className="plans-grid">
        {PLANS.map((plan) => (
          <div key={plan.name} className={`plan-card ${plan.highlight ? "highlighted" : ""}`}>
            {plan.highlight && <div className="popular-badge">Most Popular</div>}
            <h2>{plan.name}</h2>
            <p className="plan-desc">{plan.description}</p>
            <div className="plan-price">
              {plan.price.monthly ? (
                <>
                  <span className="price-amount">${annual ? plan.price.annual : plan.price.monthly}</span>
                  <span className="price-period">/month</span>
                  {annual && <div className="annual-note">billed annually</div>}
                </>
              ) : (
                <span className="price-custom">Custom Pricing</span>
              )}
            </div>
            <button
              className={`plan-cta ${plan.highlight ? "cta-primary" : "cta-secondary"}`}
              onClick={() => handleCTA(plan)}
            >
              {plan.cta}
            </button>
            <ul className="feature-list">
              {plan.features.map((f) => (
                <li key={f}><span className="check">✓</span>{f}</li>
              ))}
            </ul>
          </div>
        ))}
      </section>

      {/* ROI Calculator */}
      <section className="roi-section">
        <h2>💰 ROI Calculator</h2>
        <p>A clinic with 10 clinicians saves an average of:</p>
        <div className="roi-grid">
          <div className="roi-card"><strong>150 hrs</strong><span>Saved per week</span></div>
          <div className="roi-card"><strong>$312,000</strong><span>Annual labor savings</span></div>
          <div className="roi-card"><strong>1,440</strong><span>Errors prevented/year</span></div>
          <div className="roi-card"><strong>47x</strong><span>Return on investment</span></div>
        </div>
      </section>

      {/* FAQ */}
      <section className="faq-section">
        <h2>Frequently Asked Questions</h2>
        <div className="faq-list">
          {FAQS.map((faq) => (
            <FAQItem key={faq.q} q={faq.q} a={faq.a} />
          ))}
        </div>
      </section>

      {/* CTA Banner */}
      <section className="cta-banner">
        <h2>Ready to eliminate clinical burnout?</h2>
        <p>Join 500+ clinicians already using MediMind AI</p>
        <button onClick={() => navigate("/onboarding?plan=growth")}>Start Your Free Trial →</button>
      </section>

      <footer className="marketing-footer">
        <p>© 2025 MediMind AI · HIPAA Compliant · SOC 2 Type II · <a href="mailto:support@medimind.ai">support@medimind.ai</a></p>
      </footer>
    </div>
  );
}

function FAQItem({ q, a }: { q: string; a: string }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="faq-item" onClick={() => setOpen(!open)}>
      <div className="faq-question">
        <span>{q}</span>
        <span>{open ? "−" : "+"}</span>
      </div>
      {open && <p className="faq-answer">{a}</p>}
    </div>
  );
}
