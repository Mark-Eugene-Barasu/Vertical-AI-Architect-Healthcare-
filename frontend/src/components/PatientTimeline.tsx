import { useState } from "react";
import { timelineApi } from "../services/api";
import type { TimelineEvent } from "../types";

const EVENT_ICONS: Record<string, string> = {
  NOTE: "📋",
  DRUG_CHECK: "💊",
  ALERT: "🚨",
  DIAGNOSIS: "🔬",
  MEDICATION: "💉",
  LAB_RESULT: "🧪",
  VISIT: "🏥",
};

const EVENT_COLORS: Record<string, string> = {
  NOTE: "#2b6cb0",
  DRUG_CHECK: "#38a169",
  ALERT: "#e53e3e",
  DIAGNOSIS: "#805ad5",
  MEDICATION: "#dd6b20",
  LAB_RESULT: "#0987a0",
  VISIT: "#718096",
};

export default function PatientTimeline() {
  const [patientId, setPatientId] = useState("");
  const [timeline, setTimeline] = useState<TimelineEvent[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const fetchTimeline = async () => {
    if (!patientId.trim()) return setError("Patient ID is required");
    setLoading(true);
    setError("");
    try {
      const { data } = await timelineApi.get(patientId);
      setTimeline(data.timeline);
    } catch {
      setError("Failed to load timeline.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="panel">
      <h2>📅 Patient History Timeline</h2>
      <div className="timeline-search">
        <input
          placeholder="Enter Patient ID"
          value={patientId}
          onChange={(e) => setPatientId(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && fetchTimeline()}
          aria-label="Patient ID"
        />
        <button onClick={fetchTimeline} disabled={loading}>
          {loading ? "Loading..." : "Load Timeline"}
        </button>
      </div>
      {error && <p className="error" role="alert">{error}</p>}

      {timeline.length > 0 && (
        <div className="timeline" role="list" aria-label="Patient timeline events">
          {timeline.map((event, idx) => (
            <div key={idx} className="timeline-event" role="listitem">
              <div
                className="timeline-dot"
                style={{ background: EVENT_COLORS[event.event_type] || "#718096" }}
                aria-hidden="true"
              >
                {EVENT_ICONS[event.event_type] || "📌"}
              </div>
              <div className="timeline-content">
                <div className="timeline-header">
                  <strong style={{ color: EVENT_COLORS[event.event_type] }}>
                    {event.event_type.replace(/_/g, " ")}
                  </strong>
                  <small>{new Date(event.timestamp).toLocaleString()}</small>
                </div>
                <p>{event.title}</p>
                {Object.keys(event.data).length > 0 && (
                  <pre className="timeline-data">{JSON.stringify(event.data, null, 2)}</pre>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {timeline.length === 0 && patientId && !loading && !error && (
        <p className="empty-state">No timeline events found for this patient.</p>
      )}
    </div>
  );
}
