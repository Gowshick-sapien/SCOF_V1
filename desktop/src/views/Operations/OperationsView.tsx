import React, { useEffect, useState } from "react";
import styles from "./Operations.module.css";
import { useDashboardState } from "../../hooks/useDashboardState";
import { apiClient } from "../../api/client";
import type { DecisionRecord } from "../../api/types";

interface OperationsViewProps {
  onSelectDecision?: (decisionId: string) => void;
}

interface TopologyNode {
  id: string;
  name: string;
  type: "manufacturer" | "supplier" | "warehouse" | "dc";
  location: string;
  coords: string;
  x: number;
  y: number;
  details: string;
  status: "NOMINAL" | "ACTIVE" | "ELEVATED";
}

const TOPOLOGY_NODES: TopologyNode[] = [
  // 1. Central Assembly Hub
  {
    id: "mfg-01",
    name: "Sriperumbudur High-Tech Assembly Plant",
    type: "manufacturer",
    location: "Sriperumbudur, Tamil Nadu",
    coords: "12.9716 N, 79.9416 E",
    x: 580,
    y: 220,
    details: "Primary Tier-0 Assembly Hub for IoT Gateways, Telematics & Inverters",
    status: "NOMINAL",
  },
  // 2. Suppliers (8 nodes)
  {
    id: "sup-01",
    name: "SPEL Semiconductor",
    type: "supplier",
    location: "Maraimalai Nagar, Chennai, TN",
    coords: "12.7937 N, 80.0242 E",
    x: 690,
    y: 290,
    details: "Lead Time: 5d | WLCSP IC Packaging & Test Fab",
    status: "NOMINAL",
  },
  {
    id: "sup-02",
    name: "Continental Device India (CDIL)",
    type: "supplier",
    location: "Electronic City, Bengaluru, KA",
    coords: "12.8452 N, 77.6602 E",
    x: 230,
    y: 180,
    details: "Lead Time: 6d | Discrete Semiconductors & Power Transistors",
    status: "NOMINAL",
  },
  {
    id: "sup-03",
    name: "Kaynes Technology India",
    type: "supplier",
    location: "Koorgalli, Mysuru, KA",
    coords: "12.3382 N, 76.5824 E",
    x: 90,
    y: 170,
    details: "Lead Time: 8d | Automotive Telematics & IoT EMS",
    status: "NOMINAL",
  },
  {
    id: "sup-04",
    name: "Syrma SGS Technology",
    type: "supplier",
    location: "Bargur Industrial Estate, TN",
    coords: "12.5442 N, 78.3614 E",
    x: 430,
    y: 220,
    details: "Lead Time: 7d | High-Precision Surface Mount Assemblies",
    status: "NOMINAL",
  },
  {
    id: "sup-05",
    name: "Centum Electronics",
    type: "supplier",
    location: "Yelahanka, Bengaluru, KA",
    coords: "13.1007 N, 77.5963 E",
    x: 230,
    y: 105,
    details: "Lead Time: 9d | Microelectronics & Power Converters",
    status: "NOMINAL",
  },
  {
    id: "sup-06",
    name: "Vinyas Innovative Technologies",
    type: "supplier",
    location: "Hebbal Industrial Area, Mysuru, KA",
    coords: "12.3551 N, 76.6110 E",
    x: 90,
    y: 250,
    details: "Lead Time: 12d | Power Electronics & SMT Manufacturing",
    status: "NOMINAL",
  },
  {
    id: "sup-07",
    name: "SFO Technologies (NeST)",
    type: "supplier",
    location: "Kakkanad, Kochi, KL",
    coords: "9.9982 N, 76.3570 E",
    x: 130,
    y: 350,
    details: "Lead Time: 7d | Fiber Optics & Industrial Control Modules",
    status: "NOMINAL",
  },
  {
    id: "sup-08",
    name: "Sahasra Electronic Solutions",
    type: "supplier",
    location: "Hyderabad, TS",
    coords: "17.3850 N, 78.4867 E",
    x: 390,
    y: 50,
    details: "Lead Time: 10d | High-Layer PCB Fabrication & LED Drivers",
    status: "NOMINAL",
  },
  // 3. Buffer Warehouses (4 nodes)
  {
    id: "wh-01",
    name: "Hosur Logistics Buffer Warehouse",
    type: "warehouse",
    location: "Hosur, TN / KA Border",
    coords: "12.7409 N, 77.8253 E",
    x: 320,
    y: 220,
    details: "Capacity: 75,000 units | Primary NH48 Gateway Buffer",
    status: "NOMINAL",
  },
  {
    id: "wh-02",
    name: "Whitefield Inland Container Depot",
    type: "warehouse",
    location: "Whitefield, Bengaluru, KA",
    coords: "12.9698 N, 77.7500 E",
    x: 310,
    y: 135,
    details: "Capacity: 50,000 units | Intermodal Rail & ICD Logistics",
    status: "NOMINAL",
  },
  {
    id: "wh-03",
    name: "Oragadam JIT Supplier Warehouse",
    type: "warehouse",
    location: "Oragadam Industrial Corridor, TN",
    coords: "12.8342 N, 79.9197 E",
    x: 580,
    y: 315,
    details: "Capacity: 60,000 units | JIT Automotive Feeder to Sriperumbudur",
    status: "NOMINAL",
  },
  {
    id: "wh-04",
    name: "Sri City FTWZ Logistics Center",
    type: "warehouse",
    location: "Sri City FTWZ, AP",
    coords: "13.5298 N, 80.0244 E",
    x: 650,
    y: 105,
    details: "Capacity: 40,000 units | Duty-Free Customs Buffer Hub",
    status: "NOMINAL",
  },
  // 4. Multimodal Gateways (3 nodes)
  {
    id: "dc-01",
    name: "Chennai Port Container Terminal",
    type: "dc",
    location: "Chennai Port, TN",
    coords: "13.0827 N, 80.2937 E",
    x: 770,
    y: 180,
    details: "Maritime Deep-Water Gateway | Coromandel Coast Outbound",
    status: "NOMINAL",
  },
  {
    id: "dc-02",
    name: "Cochin Port Vallarpadam Terminal",
    type: "dc",
    location: "Vallarpadam ICTT, Kochi, KL",
    coords: "9.9674 N, 76.2429 E",
    x: 210,
    y: 395,
    details: "International Transshipment Terminal | Arabian Sea Hub",
    status: "NOMINAL",
  },
  {
    id: "dc-03",
    name: "Hyderabad Air Cargo Gateway",
    type: "dc",
    location: "Shamshabad Aerotropolis, Hyderabad, TS",
    coords: "17.2403 N, 78.4294 E",
    x: 480,
    y: 50,
    details: "High-Priority Air Freight Transshipment Terminal",
    status: "NOMINAL",
  },
];

