import { useEffect, useRef, useState, useCallback } from "react";
import { fetchAuthSession } from "aws-amplify/auth";
import type { Alert } from "../types";

// Re-export for components that import from here
export type { Alert };

const MAX_ALERTS = 50;
const RECONNECT_DELAY_MS = 3000;

export function useAlerts(clinicianId: string) {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (!clinicianId) return;

    let isMounted = true;

    const connect = async () => {
      try {
        const session = await fetchAuthSession();
        const token = session.tokens?.idToken?.toString();
        const wsUrl = `${import.meta.env.VITE_WS_URL}/api/alerts/ws/${clinicianId}?token=${token}`;

        wsRef.current = new WebSocket(wsUrl);

        wsRef.current.onmessage = (event) => {
          if (!isMounted) return;
          try {
            const alert: Alert = JSON.parse(event.data);
            setAlerts((prev) => [alert, ...prev].slice(0, MAX_ALERTS));
          } catch {
            console.error("[useAlerts] Failed to parse alert message");
          }
        };

        wsRef.current.onclose = () => {
          if (!isMounted) return;
          reconnectTimerRef.current = setTimeout(connect, RECONNECT_DELAY_MS);
        };

        wsRef.current.onerror = () => {
          wsRef.current?.close();
        };
      } catch {
        if (isMounted) {
          reconnectTimerRef.current = setTimeout(connect, RECONNECT_DELAY_MS);
        }
      }
    };

    connect();

    return () => {
      isMounted = false;
      wsRef.current?.close();
      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current);
      }
    };
  }, [clinicianId]);

  const dismissAlert = useCallback(
    (timestamp: string) => setAlerts((prev) => prev.filter((a) => a.timestamp !== timestamp)),
    [],
  );

  return { alerts, dismissAlert };
}
