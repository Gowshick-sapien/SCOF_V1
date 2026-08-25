import { useState, useEffect } from "react";
import { wsManager } from "../api/websocket";
import { AgentActivityPayload, EventEnvelope } from "../api/types";

export function useAgentActivity() {
  const [activities, setActivities] = useState<AgentActivityPayload[]>([]);

  useEffect(() => {
    const unsub = wsManager.subscribe("/ws/agents/activity", (data: EventEnvelope<AgentActivityPayload>) => {
      if (data?.payload && typeof data.payload.status === "string") {
        setActivities(prev => {
          const next = [...prev];
          const existingIdx = next.findIndex(
            a => a.agent_id === data.payload.agent_id && a.scenario_id === data.payload.scenario_id
          );
          
          if (existingIdx >= 0) {
            next[existingIdx] = data.payload;
            return next;
          }
          
          return [data.payload, ...next].slice(0, 50); // Keep last 50 activities
        });
      }
    });
    return unsub;
  }, []);

  return activities;
}
