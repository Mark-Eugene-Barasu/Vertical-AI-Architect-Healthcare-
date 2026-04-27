import { useState } from "react";
import { notesApi } from "../services/api";
import type { SOAPNote } from "../types";

export default function NoteGenerator() {
  const [patientId, setPatientId] = useState("");
  const [transcript, setTranscript] = useState("");
  const [note, setNote] = useState<SOAPNote | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleGenerate = async () => {
    if (!transcript || !patientId) return setError("Patient ID and transcript are required");
    setLoading(true);
    setError("");
    try {
      const { data } = await notesApi.generate(transcript, patientId);
      setNote(data.clinical_note);
    } catch {
      setError("Failed to generate note. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="panel">
      <h2>🎙️ Clinical Note Generator</h2>
      <input
        placeholder="Patient ID"
        value={patientId}
        onChange={(e) => setPatientId(e.target.value)}
      />
      <textarea
        placeholder="Paste or type the doctor-patient conversation transcript here..."
        rows={8}
        value={transcript}
        onChange={(e) => setTranscript(e.target.value)}
      />
      {error && <p className="error">{error}</p>}
      <button onClick={handleGenerate} disabled={loading}>
        {loading ? "Generating..." : "Generate SOAP Note"}
      </button>

      {note && (
        <div className="soap-note">
          <h3>Generated SOAP Note</h3>
          {(["subjective", "objective", "assessment", "plan", "follow_up"] as const).map((key) => (
            <div key={key} className="soap-section">
              <strong>{key.replace("_", " ").toUpperCase()}</strong>
              <p>{note[key]}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