export const OperationsView: React.FC<OperationsViewProps> = ({ onSelectDecision }) => {
  const dashboardState = useDashboardState();
  const [persistedDecisions, setPersistedDecisions] = useState<DecisionRecord[]>([]);
  const [activeNode, setActiveNode] = useState<TopologyNode | null>(TOPOLOGY_NODES[0]);

  useEffect(() => {
    let mounted = true;
    apiClient
      .listDecisions()
      .then((data: DecisionRecord[]) => {
        if (mounted && Array.isArray(data)) {
          setPersistedDecisions(data);
        }
      })
      .catch(() => {
        // Fallback
      });
    return () => {
      mounted = false;
    };
  }, []);

  const recentDecisions = persistedDecisions.slice(0, 4);

  return (
    <div className={styles.container}>
      {/* KPI Metric Cards */}
      <section className={styles.metricsGrid}>
        <div className={styles.metricCard}>
          <span className={styles.metricLabel}>Supply Chain Reliability</span>
          <div className={styles.metricValueRow}>
            <span className={styles.metricValue}>
              {dashboardState?.system_health ? "96.4%" : "95.8%"}
            </span>
            <span className={styles.metricSubtext}>+1.2% vs target</span>
          </div>
        </div>

        <div className={styles.metricCard}>
          <span className={styles.metricLabel}>Inventory Stock Coverage</span>
          <div className={styles.metricValueRow}>
            <span className={styles.metricValue}>18.4 d</span>
            <span className={styles.metricSubtextWarning}>Safety threshold: 14d</span>
          </div>
        </div>

        <div className={styles.metricCard}>
          <span className={styles.metricLabel}>Active Disruption Risk</span>
          <div className={styles.metricValueRow}>
            <span className={styles.metricValue}>
              {recentDecisions.length > 0 ? "ELEVATED" : "NOMINAL"}
            </span>
            <span className={recentDecisions.length > 0 ? styles.metricSubtextWarning : styles.metricSubtext}>
              {recentDecisions.length > 0 ? "Active arbitration" : "All nodes stable"}
            </span>
          </div>
        </div>

        <div className={styles.metricCard}>
          <span className={styles.metricLabel}>Specialist Agents Online</span>
          <div className={styles.metricValueRow}>
            <span className={styles.metricValue}>4 / 4</span>
            <span className={styles.metricSubtext}>A2A Discovery OK</span>
          </div>
        </div>
      </section>

      {/* Main Grid: Supply Chain Map / Topology + Live Alerts / Decisions */}
      <div className={styles.mainGrid}>
        {/* Topology Visualizer */}
        <section className={styles.topologySection}>
          <div className={styles.sectionHeader}>
            <span className={styles.sectionTitle}>Peninsular India High-Tech Supply Topology</span>
            <span className={styles.sectionBadge}>SOUTH INDIAN ELECTRONICS CORRIDOR</span>
          </div>

          <div className={styles.topologyLegend}>
            <div className={styles.legendItem}>
              <span className={styles.legendDot} style={{ background: "#ff9f0a" }} />
              <span>Assembly Hub</span>
            </div>
            <div className={styles.legendItem}>
              <span className={styles.legendDot} style={{ background: "#0a84ff" }} />
              <span>Tier-1 Component Suppliers</span>
            </div>
            <div className={styles.legendItem}>
              <span className={styles.legendDot} style={{ background: "#af52de" }} />
              <span>Buffer Warehouses & ICDs</span>
            </div>
            <div className={styles.legendItem}>
              <span className={styles.legendDot} style={{ background: "#30d158" }} />
              <span>Multimodal Export Gateways</span>
            </div>
            <div className={styles.legendItem}>
              <span style={{ width: 14, height: 2, background: "#0a84ff", display: "inline-block" }} />
              <span>NH48 Freight Spine</span>
            </div>
          </div>

          <div className={styles.topologyVisualizer}>
            <svg width="100%" height="100%" viewBox="0 0 920 460" preserveAspectRatio="xMidYMid meet">
              <defs>
                <linearGradient id="routeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="#0a84ff" stopOpacity="0.8" />
                  <stop offset="100%" stopColor="#64d2ff" stopOpacity="0.8" />
                </linearGradient>
                <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                  <feGaussianBlur stdDeviation="3.5" result="coloredBlur" />
                  <feMerge>
                    <feMergeNode in="coloredBlur" />
                    <feMergeNode in="SourceGraphic" />
                  </feMerge>
                </filter>
                <filter id="hubGlow" x="-30%" y="-30%" width="160%" height="160%">
                  <feGaussianBlur stdDeviation="5" result="coloredBlur" />
                  <feMerge>
                    <feMergeNode in="coloredBlur" />
                    <feMergeNode in="SourceGraphic" />
                  </feMerge>
                </filter>
              </defs>

              {/* Corridor Route lines */}
              {/* NH48 Interstate Arterial Freight Spine (Glowing Blue) */}
              <path
                d="M 320 220 L 430 220 L 580 220"
                stroke="#0a84ff"
                strokeWidth="3.5"
                fill="none"
                filter="url(#glow)"
              />

              {/* Mysuru to Bengaluru links */}
              <path
                d="M 90 170 Q 160 160 230 180"
                stroke="rgba(255,255,255,0.18)"
                strokeWidth="1.5"
                strokeDasharray="4 4"
                fill="none"
              />
              <path
                d="M 90 250 Q 160 230 230 180"
                stroke="rgba(255,255,255,0.18)"
                strokeWidth="1.5"
                strokeDasharray="4 4"
                fill="none"
              />

              {/* Bengaluru Microelectronics Feeder links */}
              <path
                d="M 230 105 L 310 135"
                stroke="rgba(255,255,255,0.2)"
                strokeWidth="1.5"
                fill="none"
              />
              <path
                d="M 230 180 L 320 220"
                stroke="#0a84ff"
                strokeWidth="2"
                fill="none"
              />
              <path
                d="M 310 135 L 320 220"
                stroke="#0a84ff"
                strokeWidth="2"
                strokeDasharray="3 3"
                fill="none"
              />

              {/* Southern Kerala Corridor (Kochi) */}
              <path
                d="M 130 350 L 210 395"
                stroke="#30d158"
                strokeWidth="1.5"
                fill="none"
              />
              <path
                d="M 210 395 Q 260 300 320 220"
                stroke="rgba(255,255,255,0.18)"
                strokeWidth="1.5"
                strokeDasharray="4 4"
                fill="none"
              />

              {/* Northern Hyderabad Corridor */}
              <path
                d="M 390 50 L 480 50"
                stroke="#64d2ff"
                strokeWidth="1.5"
                fill="none"
              />
              <path
                d="M 480 50 Q 580 60 650 105"
                stroke="rgba(255,255,255,0.18)"
                strokeWidth="1.5"
                strokeDasharray="4 4"
                fill="none"
              />

              {/* Sri City FTWZ Buffer Feed to Sriperumbudur */}
              <path
                d="M 650 105 Q 630 160 580 220"
                stroke="#af52de"
                strokeWidth="2"
                fill="none"
              />

              {/* Maraimalai Nagar & Oragadam JIT Cluster */}
              <path
                d="M 690 290 L 580 315"
                stroke="rgba(255,255,255,0.2)"
                strokeWidth="1.5"
                fill="none"
              />
              <path
                d="M 580 315 L 580 220"
                stroke="#30d158"
                strokeWidth="2.5"
                fill="none"
              />

              {/* Outbound Corridors to Sea & Air Gateways */}
              <path
                d="M 580 220 Q 670 190 770 180"
                stroke="#30d158"
                strokeWidth="2.5"
                fill="none"
                filter="url(#glow)"
              />
              <path
                d="M 580 220 Q 420 340 210 395"
                stroke="rgba(48,209,88,0.5)"
                strokeWidth="1.5"
                strokeDasharray="5 5"
                fill="none"
              />
              <path
                d="M 580 220 Q 520 120 480 50"
                stroke="rgba(100,210,255,0.5)"
                strokeWidth="1.5"
                strokeDasharray="5 5"
                fill="none"
              />

              {/* Render Nodes */}
              {TOPOLOGY_NODES.map((node) => {
                const isSelected = activeNode?.id === node.id;
                const isMfg = node.type === "manufacturer";
                const isWh = node.type === "warehouse";
                const isDc = node.type === "dc";

                return (
                  <g
                    key={node.id}
                    transform={`translate(${node.x}, ${node.y})`}
                    style={{ cursor: "pointer" }}
                    onClick={() => setActiveNode(node)}
                    onMouseEnter={() => setActiveNode(node)}
                  >
                    {isMfg ? (
                      <>
                        <circle
                          r="28"
                          fill="none"
                          stroke="#ff9f0a"
                          strokeWidth="1"
                          opacity="0.3"
                          filter="url(#hubGlow)"
                        />
                        <rect
                          x="-22"
                          y="-22"
                          width="44"
                          height="44"
                          rx="10"
                          fill="#181b24"
                          stroke="#ff9f0a"
                          strokeWidth={isSelected ? 3 : 2}
                          filter="url(#hubGlow)"
                        />
                        <text
                          x="0"
                          y="4"
                          fill="#f5f5f7"
                          fontSize="11"
                          fontWeight="700"
                          textAnchor="middle"
                          fontFamily="-apple-system, sans-serif"
                        >
                          MFG-01
                        </text>
                        <text
                          x="0"
                          y="34"
                          fill="#ff9f0a"
                          fontSize="10"
                          fontWeight="600"
                          textAnchor="middle"
                          fontFamily="-apple-system, sans-serif"
                        >
                          Sriperumbudur
                        </text>
                      </>
                    ) : isWh ? (
                      <>
                        <rect
                          x="-14"
                          y="-14"
                          width="28"
                          height="28"
                          rx="6"
                          fill="#141720"
                          stroke="#af52de"
                          strokeWidth={isSelected ? 2.5 : 1.8}
                        />
                        <circle r="4" fill="#af52de" />
                        <text
                          x="0"
                          y="24"
                          fill="#d084f8"
                          fontSize="9.5"
                          fontWeight="500"
                          textAnchor="middle"
                          fontFamily="-apple-system, sans-serif"
                        >
                          {node.id.toUpperCase()}
                        </text>
                      </>
                    ) : isDc ? (
                      <>
                        <circle
                          r="15"
                          fill="#141720"
                          stroke="#30d158"
                          strokeWidth={isSelected ? 2.5 : 1.8}
                        />
                        <circle r="5" fill="#30d158" />
                        <text
                          x="0"
                          y="24"
                          fill="#30d158"
                          fontSize="9.5"
                          fontWeight="500"
                          textAnchor="middle"
                          fontFamily="-apple-system, sans-serif"
                        >
                          {node.id.toUpperCase()}
                        </text>
                      </>
                    ) : (
                      <>
                        <circle
                          r="13"
                          fill="#141720"
                          stroke="#0a84ff"
                          strokeWidth={isSelected ? 2.5 : 1.5}
                        />
                        <circle r="4" fill={isSelected ? "#64d2ff" : "#0a84ff"} />
                        <text
                          x="0"
                          y="22"
                          fill="#a1a1a6"
                          fontSize="9"
                          fontWeight="500"
                          textAnchor="middle"
                          fontFamily="-apple-system, sans-serif"
                        >
                          {node.id.toUpperCase()}
                        </text>
                      </>
                    )}
                  </g>
                );
              })}
            </svg>

            {/* Interactive Node Telemetry HUD */}
            {activeNode && (
              <div className={styles.nodeDetailsHud}>
                <div>
                  <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <span
                      style={{
                        fontSize: "12px",
                        fontFamily: "var(--font-mono)",
                        fontWeight: 700,
                        color:
                          activeNode.type === "manufacturer"
                            ? "#ff9f0a"
                            : activeNode.type === "warehouse"
                            ? "#af52de"
                            : activeNode.type === "dc"
                            ? "#30d158"
                            : "#0a84ff",
                      }}
                    >
                      [{activeNode.id.toUpperCase()}]
                    </span>
                    <span style={{ fontSize: "12px", fontWeight: 600, color: "var(--text-primary)" }}>
                      {activeNode.name}
                    </span>
                    <span style={{ fontSize: "11px", color: "var(--text-muted)" }}>
                      ({activeNode.location})
                    </span>
                  </div>
                  <div style={{ fontSize: "11px", color: "var(--text-secondary)", marginTop: 2 }}>
                    {activeNode.details} • Coordinates: {activeNode.coords}
                  </div>
                </div>
                <div style={{ textAlign: "right" }}>
                  <span
                    style={{
                      fontSize: "10px",
                      fontFamily: "var(--font-mono)",
                      padding: "2px 8px",
                      borderRadius: 99,
                      background: "rgba(48,209,88,0.12)",
                      color: "var(--apple-green)",
                      border: "1px solid rgba(48,209,88,0.25)",
                    }}
                  >
                    STATUS: {activeNode.status}
                  </span>
                </div>
              </div>
            )}
          </div>
        </section>

        {/* Side Panel: Alerts & Recent Decisions */}
        <div className={styles.sideSection}>
          <div className={styles.alertsCard}>
            <div className={styles.sectionHeader}>
              <span className={styles.sectionTitle}>Operational Alerts</span>
              <span className={styles.sectionBadge}>LIVE</span>
            </div>

            {recentDecisions.length > 0 ? (
              <div className={styles.alertItem}>
                <div className={styles.alertHeader}>
                  <span>SCENARIO {recentDecisions[0].scenario_id.toUpperCase()}</span>
                  <span style={{ color: "var(--accent-red)" }}>ACTIVE</span>
                </div>
                <div className={styles.alertText}>
                  Consensus generated winning arbitration for component reorder. Escalation Tier: {recentDecisions[0].escalation_tier}.
                </div>
              </div>
            ) : (
              <div className={styles.alertItemSuccess}>
                <div className={styles.alertHeader}>
                  <span>ALL SYSTEMS NORMAL</span>
                  <span style={{ color: "var(--accent-green)" }}>NOMINAL</span>
                </div>
                <div className={styles.alertText}>
                  All nodes stable across peninsular corridors. Real-time agent monitoring listening on Kafka bus.
                </div>
              </div>
            )}
          </div>

          <div className={styles.decisionsCard}>
            <div className={styles.sectionHeader}>
              <span className={styles.sectionTitle}>Recent Decisions</span>
              <span className={styles.sectionBadge}>{recentDecisions.length} TOTAL</span>
            </div>

            <div className={styles.decisionList}>
              {recentDecisions.map((dec: DecisionRecord) => (
                <div
                  key={dec.decision_id}
                  className={styles.decisionRow}
                  onClick={() => onSelectDecision?.(dec.decision_id)}
                  style={{ cursor: onSelectDecision ? "pointer" : "default" }}
                >
                  <div className={styles.decisionMeta}>
                    <span className={styles.scenarioTag}>{dec.scenario_id}</span>
                    <span
                      className={`${styles.tierBadge} ${
                        dec.escalation_tier === "HUMAN_ESCALATION"
                          ? styles.tierEscalated
                          : styles.tierFast
                      }`}
                    >
                      {dec.escalation_tier}
                    </span>
                  </div>
                  <div className={styles.decisionRec}>
                    {dec.final_recommendation || "No recommendation"}
                  </div>
                  <div className={styles.decisionFooter}>
                    <span>Confidence: {(dec.decision_confidence * 100).toFixed(1)}%</span>
                    <span>Method: {dec.decision_method || "CD2F"}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
