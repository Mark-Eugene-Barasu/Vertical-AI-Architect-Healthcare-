import { useEffect, useRef, useState } from "react";
import { fetchAuthSession } from "aws-amplify/auth";

export interface Alert {
  alert_type: string;
  severity: "CRITICAL" | "HIGH" | "MEDIUM" | "INFO";
  patient_id: string;
  message: string;
  details: Record<string, any>;
  timestamp: string;
}

export function useAlerts(clinicianId: string) {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!clinicianId) return;

    const connect = async () => {
      const session = await fetchAuthSession();
      const token = session.tokens?.idToken?.toString();
      const wsUrl = `${import.meta.env.VITE_WS_URL}/api/alerts/ws/${clinicianId}?token=${token}`;

      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onmessage = (event) => {
        const alert: Alert = JSON.parse(event.data);
        setAlerts((prev) => [alert, ...prev].slice(0, 50)); // keep last 50
      };

      wsRef.current.onclose = () => {
        setTimeout(connect, 3000); // auto-reconnect
      };
    };

    connect();
    return () => wsRef.current?.close();
  }, [clinicianId]);

  const dismissAlert = (timestamp: string) =>
    setAlerts((prev) => prev.filter((a) => a.timestamp !== timestamp));

  return { alerts, dismissAlert };
}
