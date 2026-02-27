import { useEffect, useRef, useState, useCallback } from "react";

const WS_BASE = process.env.REACT_APP_BACKEND_URL
  .replace(/^http/, "ws");

export function useSLAWebSocket() {
  const [events, setEvents] = useState([]);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef(null);
  const retryRef = useRef(0);
  const timerRef = useRef(null);

  const clearEvent = useCallback((idx) => {
    setEvents((prev) => prev.filter((_, i) => i !== idx));
  }, []);

  const clearAll = useCallback(() => setEvents([]), []);

  useEffect(() => {
    let destroyed = false;

    function connect() {
      if (destroyed) return;
      const ws = new WebSocket(`${WS_BASE}/api/ws/sla`);
      wsRef.current = ws;

      ws.onopen = () => {
        setConnected(true);
        retryRef.current = 0;
      };

      ws.onmessage = (e) => {
        try {
          const data = JSON.parse(e.data);
          if (data.type === "pong" || data.type === "heartbeat") return;
          setEvents((prev) => [data, ...prev].slice(0, 50));
        } catch {}
      };

      ws.onclose = () => {
        setConnected(false);
        if (!destroyed) {
          const delay = Math.min(2000 * 2 ** retryRef.current, 30000);
          retryRef.current += 1;
          timerRef.current = setTimeout(connect, delay);
        }
      };

      ws.onerror = () => ws.close();
    }

    connect();

    // Keepalive ping every 25s
    const ping = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send("ping");
      }
    }, 25000);

    return () => {
      destroyed = true;
      clearInterval(ping);
      clearTimeout(timerRef.current);
      wsRef.current?.close();
    };
  }, []);

  return { events, connected, clearEvent, clearAll };
}
