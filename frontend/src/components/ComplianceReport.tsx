import { useState } from "react";
import axios from "axios";

interface ComplianceCheck {
  status: "pass" | "fail";
  detail: string;
}

interface ComplianceStatus {
  status: string;
  checks: Record<string, ComplianceCheck>;
}

export default function ComplianceReport() {
  const [status, setStatus] = useState<ComplianceStatus | null>(null);
  const [report, setReport] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [reportLoading, setReportLoading] = useState(false);

  const loadStatus = async () => {
    setLoading(true);
    try {
      const { data } = await axios.get("/api/compliance/compliance-status");
      setStatus(data);
    } finally {
      setLoading(false);
    }
  };

  const generateReport = async (days: number) => {
    setReportLoading(true);
    try {
      const { data } = await axios.get(`/api/compliance/audit-report?days=${days}`);
      setReport(data);
    } finally {
      setReportLoading(false);
    }
  };

  return (
    <div className="panel">
      <h2>🛡️ HIPAA Compliance</h2>

      <div className="compliance-actions">
        <button onClick={loadStatus} disabled={loading}>
          {loading ? "Checking..." : "Check Compliance Status"}
        </button>
        <button onClick={() => generateReport(30)} disabled={reportLoading} style={{ marginLeft: "0.75rem", background: "#38a169" }}>
          {reportLoading ? "Generating..." : "Generate 30-Day Audit Report"}
        </button>
      </div>

      {status && (
        <div className="compliance-grid">
          {Object.entries(status.checks).map(([key, check]) => (
            <div key={key} className={`compliance-card ${check.status}`}>
              <div className="compliance-header">
                <span className="compliance-icon">{check.status === "pass" ? "✅" : "❌"}</span>
                <strong>{key.replace(/_/g, " ").toUpperCase()}</strong>
              </div>
              <p>{check.detail}</p>
            </div>
          ))}
        </div>
      )}

      {report && (
        <div className="audit-report">
          <h3>Audit Report — {report.report_id}</h3>
          <p className="report-period">Period: {report.period.start.slice(0, 10)} → {report.period.end.slice(0, 10)}</p>
          <div className="report-summary">
            {Object.entries(report.summary).map(([key, val]) => (
              <div key={key} className="report-stat">
                <strong>{String(val)}</strong>
                <span>{key.replace(/_/g, " ")}</span>
              </div>
            ))}
          </div>
          <h4 style={{ margin: "1rem 0 0.5rem" }}>Recent Audit Events ({report.events.length})</h4>
          <div className="audit-events">
            {report.events.slice(0, 10).map((e: any, i: number) => (
              <div key={i} className="audit-event">
                <span className="event-name">{e.event_name}</span>
                <span className="event-user">{e.user}</span>
                <span className="event-time">{new Date(e.event_time).toLocaleString()}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
