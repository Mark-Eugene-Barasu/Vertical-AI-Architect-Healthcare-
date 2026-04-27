import { Component, type ErrorInfo, type ReactNode } from "react";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

/**
 * React Error Boundary that catches render errors in child components
 * and displays a fallback UI instead of crashing the entire app.
 */
export default class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("[ErrorBoundary] Uncaught error:", error, errorInfo);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            minHeight: "40vh",
            padding: "2rem",
            textAlign: "center",
          }}
          role="alert"
        >
          <h2 style={{ color: "#e53e3e", marginBottom: "0.75rem" }}>Something went wrong</h2>
          <p style={{ color: "#718096", marginBottom: "1.5rem", maxWidth: "500px" }}>
            An unexpected error occurred. Please try refreshing the page or click the button below.
          </p>
          <button
            onClick={this.handleReset}
            style={{
              background: "#2b6cb0",
              color: "white",
              border: "none",
              padding: "0.75rem 1.5rem",
              borderRadius: "8px",
              cursor: "pointer",
              fontWeight: 600,
            }}
          >
            Try Again
          </button>
          {this.state.error && (
            <pre
              style={{
                marginTop: "1.5rem",
                padding: "1rem",
                background: "#f7fafc",
                borderRadius: "8px",
                fontSize: "0.8rem",
                color: "#718096",
                maxWidth: "600px",
                overflow: "auto",
              }}
            >
              {this.state.error.message}
            </pre>
          )}
        </div>
      );
    }

    return this.props.children;
  }
}
