import { useState } from "react";
import { complianceApi } from "../services/api";
import type { ComplianceStatus, AuditReport } from "../types";

export default function ComplianceReport() {
  const [status, setStatus] = useState<ComplianceStatus | null>(null);
  const [report, setReport] = useState<AuditReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [reportLoading, setReportLoading] = useState(false);
  const [error, setError] = useState("");

  const loadStatus = async () => {
    setLoading(true);
    setError("");
    try {
      const { data } = await complianceApi.status();
      setStatus(data);
    } catch {
      setError("Failed to load compliance status.");
    } finally {
      setLoading(false);
    }
  };

  const generateReport = async (days: number) => {
    setReportLoading(true);
    setError("");
    try {
      const { data } = await complianceApi.auditReport(days);
      setReport(data);
    } catch {
      setError("Failed to generate audit report.");
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
        <button
          onClick={() => generateReport(30)}
          disabled={reportLoading}
          style={{ marginLeft: "0.75rem", background: "#38a169" }}
        >
          {reportLoading ? "Generating..." : "Generate 30-Day Audit Report"}
        </button>
      </div>

      {error && <p className="error" role="alert">{error}</p>}

      {status && (
        <div className="compliance-grid" role="list" aria-label="Compliance checks">
          {Object.entries(status.checks).map(([key, check]) => (
            <div key={key} className={`compliance-card ${check.status}`} role="listitem">
              <div className="compliance-header">
                <span className="compliance-icon" aria-hidden="true">
                  {check.status === "pass" ? "✅" : "❌"}
                </span>
                <strong>{key.replace(/_/g, " ").toUpperCase()}</strong>
              </div>
              <p>{check.detail}</p>
            </div>
          ))}
        </div>
      )}

      {report && (
        <div className="audit-report">
          <h3>Audit Report -- {report.report_id}</h3>
          <p className="report-period">
            Period: {report.period.start.slice(0, 10)} &rarr; {report.period.end.slice(0, 10)}
          </p>
          <div className="report-summary" role="list" aria-label="Report summary">
            {Object.entries(report.summary).map(([key, val]) => (
              <div key={key} className="report-stat" role="listitem">
                <strong>{String(val)}</strong>
                <span>{key.replace(/_/g, " ")}</span>
              </div>
            ))}
          </div>
          <h4 style={{ margin: "1rem 0 0.5rem" }}>Recent Audit Events ({report.events.length})</h4>
          <div className="audit-events" role="table" aria-label="Audit events">
            {report.events.slice(0, 10).map((e, i) => (
              <div key={i} className="audit-event" role="row">
                <span className="event-name" role="cell">{e.event_name}</span>
                <span className="event-user" role="cell">{e.user}</span>
                <span className="event-time" role="cell">{new Date(e.event_time).toLocaleString()}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
