import { useState } from "react";

const ARTICLES = [
  {
    category: "Getting Started",
    items: [
      { title: "How to generate your first clinical note", content: "Navigate to the 🎙️ Clinical Notes tab. Enter a Patient ID, paste or type a doctor-patient conversation transcript, then click 'Generate SOAP Note'. Your structured note will appear in seconds." },
      { title: "Connecting your EHR via FHIR", content: "Go to Settings → EHR Integration. Enter your FHIR endpoint URL (e.g. https://your-ehr.com/fhir/r4). MediMind AI supports Epic, Cerner, and any FHIR R4 compliant system." },
      { title: "Inviting clinicians to your organization", content: "Go to Settings → Team. Click 'Invite Clinician', enter their work email and role. They'll receive an email with setup instructions." },
    ],
  },
  {
    category: "Clinical Notes",
    items: [
      { title: "What is a SOAP note?", content: "SOAP stands for Subjective, Objective, Assessment, and Plan. It's the standard clinical documentation format used by physicians worldwide. MediMind AI generates all four sections automatically." },
      { title: "How accurate are AI-generated notes?", content: "Our beta clinicians rate note accuracy at 94%. Notes are generated as a starting point — always review and edit before finalizing. You are always in control." },
      { title: "Can I edit a generated note?", content: "Yes. After generation, click any section to edit inline. Changes are saved automatically to DynamoDB and synced to your EHR." },
    ],
  },
  {
    category: "Drug Interactions",
    items: [
      { title: "How does drug interaction checking work?", content: "We use Amazon Comprehend Medical to extract medication entities from clinical text, then cross-reference against RxNorm codes to identify known interactions. High-risk pairs trigger real-time alerts." },
      { title: "What drug pairs are flagged?", content: "We flag clinically significant interactions including warfarin+aspirin, SSRIs+MAOIs, digoxin+amiodarone, and metformin+contrast dye, among others. The list is continuously updated." },
    ],
  },
  {
    category: "Billing & Plans",
    items: [
      { title: "How do I upgrade my plan?", content: "Go to Settings → Billing → Upgrade Plan. Changes take effect immediately. You'll be charged the prorated difference for the current billing period." },
      { title: "What happens when I hit my note limit?", content: "You'll receive an email alert at 80% usage. At 100%, additional notes are billed at $0.50 each, or you can upgrade your plan to avoid overages." },
      { title: "How do I cancel?", content: "Go to Settings → Billing → Cancel Subscription. Your access continues until the end of the current billing period. No data is deleted for 90 days after cancellation." },
    ],
  },
];

export default function HelpCenter() {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState("");
  const [expanded, setExpanded] = useState<string | null>(null);

  const filtered = ARTICLES.map((cat) => ({
    ...cat,
    items: cat.items.filter(
      (item) =>
        item.title.toLowerCase().includes(search.toLowerCase()) ||
        item.content.toLowerCase().includes(search.toLowerCase())
    ),
  })).filter((cat) => cat.items.length > 0);

  return (
    <>
      <button className="help-fab" onClick={() => setOpen(!open)} title="Help Center">
        {open ? "✕" : "?"}
      </button>

      {open && (
        <div className="help-panel">
          <div className="help-header">
            <h3>📚 Help Center</h3>
            <input
              placeholder="Search articles..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="help-search"
            />
          </div>
          <div className="help-articles">
            {filtered.map((cat) => (
              <div key={cat.category}>
                <div className="help-category">{cat.category}</div>
                {cat.items.map((item) => (
                  <div key={item.title} className="help-article">
                    <button
                      className="help-article-title"
                      onClick={() => setExpanded(expanded === item.title ? null : item.title)}
                    >
                      <span>{item.title}</span>
                      <span>{expanded === item.title ? "−" : "+"}</span>
                    </button>
                    {expanded === item.title && (
                      <p className="help-article-content">{item.content}</p>
                    )}
                  </div>
                ))}
              </div>
            ))}
            {filtered.length === 0 && (
              <div className="help-empty">
                <p>No articles found.</p>
                <a href="mailto:support@medimind.ai">Contact support →</a>
              </div>
            )}
          </div>
          <div className="help-footer">
            <a href="mailto:support@medimind.ai">📧 Email Support</a>
            <a href="https://docs.medimind.ai" target="_blank">📖 Full Docs</a>
          </div>
        </div>
      )}
    </>
  );
}
