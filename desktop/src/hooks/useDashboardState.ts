import { useState, useEffect } from "react";
import { wsManager } from "../api/websocket";
import { DashboardState } from "../api/types";

export function useDashboardState() {
  const [dashboard, setDashboard] = useState<DashboardState | null>(null);

  useEffect(() => {
    const unsub = wsManager.subscribe("/ws/dashboard/state", (data: any) => {
      // Handle both raw payloads and EventEnvelopes based on D08 conventions
      if (data && typeof data === "object") {
        if ("payload" in data && data.payload) {
          setDashboard(data.payload as DashboardState);
        } else {
          setDashboard(data as DashboardState);
        }
      }
    });
    return unsub;
  }, []);

  return dashboard;
}
