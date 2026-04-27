import type { Alert } from "../hooks/useAlerts";

const SEVERITY_STYLES: Record<string, { bg: string; border: string; color: string; icon: string }> = {
  CRITICAL: { bg: "#fff5f5", border: "#fc8181", color: "#c53030", icon: "🚨" },
  HIGH:     { bg: "#fffaf0", border: "#f6ad55", color: "#c05621", icon: "⚠️" },
  MEDIUM:   { bg: "#fffff0", border: "#f6e05e", color: "#975a16", icon: "⚡" },
  INFO:     { bg: "#ebf8ff", border: "#63b3ed", color: "#2b6cb0", icon: "ℹ️" },
};

interface Props {
  alerts: Alert[];
  onDismiss: (timestamp: string) => void;
}

export default function AlertBanner({ alerts, onDismiss }: Props) {
  if (alerts.length === 0) return null;

  return (
    <div className="alert-container">
      {alerts.map((alert) => {
        const style = SEVERITY_STYLES[alert.severity];
        return (
          <div
            key={alert.timestamp}
            className="alert-item"
            style={{ background: style.bg, borderLeft: `4px solid ${style.border}` }}
          >
            <div className="alert-header">
              <span style={{ color: style.color, fontWeight: 700 }}>
                {style.icon} {alert.severity} — {alert.alert_type.replace(/_/g, " ")}
              </span>
              <button className="dismiss-btn" onClick={() => onDismiss(alert.timestamp)}>✕</button>
            </div>
            <p className="alert-message">{alert.message}</p>
            <small className="alert-meta">
              Patient: {alert.patient_id} · {new Date(alert.timestamp).toLocaleTimeString()}
            </small>
          </div>
        );
      })}
    </div>
  );
}
