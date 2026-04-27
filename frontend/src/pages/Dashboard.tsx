import { useState, useEffect } from "react";
import { signOut, getCurrentUser } from "aws-amplify/auth";
import { useNavigate } from "react-router-dom";
import NoteGenerator from "../components/NoteGenerator";
import DrugChecker from "../components/DrugChecker";
import DecisionSupport from "../components/DecisionSupport";
import PatientTimeline from "../components/PatientTimeline";
import AlertBanner from "../components/AlertBanner";
import AnalyticsDashboard from "../components/AnalyticsDashboard";
import ComplianceReport from "../components/ComplianceReport";
import { useAlerts } from "../hooks/useAlerts";

type Tab = "notes" | "drugs" | "decision" | "timeline" | "analytics" | "compliance";

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState<Tab>("notes");
  const [clinicianId, setClinicianId] = useState("");
  const navigate = useNavigate();
  const { alerts, dismissAlert } = useAlerts(clinicianId);

  useEffect(() => {
    getCurrentUser().then((user) => setClinicianId(user.userId));
  }, []);

  const tabs: { key: Tab; label: string }[] = [
    { key: "notes",      label: "🎙️ Notes" },
    { key: "drugs",      label: "💊 Drugs" },
    { key: "decision",   label: "🧠 Decision" },
    { key: "timeline",   label: "📅 Timeline" },
    { key: "analytics",  label: "📊 Analytics" },
    { key: "compliance", label: "🛡️ Compliance" },
  ];

  return (
    <div className="dashboard">
      <header>
        <h1>🧠 MediMind AI</h1>
        <div className="header-right">
          {alerts.length > 0 && (
            <span className="alert-badge">{alerts.length} Alert{alerts.length > 1 ? "s" : ""}</span>
          )}
          <button onClick={() => signOut().then(() => navigate("/"))}>Sign Out</button>
        </div>
      </header>

      <AlertBanner alerts={alerts} onDismiss={dismissAlert} />

      <nav>
        {tabs.map((tab) => (
          <button key={tab.key} className={activeTab === tab.key ? "active" : ""} onClick={() => setActiveTab(tab.key)}>
            {tab.label}
          </button>
        ))}
      </nav>

      <main>
        {activeTab === "notes"      && <NoteGenerator />}
        {activeTab === "drugs"      && <DrugChecker />}
        {activeTab === "decision"   && <DecisionSupport />}
        {activeTab === "timeline"   && <PatientTimeline />}
        {activeTab === "analytics"  && <AnalyticsDashboard />}
        {activeTab === "compliance" && <ComplianceReport />}
      </main>
    </div>
  );
}
