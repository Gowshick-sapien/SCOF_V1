import React from "react";
import styles from "./AgentCommand.module.css";
import { useAgentActivity } from "../../hooks/useAgentActivity";
import type { AgentActivityPayload } from "../../api/types";

interface SpecialistAgent {
  id: string;
  name: string;
  endpoint: string;
  role: string;
  skills: string[];
}

const SPECIALIST_AGENTS: SpecialistAgent[] = [
  {
    id: "demand-agent",
    name: "Demand Forecasting Specialist",
    endpoint: "http://demand-agent:8011",
    role: "Prophet + XGBoost time-series forecasting & demand surge detection.",
    skills: ["forecast_demand", "detect_anomalies"],
  },
  {
    id: "inventory-agent",
    name: "Inventory Risk Specialist",
    endpoint: "http://inventory-agent:8012",
    role: "Multi-echelon safety stock optimization and stockout hazard modeling.",
    skills: ["evaluate_stockouts", "reorder_safety_stock"],
  },
  {
    id: "supplier-agent",
    name: "Supplier Intelligence Specialist",
    endpoint: "http://supplier-agent:8013",
    role: "Supplier reliability ranking, lead-time variance analysis, and alternate sourcing.",
    skills: ["analyze_lead_times", "alternate_routing"],
  },
  {
    id: "transport-agent",
    name: "Transportation Logistics Specialist",
    endpoint: "http://transport-agent:8014",
    role: "Dynamic lane routing, carrier capacity allocation, and freight cost optimization.",
    skills: ["reroute_lanes", "estimate_transit_delays"],
  },
];

export const AgentCommandView: React.FC = () => {
  const activities = useAgentActivity();

  // Find latest state per agent
  const getAgentStatus = (agentId: string) => {
    const latest = activities.find((a: AgentActivityPayload) => a.agent_id === agentId);
    if (!latest) return { status: "IDLE", latency: null, timestamp: null };
    return {
      status: latest.status,
      latency: latest.latency_ms ?? (latest as any).execution_time_ms ?? null,
      timestamp: latest.timestamp || null,
    };
  };

  return (
    <div className={styles.container}>
      <div className={styles.sectionHeader}>
        <span className={styles.sectionTitle}>Autonomous Specialist Agents (A2A Network)</span>
        <span style={{ fontSize: "11px", color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>
          4 REGISTERED ON PROTOCOL
        </span>
      </div>

      {/* Agents Grid */}
      <div className={styles.agentsGrid}>
        {SPECIALIST_AGENTS.map((agent) => {
          const { status, latency } = getAgentStatus(agent.id);
          const isCompleted = status === "COMPLETED";
          const isRunning = status === "RUNNING";
          const isDispatched = status === "DISPATCHED";

          return (
            <div
              key={agent.id}
              className={`${styles.agentCard} ${isRunning || isCompleted ? styles.agentCardActive : ""}`}
            >
              <div className={styles.agentHeader}>
                <div>
                  <h4 className={styles.agentName}>{agent.name}</h4>
                  <span className={styles.agentId}>{agent.id}</span>
                </div>
                <span
                  className={`${styles.statusPill} ${
                    isCompleted
                      ? styles.statusCompleted
                      : isRunning
                      ? styles.statusRunning
                      : isDispatched
                      ? styles.statusDispatched
                      : styles.statusIdle
                  }`}
                >
                  {status}
                </span>
              </div>

              <p className={styles.agentDesc}>{agent.role}</p>

              <div className={styles.agentMeta}>
                <span>Endpoint: :{agent.endpoint.split(":").pop()}</span>
                <span>{latency ? `${Math.round(latency)}ms` : "Ready"}</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Agent Activity Stream */}
      <div className={styles.historySection}>
        <div className={styles.sectionHeader}>
          <span className={styles.sectionTitle}>Live Activity Event Feed</span>
          <span style={{ fontSize: "11px", color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>
            {activities.length} EVENTS RECORDED
          </span>
        </div>

        <div className={styles.timeline}>
          {activities.length === 0 ? (
            <div style={{ color: "var(--text-muted)", fontSize: "13px", padding: "16px 0" }}>
              No recent agent events. Trigger a scenario from the Scenarios tab to observe real-time execution.
            </div>
          ) : (
            activities.map((act: AgentActivityPayload, idx: number) => (
              <div key={idx} className={styles.timelineItem}>
                <div className={styles.timelineLeft}>
                  <span className={styles.timelineAgent}>{act.agent_id}</span>
                  <span className={styles.timelineMessage}>
                    Status changed to <strong style={{ color: "var(--accent-cyan)" }}>{act.status}</strong>
                    {act.latency_ms ? ` (${Math.round(act.latency_ms)}ms)` : ""}
                  </span>
                </div>
                <span className={styles.timelineTime}>
                  {act.timestamp ? new Date(act.timestamp).toLocaleTimeString() : "Live"}
                </span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
