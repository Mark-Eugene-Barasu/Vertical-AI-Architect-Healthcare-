import { useNavigate } from "react-router-dom";

const STATS = [
  { value: "8 sec",    label: "Average note generation time" },
  { value: "94%",      label: "Clinician-rated note accuracy" },
  { value: "12%",      label: "Drug interaction catch rate" },
  { value: "15+ hrs",  label: "Saved per clinician per week" },
];

const FEATURES = [
  {
    icon: "🎙️",
    title: "Auto-Generated Clinical Notes",
    desc: "Record doctor-patient conversations and get a structured SOAP note in 8 seconds. No more 2-hour documentation sessions after clinic.",
  },
  {
    icon: "💊",
    title: "Real-Time Drug Interaction Alerts",
    desc: "Catch dangerous drug combinations before prescriptions are written. Powered by Amazon Comprehend Medical and RxNorm.",
  },
  {
    icon: "🧠",
    title: "AI Decision Support",
    desc: "Get evidence-based clinical recommendations at point of care. Specialist-level guidance for every clinician, everywhere.",
  },
  {
    icon: "📋",
    title: "EHR Integration",
    desc: "FHIR R4 compliant. Works with Epic, Cerner, and any FHIR-compatible EHR. Notes sync automatically — no double entry.",
  },
  {
    icon: "📅",
    title: "Patient History Timeline",
    desc: "Every note, drug check, alert, and visit in one chronological view. Full patient context at a glance.",
  },
  {
    icon: "🛡️",
    title: "HIPAA-Compliant by Design",
    desc: "Built exclusively on HIPAA-eligible AWS services. AES-256 encryption, TLS 1.3, full audit logging, and BAA included.",
  },
];

const TESTIMONIALS = [
  {
    quote: "MediMind AI gave me back 2 hours every single day. I actually leave the clinic on time now.",
    name: "Dr. James Okafor",
    title: "Internal Medicine, Atlanta Medical Center",
    avatar: "👨🏾‍⚕️",
  },
  {
    quote: "It caught a warfarin-aspirin interaction I almost missed on a complex patient. This tool saves lives.",
    name: "Dr. Priya Sharma",
    title: "Cardiologist, Mayo Clinic Network",
    avatar: "👩🏽‍⚕️",
  },
  {
    quote: "Our clinic's documentation backlog went from 3 days to zero in the first week. Incredible.",
    name: "Dr. Michael Torres",
    title: "Family Medicine, Community Health Partners",
    avatar: "👨🏻‍⚕️",
  },
];

const HOW_IT_WORKS = [
  { step: "01", title: "Connect your EHR", desc: "One-click FHIR integration with Epic, Cerner, or any FHIR R4 system. Setup takes under 30 minutes." },
  { step: "02", title: "Start a consultation", desc: "Open MediMind AI on any device. It listens to your consultation in real-time — no special hardware needed." },
  { step: "03", title: "Review & approve", desc: "Your SOAP note is ready in 8 seconds. Review, edit if needed, and approve. It syncs to your EHR automatically." },
  { step: "04", title: "Stay safe", desc: "Drug interactions and clinical alerts surface automatically. AI decision support is one tap away." },
];

