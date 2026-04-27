import { useEffect, useState } from "react";
import axios from "axios";

interface Metrics {
  month: string;
  notes_generated: number;
  drug_checks_performed: number;
  decision_queries: number;
  transcriptions: number;
  estimated_time_saved_hours: number;
  estimated_errors_prevented: number;
}

interface TrendPoint {
  month: string;
  notes: number;
  drug_checks: number;
  decision_queries: number;
}

interface AlertSummary {
  total_alerts: number;
  critical: number;
  high: number;
  medium: number;
}

export default function AnalyticsDashboard() {
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [trend, setTrend] = useState<TrendPoint[]>([]);
  const [alertSummary, setAlertSummary] = useState<AlertSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      axios.get("/api/analytics/metrics"),
      axios.get("/api/analytics/trend"),
      axios.get("/api/analytics/alerts"),
    ]).then(([m, t, a]) => {
      setMetrics(m.data);
      setTrend(t.data.trend);
      setAlertSummary(a.data);
    }).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="loading">Loading analytics...</div>;

  const statCards = [
    { label: "Notes Generated",       value: metrics?.notes_generated,           icon: "📋", color: "#2b6cb0" },
    { label: "Drug Checks",            value: metrics?.drug_checks_performed,      icon: "💊", color: "#38a169" },
    { label: "Hours Saved",            value: metrics?.estimated_time_saved_hours, icon: "⏱️", color: "#805ad5" },
    { label: "Errors Prevented",       value: metrics?.estimated_errors_prevented, icon: "🛡️", color: "#e53e3e" },
    { label: "Decision Queries",       value: metrics?.decision_queries,           icon: "🧠", color: "#dd6b20" },
    { label: "Transcriptions",         value: metrics?.transcriptions,             icon: "🎙️", color: "#0987a0" },
  ];

  const maxNotes = Math.max(...trend.map((t) => t.notes), 1);

  return (
    <div className="panel">
      <h2>📊 Analytics Dashboard — {metrics?.month}</h2>

      <div className="stat-grid">
        {statCards.map((card) => (
          <div key={card.label} className="stat-card" style={{ borderTop: `4px solid ${card.color}` }}>
            <span className="stat-icon">{card.icon}</span>
            <span className="stat-value" style={{ color: card.color }}>{card.value ?? 0}</span>
            <span className="stat-label">{card.label}</span>
          </div>
        ))}
      </div>

      <h3 style={{ margin: "2rem 0 1rem" }}>📈 6-Month Usage Trend</h3>
      <div className="trend-chart">
        {trend.map((point) => (
          <div key={point.month} className="trend-bar-group">
            <div className="trend-bars">
              <div className="trend-bar" style={{ height: `${(point.notes / maxNotes) * 100}%`, background: "#2b6cb0" }} title={`Notes: ${point.notes}`} />
              <div className="trend-bar" style={{ height: `${(point.drug_checks / maxNotes) * 100}%`, background: "#38a169" }} title={`Drug checks: ${point.drug_checks}`} />
              <div className="trend-bar" style={{ height: `${(point.decision_queries / maxNotes) * 100}%`, background: "#805ad5" }} title={`Decisions: ${point.decision_queries}`} />
            </div>
            <span className="trend-label">{point.month.slice(5)}</span>
          </div>
        ))}
      </div>
      <div className="chart-legend">
        <span><span className="legend-dot" style={{ background: "#2b6cb0" }} /> Notes</span>
        <span><span className="legend-dot" style={{ background: "#38a169" }} /> Drug Checks</span>
        <span><span className="legend-dot" style={{ background: "#805ad5" }} /> Decisions</span>
      </div>

      {alertSummary && (
        <>
          <h3 style={{ margin: "2rem 0 1rem" }}>🚨 Alert Summary</h3>
          <div className="alert-summary">
            <div className="alert-stat" style={{ color: "#e53e3e" }}>
              <strong>{alertSummary.critical}</strong><span>Critical</span>
            </div>
            <div className="alert-stat" style={{ color: "#dd6b20" }}>
              <strong>{alertSummary.high}</strong><span>High</span>
            </div>
            <div className="alert-stat" style={{ color: "#975a16" }}>
              <strong>{alertSummary.medium}</strong><span>Medium</span>
            </div>
            <div className="alert-stat" style={{ color: "#2d3748" }}>
              <strong>{alertSummary.total_alerts}</strong><span>Total</span>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
