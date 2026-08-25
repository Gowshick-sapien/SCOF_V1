import { useState, useEffect } from "react";
import { wsManager } from "../api/websocket";
import { EventEnvelope, DecisionCompletedPayload, OrchestrationFailedPayload } from "../api/types";

export type LocalDecisionEvent = 
  | { type: "completed"; payload: DecisionCompletedPayload }
  | { type: "failed"; payload: OrchestrationFailedPayload };

export function useDecisions() {
  const [events, setEvents] = useState<LocalDecisionEvent[]>([]);

  useEffect(() => {
    const unsub = wsManager.subscribe("/ws/decisions/live", (data: EventEnvelope<any>) => {
      if (data?.event_type === "decision.completed") {
        setEvents(prev => {
          const newEvent: LocalDecisionEvent = { type: "completed", payload: data.payload as DecisionCompletedPayload };
          return [newEvent, ...prev].slice(0, 20);
        });
      } else if (data?.event_type === "orchestration.failed") {
        setEvents(prev => {
          const newEvent: LocalDecisionEvent = { type: "failed", payload: data.payload as OrchestrationFailedPayload };
          return [newEvent, ...prev].slice(0, 20);
        });
      }
    });
    return unsub;
  }, []);

  return events;
}