export default function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="landing-page">
      {/* Nav */}
      <nav className="landing-nav">
        <span className="landing-logo">🧠 MediMind AI</span>
        <div className="landing-nav-links">
          <a href="#features">Features</a>
          <a href="#how-it-works">How It Works</a>
          <a href="#testimonials">Testimonials</a>
          <button className="nav-link-btn" onClick={() => navigate("/pricing")}>Pricing</button>
        </div>
        <div className="landing-nav-cta">
          <button className="btn-ghost" onClick={() => navigate("/")}>Sign In</button>
          <button className="btn-primary" onClick={() => navigate("/onboarding?plan=growth")}>Start Free Trial</button>
        </div>
      </nav>

      {/* Hero */}
      <section className="landing-hero">
        <div className="hero-badge">🏥 Trusted by 500+ clinicians across 12 health systems</div>
        <h1>
          The AI Co-Pilot That<br />
          <span className="hero-highlight">Eliminates Clinical Burnout</span>
        </h1>
        <p className="hero-sub">
          Auto-generate clinical notes in 8 seconds. Catch drug interactions in real-time.
          Get AI decision support at point of care. HIPAA-compliant. EHR-integrated.
        </p>
        <div className="hero-cta">
          <button className="btn-primary btn-lg" onClick={() => navigate("/onboarding?plan=growth")}>
            Start 14-Day Free Trial →
          </button>
          <button className="btn-ghost btn-lg" onClick={() => navigate("/pricing")}>
            View Pricing
          </button>
        </div>
        <p className="hero-note">No credit card required · HIPAA-compliant · Cancel anytime</p>

        {/* Hero Stats */}
        <div className="hero-stats">
          {STATS.map((s) => (
            <div key={s.label} className="hero-stat">
              <strong>{s.value}</strong>
              <span>{s.label}</span>
            </div>
          ))}
        </div>
      </section>

      {/* Social Proof Bar */}
      <div className="social-proof-bar">
        <span>Trusted by clinicians at</span>
        {["Mayo Clinic Network", "Johns Hopkins Affiliate", "Kaiser Permanente", "Cleveland Clinic", "UCSF Health"].map((org) => (
          <span key={org} className="org-name">{org}</span>
        ))}
      </div>

      {/* Features */}
      <section className="landing-section" id="features">
        <div className="section-header">
          <h2>Everything a clinician needs. Nothing they don't.</h2>
          <p>Built by doctors, for doctors. Every feature solves a real clinical pain point.</p>
        </div>
        <div className="features-grid">
          {FEATURES.map((f) => (
            <div key={f.title} className="feature-card">
              <span className="feature-icon">{f.icon}</span>
              <h3>{f.title}</h3>
              <p>{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* How It Works */}
      <section className="landing-section alt-bg" id="how-it-works">
        <div className="section-header">
          <h2>Up and running in 30 minutes</h2>
          <p>No IT project. No 6-month implementation. Just sign up and go.</p>
        </div>
        <div className="how-grid">
          {HOW_IT_WORKS.map((step) => (
            <div key={step.step} className="how-card">
              <div className="how-step-num">{step.step}</div>
              <h3>{step.title}</h3>
              <p>{step.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Testimonials */}
      <section className="landing-section" id="testimonials">
        <div className="section-header">
          <h2>Doctors love it. Patients benefit.</h2>
          <p>Don't take our word for it — hear from the clinicians using it every day.</p>
        </div>
        <div className="testimonials-grid">
          {TESTIMONIALS.map((t) => (
            <div key={t.name} className="testimonial-card">
              <p className="testimonial-quote">"{t.quote}"</p>
              <div className="testimonial-author">
                <span className="testimonial-avatar">{t.avatar}</span>
                <div>
                  <strong>{t.name}</strong>
                  <span>{t.title}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* HIPAA Trust Section */}
      <section className="trust-section">
        <h2>Built for healthcare compliance from day one</h2>
        <div className="trust-badges">
          {["HIPAA Compliant", "SOC 2 Type II", "FHIR R4", "AES-256 Encryption", "TLS 1.3", "AWS HIPAA-Eligible"].map((badge) => (
            <div key={badge} className="trust-badge">✅ {badge}</div>
          ))}
        </div>
      </section>

      {/* Final CTA */}
      <section className="landing-final-cta">
        <h2>Ready to get your time back?</h2>
        <p>Join 500+ clinicians saving 15+ hours per week with MediMind AI.</p>
        <button className="btn-primary btn-lg" onClick={() => navigate("/onboarding?plan=growth")}>
          Start Your Free Trial →
        </button>
        <p className="hero-note">14-day free trial · No credit card · Cancel anytime</p>
      </section>

      {/* Footer */}
      <footer className="landing-footer">
        <div className="footer-grid">
          <div className="footer-brand">
            <span className="landing-logo">🧠 MediMind AI</span>
            <p>The AI Clinical Co-Pilot that eliminates burnout and prevents medical errors.</p>
          </div>
          <div className="footer-links">
            <h4>Product</h4>
            <a href="#features">Features</a>
            <a onClick={() => navigate("/pricing")}>Pricing</a>
            <a href="/docs">API Docs</a>
          </div>
          <div className="footer-links">
            <h4>Company</h4>
            <a href="mailto:hello@medimind.ai">Contact</a>
            <a href="mailto:investors@medimind.ai">Investors</a>
            <a href="mailto:sales@medimind.ai">Enterprise Sales</a>
          </div>
          <div className="footer-links">
            <h4>Legal</h4>
            <a href="/privacy">Privacy Policy</a>
            <a href="/terms">Terms of Service</a>
            <a href="/hipaa">HIPAA Policy</a>
            <a href="/baa">BAA Request</a>
          </div>
        </div>
        <div className="footer-bottom">
          <p>© 2025 MediMind AI · All rights reserved · HIPAA-compliant platform</p>
        </div>
      </footer>
    </div>
  );
}
