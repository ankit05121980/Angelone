import { useEffect } from "react";

import { useAppStore } from "../store";

export function useRealtime(): void {
  const pushEvent = useAppStore((state) => state.pushEvent);
  const load = useAppStore((state) => state.load);

  useEffect(() => {
    const wsBase = import.meta.env.VITE_WS_URL ?? `${window.location.protocol === "https:" ? "wss" : "ws"}://${window.location.host}/api/v1/ws`;
    const websocket = new WebSocket(wsBase);
    websocket.onmessage = (message) => {
      const data = JSON.parse(message.data) as { event: string; payload: unknown };
      pushEvent(data.event, data.payload);
      if (["order_update", "position_closed", "pnl_update", "strategy_status"].includes(data.event)) {
        void load();
      }
    };
    websocket.onopen = () => pushEvent("websocket_connected", {});
    websocket.onerror = () => pushEvent("websocket_error", {});
    return () => websocket.close();
  }, [load, pushEvent]);
}
