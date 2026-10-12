import React, { useState, useRef, useEffect } from "react";
import styles from "./AgentCommand.module.css";
import { useAgentActivity } from "../../hooks/useAgentActivity";
import type { AgentActivityPayload } from "../../api/types";
import { ContextualDrawer } from "../../components/common/ContextualDrawer";

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
  const [selectedAgentId, setSelectedAgentId] = useState<string | null>(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState<boolean>(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const [containerWidth, setContainerWidth] = useState<number>(1200);

  useEffect(() => {
    if (!containerRef.current) return;
    const updateSize = () => {
      if (containerRef.current) {
        setContainerWidth(containerRef.current.clientWidth);
      }
    };
    updateSize();

    const ro = new ResizeObserver((entries) => {
      for (const entry of entries) {
        setContainerWidth(entry.contentRect.width);
      }
    });
    ro.observe(containerRef.current);
    return () => ro.disconnect();
  }, []);

  const drawerMode = containerWidth >= 1100 ? "docked" : "overlay";

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

  const selectedAgent = SPECIALIST_AGENTS.find((a) => a.id === selectedAgentId);
  const selectedTelemetry = selectedAgent ? getAgentStatus(selectedAgent.id) : null;

  const handleSelectAgent = (agentId: string) => {
    setSelectedAgentId(agentId);
    setIsDrawerOpen(true);
  };

  const agentActivities = selectedAgent
    ? activities.filter((a) => a.agent_id === selectedAgent.id)
    : [];

  return (
    <div className={styles.workspaceWrapper} ref={containerRef}>
      <div className={styles.workspaceMain}>
        {/* Section Header */}
        <div className={styles.sectionHeader}>
          <div className={styles.headerTitleGroup}>
            <span className={styles.sectionTitle}>Autonomous Specialist Agents (A2A Network)</span>
            <span className={styles.agentCounter}>
              {SPECIALIST_AGENTS.length} SPECIALISTS REGISTERED ON PROTOCOL
            </span>
          </div>
          <span className={styles.protocolBadge}>A2A JSON-RPC 2.0</span>
        </div>

        {/* Full-Width Operations Data Table */}
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
                  <th>Capabilities</th>
                  <th style={{ textAlign: "right" }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {SPECIALIST_AGENTS.map((agent) => {
                  const { status, latency } = getAgentStatus(agent.id);
                  const isSelected = agent.id === selectedAgentId && isDrawerOpen;
                  const isCompleted = status === "COMPLETED";
                  const isRunning = status === "RUNNING";
                  const isDispatched = status === "DISPATCHED";

                  return (
                    <tr
                      key={agent.id}
                      className={`${styles.agentRow} ${isSelected ? styles.agentRowSelected : ""}`}
                      onClick={() => handleSelectAgent(agent.id)}
                    >
                      <td className={styles.agentId}>{agent.id}</td>
                      <td>
                        <div className={styles.agentName}>{agent.name}</div>
                        <div className={styles.agentRoleSub}>{agent.role}</div>
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
                      <td className={styles.endpointCell}>
                        {agent.endpoint}
                      </td>
                      <td className={styles.latencyValue}>
                        {latency ? `${Math.round(latency)}ms` : "Ready"}
                      </td>
                      <td>
                        <div className={styles.skillChipsInline}>
                          {agent.skills.map((s) => (
                            <span key={s} className={styles.inlineSkillBadge}>
                              {s}
                            </span>
                          ))}
                        </div>
                      </td>
                      <td style={{ textAlign: "right" }}>
                        <button
                          className={styles.inspectBtn}
                          onClick={(e) => {
                            e.stopPropagation();
                            handleSelectAgent(agent.id);
                          }}
                          title={`Inspect telemetry for ${agent.name}`}
                          aria-label={`Inspect ${agent.name}`}
                        >
                          Inspect
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Live Activity Event Feed */}
        <div className={styles.historyCard}>
          <div className={styles.sectionHeader}>
            <span className={styles.sectionTitle}>Live Activity Event Feed</span>
            <span className={styles.eventCounter}>
              {activities.length} EVENTS RECORDED
            </span>
          </div>

          <div className={styles.timeline}>
            {activities.length === 0 ? (
              <div className={styles.emptyFeed}>
                No recent agent events. Trigger a scenario from the Scenario Catalog to observe real-time execution.
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
                        Status transitioned to <strong className={styles.statusHighlight}>{act.status}</strong>
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

      {/* Contextual Telemetry Drawer */}
      {selectedAgent && selectedTelemetry && (
        <ContextualDrawer
          isOpen={isDrawerOpen}
          title={selectedAgent.name}
          badge={selectedAgent.id}
          mode={drawerMode}
          onClose={() => setIsDrawerOpen(false)}
        >
          <div className={styles.drawerContent}>
            <div className={styles.drawerSection}>
              <div className={styles.drawerHeaderStatus}>
                <span className={styles.drawerSectionLabel}>Operating Status</span>
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
            </div>

            <div className={styles.drawerSection}>
              <span className={styles.drawerSectionLabel}>Endpoint & Network Metadata</span>
              <div className={styles.metaGrid}>
                <div className={styles.metaRow}>
                  <span className={styles.metaLabel}>Endpoint URI:</span>
                  <span className={styles.metaValue}>{selectedAgent.endpoint}</span>
                </div>
                <div className={styles.metaRow}>
                  <span className={styles.metaLabel}>Specialist ID:</span>
                  <span className={styles.metaValue}>{selectedAgent.id}</span>
                </div>
                <div className={styles.metaRow}>
                  <span className={styles.metaLabel}>Current Latency:</span>
                  <span className={styles.metaValue}>
                    {selectedTelemetry.latency ? `${Math.round(selectedTelemetry.latency)}ms` : "Standby"}
                  </span>
                </div>
                <div className={styles.metaRow}>
                  <span className={styles.metaLabel}>Protocol Version:</span>
                  <span className={styles.metaValue}>A2A 1.0 (gRPC / HTTP REST)</span>
                </div>
              </div>
            </div>

            <div className={styles.drawerSection}>
              <span className={styles.drawerSectionLabel}>Specialization Scope</span>
              <div className={styles.roleBox}>{selectedAgent.role}</div>
            </div>

            <div className={styles.drawerSection}>
              <span className={styles.drawerSectionLabel}>Registered A2A Capabilities</span>
              <div className={styles.skillsContainer}>
                {selectedAgent.skills.map((skill) => (
                  <span key={skill} className={styles.skillBadge}>
                    {skill}
                  </span>
                ))}
              </div>
            </div>

            <div className={styles.drawerSection}>
              <span className={styles.drawerSectionLabel}>Specialist Execution History</span>
              {agentActivities.length === 0 ? (
                <div className={styles.emptyDrawerHistory}>
                  No recent execution events logged for {selectedAgent.id}.
                </div>
              ) : (
                <div className={styles.drawerHistoryList}>
                  {agentActivities.slice(0, 5).map((act, idx) => (
                    <div key={idx} className={styles.drawerHistoryItem}>
                      <span className={styles.drawerHistoryStatus}>{act.status}</span>
                      <span className={styles.drawerHistoryLatency}>
                        {act.latency_ms ? `${Math.round(act.latency_ms)}ms` : ""}
                      </span>
                      <span className={styles.drawerHistoryTime}>
                        {act.timestamp ? new Date(act.timestamp).toISOString().substring(11, 19) + " UTC" : "Live"}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </ContextualDrawer>
      )}
    </div>
  );
};
