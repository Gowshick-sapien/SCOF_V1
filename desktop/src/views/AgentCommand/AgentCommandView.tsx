import React, { useState } from "react";
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
  const [selectedAgentId, setSelectedAgentId] = useState<string>(SPECIALIST_AGENTS[0].id);

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

  const selectedAgent =
    SPECIALIST_AGENTS.find((a) => a.id === selectedAgentId) || SPECIALIST_AGENTS[0];
  const selectedTelemetry = getAgentStatus(selectedAgent.id);

  return (
    <div className={styles.container}>
      <div className={styles.sectionHeader}>
        <span className={styles.sectionTitle}>Autonomous Specialist Agents (A2A Network)</span>
        <span style={{ fontSize: "11px", color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>
          {SPECIALIST_AGENTS.length} SPECIALISTS REGISTERED ON PROTOCOL
        </span>
      </div>

      {/* Main Grid: Left Operations Table + Right Specialist Inspector */}
      <div className={styles.mainGrid}>
        {/* Operations Data Table */}
        <div className={styles.tableCard}>
          <div className={styles.tableWrapper}>
            <table className={styles.agentTable}>
              <thead>
                <tr>
                  <th>Agent ID</th>
                  <th>Specialist Role</th>
                  <th>Status</th>
                  <th>Endpoint</th>
                  <th>Latency</th>
                </tr>
              </thead>
              <tbody>
                {SPECIALIST_AGENTS.map((agent) => {
                  const { status, latency } = getAgentStatus(agent.id);
                  const isSelected = agent.id === selectedAgentId;
                  const isCompleted = status === "COMPLETED";
                  const isRunning = status === "RUNNING";
                  const isDispatched = status === "DISPATCHED";

                  return (
                    <tr
                      key={agent.id}
                      className={`${styles.agentRow} ${isSelected ? styles.agentRowSelected : ""}`}
                      onClick={() => setSelectedAgentId(agent.id)}
                    >
                      <td className={styles.agentId}>{agent.id}</td>
                      <td>
                        <div style={{ fontWeight: 600, color: "var(--text-primary)" }}>{agent.name}</div>
                      </td>
                      <td>
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
                      </td>
                      <td style={{ fontFamily: "var(--font-mono)", fontSize: "11.5px" }}>
                        :{agent.endpoint.split(":").pop()}
                      </td>
                      <td className={styles.latencyValue}>
                        {latency ? `${Math.round(latency)}ms` : "Ready"}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Right Telemetry Inspector Panel */}
        <div className={styles.inspectorCard}>
          <div className={styles.inspectorHeader}>
            <span className={styles.inspectorTitle}>Specialist Telemetry Inspector</span>
            <span
              className={`${styles.statusPill} ${
                selectedTelemetry.status === "COMPLETED"
                  ? styles.statusCompleted
                  : selectedTelemetry.status === "RUNNING"
                  ? styles.statusRunning
                  : styles.statusIdle
              }`}
            >
              {selectedTelemetry.status}
            </span>
          </div>

          <div className={styles.metaGrid}>
            <span className={styles.metaLabel}>Specialist ID</span>
            <span className={styles.metaValue}>{selectedAgent.id}</span>

            <span className={styles.metaLabel}>Designation</span>
            <span className={styles.metaValue}>{selectedAgent.name}</span>

            <span className={styles.metaLabel}>Endpoint URI</span>
            <span className={styles.metaValue}>{selectedAgent.endpoint}</span>

            <span className={styles.metaLabel}>Last Latency</span>
            <span className={styles.metaValue}>
              {selectedTelemetry.latency ? `${Math.round(selectedTelemetry.latency)}ms` : "Standby"}
            </span>
          </div>

          <div>
            <span className={styles.metaLabel} style={{ display: "block", marginBottom: 6 }}>
              Specialization Scope
            </span>
            <div className={styles.roleBox}>{selectedAgent.role}</div>
          </div>

          <div>
            <span className={styles.metaLabel} style={{ display: "block", marginBottom: 6 }}>
              Registered A2A Capabilities
            </span>
            <div className={styles.skillsContainer}>
              {selectedAgent.skills.map((skill) => (
                <span key={skill} className={styles.skillBadge}>
                  {skill}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Live Activity Event Feed */}
      <div className={styles.historyCard}>
        <div className={styles.sectionHeader}>
          <span className={styles.sectionTitle}>Live Activity Event Feed</span>
          <span style={{ fontSize: "11px", color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>
            {activities.length} EVENTS RECORDED
          </span>
        </div>

        <div className={styles.timeline}>
          {activities.length === 0 ? (
            <div style={{ color: "var(--text-muted)", fontSize: "12px", padding: "10px 0" }}>
              No recent agent events. Trigger a scenario from the Scenario Launcher tab to observe real-time execution.
            </div>
          ) : (
            activities.map((act: AgentActivityPayload, idx: number) => {
              const formattedTime = act.timestamp
                ? new Date(act.timestamp).toISOString().substring(11, 19) + " UTC"
                : "Live";

              return (
                <div key={idx} className={styles.timelineItem}>
                  <div className={styles.timelineLeft}>
                    <span className={styles.timelineAgent}>{act.agent_id}</span>
                    <span className={styles.timelineMessage}>
                      Status changed to <strong style={{ color: "var(--interactive-primary)" }}>{act.status}</strong>
                      {act.latency_ms ? ` (${Math.round(act.latency_ms)}ms)` : ""}
                    </span>
                  </div>
                  <span className={styles.timelineTime}>{formattedTime}</span>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
};
