import { useNavigate } from "react-router-dom";

export default function NotFound() {
  const navigate = useNavigate();

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        minHeight: "100vh",
        background: "linear-gradient(135deg, #1a365d, #2b6cb0)",
        color: "white",
        padding: "2rem",
        textAlign: "center",
      }}
    >
      <h1 style={{ fontSize: "6rem", fontWeight: 800, marginBottom: "0.5rem", opacity: 0.9 }}>
        404
      </h1>
      <h2 style={{ fontSize: "1.5rem", fontWeight: 600, marginBottom: "0.75rem" }}>
        Page Not Found
      </h2>
      <p style={{ color: "rgba(255,255,255,0.7)", maxWidth: "400px", marginBottom: "2rem" }}>
        The page you are looking for does not exist or has been moved.
      </p>
      <div style={{ display: "flex", gap: "1rem" }}>
        <button
          onClick={() => navigate("/")}
          style={{
            background: "white",
            color: "#1a365d",
            border: "none",
            padding: "0.75rem 1.5rem",
            borderRadius: "8px",
            cursor: "pointer",
            fontWeight: 600,
          }}
        >
          Go Home
        </button>
        <button
          onClick={() => navigate("/dashboard")}
          style={{
            background: "rgba(255,255,255,0.15)",
            color: "white",
            border: "1px solid rgba(255,255,255,0.3)",
            padding: "0.75rem 1.5rem",
            borderRadius: "8px",
            cursor: "pointer",
            fontWeight: 600,
          }}
        >
          Dashboard
        </button>
      </div>
    </div>
  );
}
