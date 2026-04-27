import { useState } from "react";
import { drugsApi } from "../services/api";
import type { DrugInteraction } from "../types";

export default function DrugChecker() {
  const [input, setInput] = useState("");
  const [medications, setMedications] = useState<string[]>([]);
  const [interactions, setInteractions] = useState<DrugInteraction[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleCheck = async () => {
    if (!input.trim()) return setError("Enter medications or clinical text");
    setLoading(true);
    setError("");
    try {
      const { data } = await drugsApi.check([], input);
      setMedications(data.medications);
      setInteractions(data.interactions);
    } catch {
      setError("Failed to check interactions. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const severityColor = (severity: string) =>
    severity === "HIGH" ? "#e53e3e" : severity === "MEDIUM" ? "#dd6b20" : "#38a169";

  return (
    <div className="panel">
      <h2>💊 Drug Interaction Checker</h2>
      <textarea
        placeholder="Enter medications (comma-separated) or paste clinical text..."
        rows={5}
        value={input}
        onChange={(e) => setInput(e.target.value)}
      />
      {error && <p className="error">{error}</p>}
      <button onClick={handleCheck} disabled={loading}>
        {loading ? "Checking..." : "Check Interactions"}
      </button>

      {medications.length > 0 && (
        <div className="results">
          <h3>Detected Medications</h3>
          <div className="med-tags">
            {medications.map((m) => <span key={m} className="tag">{m}</span>)}
          </div>

          <h3>Interactions {interactions.length === 0 && "— None Found ✅"}</h3>
          {interactions.map((i, idx) => (
            <div key={idx} className="interaction-card" style={{ borderLeft: `4px solid ${severityColor(i.severity)}` }}>
              <strong style={{ color: severityColor(i.severity) }}>{i.severity} RISK</strong>
              <p>{i.warning}</p>
              <small>Drugs: {i.drugs.join(" + ")}</small>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
