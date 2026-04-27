import { useState, useEffect } from "react";

interface ChecklistItem {
  id: string;
  title: string;
  desc: string;
  action?: string;
  actionLabel?: string;
}

const CHECKLIST: ChecklistItem[] = [
  { id: "ehr",      title: "Connect your EHR",           desc: "Link your Epic or Cerner system via FHIR.",         action: "/api/fhir",     actionLabel: "Connect EHR" },
  { id: "note",     title: "Generate your first note",   desc: "Try the AI note generator with a sample transcript.", action: "#notes",        actionLabel: "Try It" },
  { id: "drug",     title: "Run a drug interaction check", desc: "Enter a patient's medications and see it in action.", action: "#drugs",       actionLabel: "Try It" },
  { id: "invite",   title: "Invite a colleague",         desc: "Add another clinician to your organization.",        action: "/api/org",      actionLabel: "Invite" },
  { id: "alert",    title: "Set up alert notifications", desc: "Configure SMS/email alerts for critical events.",    action: "#alerts",       actionLabel: "Configure" },
  { id: "timeline", title: "View a patient timeline",    desc: "See the full history view for any patient.",         action: "#timeline",     actionLabel: "View" },
];

const STORAGE_KEY = "medimind_checklist";

export default function OnboardingChecklist() {
  const [completed, setCompleted] = useState<Set<string>>(() => {
    const saved = localStorage.getItem(STORAGE_KEY);
    return saved ? new Set(JSON.parse(saved)) : new Set();
  });
  const [minimized, setMinimized] = useState(false);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify([...completed]));
  }, [completed]);

  const toggle = (id: string) => {
    setCompleted((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  const progress = Math.round((completed.size / CHECKLIST.length) * 100);
  if (progress === 100) return null; // hide when all done

  return (
    <div className={`checklist-widget ${minimized ? "minimized" : ""}`}>
      <div className="checklist-header" onClick={() => setMinimized(!minimized)}>
        <div className="checklist-title">
          <span>🚀 Getting Started</span>
          <span className="checklist-progress-text">{completed.size}/{CHECKLIST.length}</span>
        </div>
        <div className="checklist-progress-bar">
          <div className="checklist-progress-fill" style={{ width: `${progress}%` }} />
        </div>
        <span className="checklist-toggle">{minimized ? "▲" : "▼"}</span>
      </div>

      {!minimized && (
        <ul className="checklist-items">
          {CHECKLIST.map((item) => (
            <li key={item.id} className={`checklist-item ${completed.has(item.id) ? "done" : ""}`}>
              <button className="checklist-check" onClick={() => toggle(item.id)}>
                {completed.has(item.id) ? "✅" : "⬜"}
              </button>
              <div className="checklist-content">
                <strong>{item.title}</strong>
                <span>{item.desc}</span>
              </div>
              {item.action && !completed.has(item.id) && (
                <a href={item.action} className="checklist-action">{item.actionLabel}</a>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
