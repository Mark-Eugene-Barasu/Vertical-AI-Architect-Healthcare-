import { useState } from "react";
import { decisionApi } from "../services/api";

export default function DecisionSupport() {
  const [context, setContext] = useState("");
  const [query, setQuery] = useState("");
  const [suggestions, setSuggestions] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async () => {
    if (!context || !query) return setError("Patient context and query are required");
    setLoading(true);
    setError("");
    try {
      const { data } = await decisionApi.suggest(context, query);
      setSuggestions(data.suggestions);
    } catch {
      setError("Failed to get suggestions. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="panel">
      <h2>🧠 AI Decision Support</h2>
      <textarea
        placeholder="Patient context (age, symptoms, history, current medications...)"
        rows={5}
        value={context}
        onChange={(e) => setContext(e.target.value)}
      />
      <input
        placeholder="Clinical query (e.g. 'What is the recommended treatment for...')"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />
      {error && <p className="error">{error}</p>}
      <button onClick={handleSubmit} disabled={loading}>
        {loading ? "Thinking..." : "Get AI Recommendations"}
      </button>

      {suggestions && (
        <div className="suggestions">
          <h3>AI Recommendations</h3>
          <div className="suggestion-text">
            {suggestions.split("\n").map((line, i) => <p key={i}>{line}</p>)}
          </div>
          <p className="disclaimer">
            ⚠️ AI suggestions are for decision support only. Always apply clinical judgment.
          </p>
        </div>
      )}
    </div>
  );
}
