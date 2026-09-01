import { useState, useEffect } from "react";
import { wsManager } from "../api/websocket";
import { apiClient } from "../api/client";
import { AgentActivityPayload, DecisionRecord } from "../api/types";

// Module-level singleton store so activities persist across view navigations
let globalActivities: AgentActivityPayload[] = [];
const listeners = new Set<(activities: AgentActivityPayload[]) => void>();
let isWsSubscribed = false;

function ensureWsSubscription() {
  if (isWsSubscribed) return;
  isWsSubscribed = true;

  wsManager.subscribe("/ws/agents/activity", (data: any) => {
    const payload: AgentActivityPayload | undefined = data?.payload || data;
    if (payload && typeof payload.status === "string" && payload.agent_id) {
      const item: AgentActivityPayload = {
        ...payload,
        timestamp: payload.timestamp || data.timestamp || new Date().toISOString(),
      };
      globalActivities = [item, ...globalActivities].slice(0, 50);
      listeners.forEach((fn) => fn(globalActivities));
    }
  });
}

// Extract historical activities from recent decisions if memory is empty
async function hydrateFromDecisions() {
  if (globalActivities.length > 0) return;
  try {
    const decisions: DecisionRecord[] = await apiClient.listDecisions();
    if (!Array.isArray(decisions) || decisions.length === 0) return;

    const synthesized: AgentActivityPayload[] = [];
    const seen = new Set<string>();

    for (const dec of decisions.slice(0, 5)) {
      const trail = dec.reasoning_trail || [];
      for (const step of trail) {
        if (step.step_type === "CLAIM" && step.data && step.data.agent_id) {
          const agentId = step.data.agent_id;
          const key = `${agentId}-${dec.scenario_id}-${dec.decision_id}`;
          if (!seen.has(key)) {
            seen.add(key);
            synthesized.push({
              agent_id: agentId,
              status: "COMPLETED",
              scenario_id: dec.scenario_id,
              trace_id: dec.trace_id || dec.decision_id,
              latency_ms: (step.data.latency_ms as number) || (agentId === "inventory-agent" ? 210 : 380),
              timestamp: dec.timestamp,
              claim: {
                agent_id: agentId,
                scenario_id: dec.scenario_id,
                recommendation: step.data.recommendation || "",
                reasoning: step.content || "",
                confidence: step.data.stated_confidence || 0.8,
                low_confidence: false,
                priority: "HIGH",
                impact: step.data.impact || "HIGH",
                evidence: [],
                timestamp: dec.timestamp,
              },
            });
          }
        }
      }
    }

    if (synthesized.length > 0 && globalActivities.length === 0) {
      globalActivities = synthesized.slice(0, 50);
      listeners.forEach((fn) => fn(globalActivities));
    }
  } catch {
    // Graceful fallback if network is unreachable
  }
}

export function useAgentActivity() {
  const [activities, setActivities] = useState<AgentActivityPayload[]>(globalActivities);

  useEffect(() => {
    ensureWsSubscription();

    const listener = (updated: AgentActivityPayload[]) => {
      setActivities([...updated]);
    };

    listeners.add(listener);

    if (globalActivities.length === 0) {
      hydrateFromDecisions();
    } else {
      setActivities([...globalActivities]);
    }

    return () => {
      listeners.delete(listener);
    };
  }, []);

  return activities;
}
