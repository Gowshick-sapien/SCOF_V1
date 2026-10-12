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
  spec: string;
  corridor: string;
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
    spec: "Tier-0 Assembly Anchor - 120k units/mo capacity",
    corridor: "NH48 Main Spine & Port Connectors",
    status: "NOMINAL",
  },
  // 2. Tier-1 Suppliers (8 nodes)
  {
    id: "sup-01",
    name: "SPEL Semiconductor",
    type: "supplier",
    location: "Maraimalai Nagar, Chennai, TN",
    coords: "12.7937 N, 80.0242 E",
    x: 690,
    y: 290,
    spec: "WLCSP IC Packaging & Test Fab - 5d lead time",
    corridor: "Maraimalai Nagar - Oragadam Feeder",
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
    spec: "Discrete Power Semiconductors - 6d lead time",
    corridor: "Electronic City - Hosur Feeder",
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
    spec: "Automotive Telematics & IoT EMS - 8d lead time",
    corridor: "Mysuru - Bengaluru Feeder",
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
    spec: "High-Precision SMT Assemblies - 7d lead time",
    corridor: "NH48 Bargur Arterial Corridor",
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
    spec: "Microelectronics & Converters - 9d lead time",
    corridor: "Yelahanka - Whitefield Feeder",
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
    spec: "Power Electronics & SMT - 12d lead time",
    corridor: "Hebbal - Bengaluru Feeder",
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
    spec: "Fiber Optics & Control Modules - 7d lead time",
    corridor: "Kochi - Vallarpadam Feeder",
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
    spec: "High-Layer PCB Fabrication - 10d lead time",
    corridor: "Hyderabad - Shamshabad Feeder",
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
    spec: "Buffer Capacity: 75,000 units",
    corridor: "NH48 Interstate Arterial Junction",
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
    spec: "Buffer Capacity: 50,000 units - Intermodal Rail",
    corridor: "Whitefield ICD Feeder Link",
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
    spec: "Buffer Capacity: 60,000 units - JIT Feeder",
    corridor: "Oragadam JIT Automotive Feeder",
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
    spec: "Buffer Capacity: 40,000 units - Duty-Free Customs Hub",
    corridor: "Sri City FTWZ Bonded Connector",
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
    spec: "Maritime Deep-Water Gateway - Coromandel Coast Outbound",
    corridor: "Sriperumbudur - Chennai Port Export Lane",
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
    spec: "International Transshipment Terminal - Arabian Sea Hub",
    corridor: "South Peninsular Export Lane",
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
    spec: "High-Priority Air Freight Transshipment Gateway",
    corridor: "North Peninsular Air Freight Express Lane",
    status: "NOMINAL",
  },
];

export const OperationsView: React.FC<OperationsViewProps> = ({ onSelectDecision }) => {
  const dashboardState = useDashboardState();
  const [persistedDecisions, setPersistedDecisions] = useState<DecisionRecord[]>([]);
  const [activeNode, setActiveNode] = useState<TopologyNode>(TOPOLOGY_NODES[0]);

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
  const activeDisruptionCount = recentDecisions.filter(
    (d) => d.escalation_tier === "HUMAN_ESCALATION" || d.decision_confidence < 0.8
  ).length;

  return (
    <div className={styles.container}>
      {/* 4 Disciplined Operational KPI Cards */}
      <section className={styles.metricsGrid}>
        <div className={styles.metricCard}>
          <div className={styles.metricHeader}>
            <span className={styles.metricLabel}>Supply Chain Reliability</span>
          </div>
          <div className={styles.metricValue}>
            {dashboardState?.system_health ? "96.4%" : "95.8%"}
          </div>
          <div className={`${styles.metricBenchmark} ${styles.metricBenchmarkSuccess}`}>
            +1.2% vs 95.0% baseline
          </div>
        </div>

        <div className={styles.metricCard}>
          <div className={styles.metricHeader}>
            <span className={styles.metricLabel}>Inventory Stock Coverage</span>
          </div>
          <div className={styles.metricValue}>18.4 d</div>
          <div className={`${styles.metricBenchmark} ${styles.metricBenchmarkNeutral}`}>
            Safety buffer: 14.0 d
          </div>
        </div>

        <div className={styles.metricCard}>
          <div className={styles.metricHeader}>
            <span className={styles.metricLabel}>Outbound Flow Status</span>
          </div>
          <div className={styles.metricValue}>NOMINAL</div>
          <div className={`${styles.metricBenchmark} ${styles.metricBenchmarkSuccess}`}>
            All 3 export gateways operational
          </div>
        </div>

        <div className={styles.metricCard}>
          <div className={styles.metricHeader}>
            <span className={styles.metricLabel}>Active Disruption Risk</span>
          </div>
          <div className={styles.metricValue}>
            {activeDisruptionCount > 0 ? "ELEVATED" : "NOMINAL"}
          </div>
          <div
            className={`${styles.metricBenchmark} ${
              activeDisruptionCount > 0
                ? styles.metricBenchmarkWarning
                : styles.metricBenchmarkSuccess
            }`}
          >
            {activeDisruptionCount > 0
              ? `${activeDisruptionCount} Active CD2F arbitration`
              : "Zero unmitigated halts"}
          </div>
        </div>
      </section>

      {/* Main Grid: Left Topology Schematic + Right Side Inspector */}
      <div className={styles.mainGrid}>
        {/* Topology Schematic Section */}
        <section className={styles.topologySection}>
          <div className={styles.sectionHeader}>
            <span className={styles.sectionTitle}>Peninsular India High-Tech Supply Topology</span>
            <span className={styles.sectionBadge}>SOUTH INDIAN ELECTRONICS CORRIDOR</span>
          </div>

          {/* Clean Vector Legend */}
          <div className={styles.topologyLegend}>
            <div className={styles.legendGroup}>
              <div className={styles.legendItem}>
                <span
                  className={styles.legendIcon}
                  style={{ background: "#171D26", border: "1.5px solid #E9B45C", borderRadius: 2 }}
                />
                <span>Assembly Hub</span>
              </div>
              <div className={styles.legendItem}>
                <span
                  className={styles.legendIcon}
                  style={{ background: "#171D26", border: "1.5px solid #45A9F3", borderRadius: "50%" }}
                />
                <span>Suppliers</span>
              </div>
              <div className={styles.legendItem}>
                <span
                  className={styles.legendIcon}
                  style={{ background: "#171D26", border: "1.5px solid #A78BFA", borderRadius: 2 }}
                />
                <span>Warehouses</span>
              </div>
              <div className={styles.legendItem}>
                <span
                  className={styles.legendIcon}
                  style={{ background: "#171D26", border: "1.5px solid #16A67E", borderRadius: "50%" }}
                />
                <span>Export Ports</span>
              </div>
            </div>

            <div className={styles.legendGroup}>
              <div className={styles.legendItem}>
                <span className={styles.legendLine} style={{ background: "#0E82D6", height: 2.5 }} />
                <span>NH48 Spine</span>
              </div>
              <div className={styles.legendItem}>
                <span className={styles.legendLine} style={{ background: "#16A67E", height: 2 }} />
                <span>Export Lanes</span>
              </div>
              <div className={styles.legendItem}>
                <span
                  className={styles.legendLine}
                  style={{
                    borderTop: "1.5px dashed #455264",
                    background: "transparent",
                    height: 0,
                  }}
                />
                <span>Feeder Lanes</span>
              </div>
            </div>
          </div>

          {/* Clean SVG Canvas without blur or glowing halos */}
          <div className={styles.topologyCanvas}>
            <svg width="100%" height="100%" viewBox="0 0 920 460" preserveAspectRatio="xMidYMid meet">
              {/* Corridor Route Paths */}

              {/* 1. NH48 Interstate Arterial Freight Spine (Solid 2.5px Brand Blue) */}
              <path
                d="M 320 220 L 430 220 L 580 220"
                stroke="#0E82D6"
                strokeWidth="2.5"
                fill="none"
              />

              {/* 2. Mysuru to Bengaluru Feeder Links (Dashed 1.5px Slate) */}
              <path
                d="M 90 170 Q 160 160 230 180"
                stroke="#455264"
                strokeWidth="1.5"
                strokeDasharray="4 4"
                fill="none"
              />
              <path
                d="M 90 250 Q 160 230 230 180"
                stroke="#455264"
                strokeWidth="1.5"
                strokeDasharray="4 4"
                fill="none"
              />

              {/* 3. Bengaluru Microelectronics Feeder Links */}
              <path
                d="M 230 105 L 310 135"
                stroke="#455264"
                strokeWidth="1.5"
                strokeDasharray="4 4"
                fill="none"
              />
              <path
                d="M 230 180 L 320 220"
                stroke="#0E82D6"
                strokeWidth="1.8"
                fill="none"
              />
              <path
                d="M 310 135 L 320 220"
                stroke="#455264"
                strokeWidth="1.5"
                strokeDasharray="4 4"
                fill="none"
              />

              {/* 4. Southern Kerala Corridor (Kochi ICTT) */}
              <path
                d="M 130 350 L 210 395"
                stroke="#455264"
                strokeWidth="1.5"
                strokeDasharray="4 4"
                fill="none"
              />
              <path
                d="M 210 395 Q 260 300 320 220"
                stroke="#455264"
                strokeWidth="1.5"
                strokeDasharray="4 4"
                fill="none"
              />

              {/* 5. Northern Hyderabad Air Corridor */}
              <path
                d="M 390 50 L 480 50"
                stroke="#455264"
                strokeWidth="1.5"
                strokeDasharray="4 4"
                fill="none"
              />
              <path
                d="M 480 50 Q 580 60 650 105"
                stroke="#455264"
                strokeWidth="1.5"
                strokeDasharray="4 4"
                fill="none"
              />

              {/* 6. Sri City FTWZ Bonded Connector */}
              <path
                d="M 650 105 Q 630 160 580 220"
                stroke="#64748B"
                strokeWidth="2"
                fill="none"
              />

              {/* 7. Maraimalai Nagar & Oragadam JIT Cluster */}
              <path
                d="M 690 290 L 580 315"
                stroke="#455264"
                strokeWidth="1.5"
                strokeDasharray="4 4"
                fill="none"
              />
              <path
                d="M 580 315 L 580 220"
                stroke="#16A67E"
                strokeWidth="2"
                fill="none"
              />

              {/* 8. Finished Goods Export Lanes to Sea & Air Gateways (Solid 2px Brand Teal) */}
              <path
                d="M 580 220 Q 670 190 770 180"
                stroke="#16A67E"
                strokeWidth="2"
                fill="none"
              />
              <path
                d="M 580 220 Q 420 340 210 395"
                stroke="#16A67E"
                strokeWidth="1.5"
                strokeDasharray="4 4"
                fill="none"
              />
              <path
                d="M 580 220 Q 520 120 480 50"
                stroke="#16A67E"
                strokeWidth="1.5"
                strokeDasharray="4 4"
                fill="none"
              />

              {/* Geometric Node Markers */}
              {TOPOLOGY_NODES.map((node) => {
                const isSelected = activeNode.id === node.id;
                const isMfg = node.type === "manufacturer";
                const isWh = node.type === "warehouse";
                const isDc = node.type === "dc";

                return (
                  <g
                    key={node.id}
                    transform={`translate(${node.x}, ${node.y})`}
                    style={{ cursor: "pointer" }}
                    onClick={() => setActiveNode(node)}
                  >
                    {isMfg ? (
                      <>
                        <rect
                          x="-20"
                          y="-20"
                          width="40"
                          height="40"
                          rx="6"
                          fill="#171D26"
                          stroke="#E9B45C"
                          strokeWidth={isSelected ? 2.5 : 1.5}
                        />
                        <text
                          x="0"
                          y="4"
                          fill="#F2F5F8"
                          fontSize="10"
                          fontWeight="700"
                          textAnchor="middle"
                          fontFamily="var(--font-sans)"
                        >
                          MFG-01
                        </text>
                        <text
                          x="0"
                          y="32"
                          fill="#E9B45C"
                          fontSize="9.5"
                          fontWeight="600"
                          textAnchor="middle"
                          fontFamily="var(--font-sans)"
                        >
                          Sriperumbudur
                        </text>
                      </>
                    ) : isWh ? (
                      <>
                        <rect
                          x="-12"
                          y="-12"
                          width="24"
                          height="24"
                          rx="4"
                          fill="#171D26"
                          stroke={isSelected ? "#C4B5FD" : "#A78BFA"}
                          strokeWidth={isSelected ? 2.5 : 1.5}
                        />
                        <circle r="2.5" fill="#A78BFA" />
                        <text
                          x="0"
                          y="22"
                          fill="#AAB6C4"
                          fontSize="9"
                          fontWeight="500"
                          textAnchor="middle"
                          fontFamily="var(--font-sans)"
                        >
                          {node.id.toUpperCase()}
                        </text>
                      </>
                    ) : isDc ? (
                      <>
                        <circle
                          r="14"
                          fill="#171D26"
                          stroke={isSelected ? "#48C69A" : "#16A67E"}
                          strokeWidth={isSelected ? 2.5 : 1.5}
                        />
                        <circle
                          r="6"
                          fill="none"
                          stroke="#16A67E"
                          strokeWidth="1.2"
                        />
                        <circle r="2" fill="#16A67E" />
                        <text
                          x="0"
                          y="24"
                          fill="#16A67E"
                          fontSize="9"
                          fontWeight="500"
                          textAnchor="middle"
                          fontFamily="var(--font-sans)"
                        >
                          {node.id.toUpperCase()}
                        </text>
                      </>
                    ) : (
                      <>
                        <circle
                          r="12"
                          fill="#171D26"
                          stroke={isSelected ? "#60A5FA" : "#45A9F3"}
                          strokeWidth={isSelected ? 2.5 : 1.5}
                        />
                        <circle r="3.5" fill={isSelected ? "#60A5FA" : "#45A9F3"} />
                        <text
                          x="0"
                          y="21"
                          fill="#AAB6C4"
                          fontSize="8.5"
                          fontWeight="500"
                          textAnchor="middle"
                          fontFamily="var(--font-sans)"
                        >
                          {node.id.toUpperCase()}
                        </text>
                      </>
                    )}
                  </g>
                );
              })}
            </svg>
          </div>
        </section>

        {/* Right Side Inspector & Operational Alerts Panel */}
        <div className={styles.sideSection}>
          {/* Contextual Facility Entity Inspector */}
          <div className={styles.inspectorCard}>
            <div className={styles.inspectorHeader}>
              <div className={styles.inspectorTitle}>
                <span>Facility: {activeNode.id.toUpperCase()}</span>
                <span
                  className={styles.nodeTypeBadge}
                  style={{
                    backgroundColor:
                      activeNode.type === "manufacturer"
                        ? "rgba(233, 180, 92, 0.15)"
                        : activeNode.type === "warehouse"
                        ? "rgba(167, 139, 250, 0.15)"
                        : activeNode.type === "dc"
                        ? "rgba(22, 166, 126, 0.15)"
                        : "rgba(69, 169, 243, 0.15)",
                    color:
                      activeNode.type === "manufacturer"
                        ? "#E9B45C"
                        : activeNode.type === "warehouse"
                        ? "#A78BFA"
                        : activeNode.type === "dc"
                        ? "#16A67E"
                        : "#45A9F3",
                  }}
                >
                  {activeNode.type}
                </span>
              </div>
              <span className={`${styles.statusBadge} ${styles.statusNominal}`}>
                {activeNode.status}
              </span>
            </div>

            <div className={styles.inspectorGrid}>
              <span className={styles.inspectorLabel}>Facility Name</span>
              <span className={styles.inspectorValue}>{activeNode.name}</span>

              <span className={styles.inspectorLabel}>Location</span>
              <span className={styles.inspectorValue}>{activeNode.location}</span>

              <span className={styles.inspectorLabel}>Coordinates</span>
              <span className={styles.inspectorValue}>{activeNode.coords}</span>

              <span className={styles.inspectorLabel}>Operational Spec</span>
              <span className={styles.inspectorValue}>{activeNode.spec}</span>

              <span className={styles.inspectorLabel}>Corridor Link</span>
              <span className={styles.inspectorValue}>{activeNode.corridor}</span>
            </div>
            <span className={styles.inspectorHint}>
              Click any node in topology schematic to inspect facility parameters.
            </span>
          </div>

          {/* Operational Alerts & Live Decision Queue */}
          <div className={styles.alertsCard}>
            <div className={styles.sectionHeader}>
              <span className={styles.sectionTitle}>Operational Alert Queue</span>
              <span className={styles.sectionBadge}>
                {recentDecisions.length > 0 ? "LIVE" : "NOMINAL"}
              </span>
            </div>

            {recentDecisions.length > 0 ? (
              <div className={`${styles.alertBanner} ${styles.alertBannerActive}`}>
                <div className={`${styles.alertHeader} ${styles.alertHeaderActive}`}>
                  <span>SCENARIO {recentDecisions[0].scenario_id.toUpperCase()}</span>
                  <span>ACTIVE ARBITRATION</span>
                </div>
                <div className={styles.alertDescription}>
                  Consensus generated winning arbitration for component reorder. Escalation Tier: {recentDecisions[0].escalation_tier}.
                </div>
              </div>
            ) : (
              <div className={`${styles.alertBanner} ${styles.alertBannerSuccess}`}>
                <div className={`${styles.alertHeader} ${styles.alertHeaderSuccess}`}>
                  <span>ALL SYSTEMS NOMINAL</span>
                  <span>NOMINAL</span>
                </div>
                <div className={styles.alertDescription}>
                  Zero unmitigated corridor disruptions. Multi-agent monitoring listening on Kafka bus.
                </div>
              </div>
            )}

            <div className={styles.decisionsSection}>
              <div className={styles.decisionsHeader}>
                <span>Recent Deliberated Decisions</span>
                <span className={styles.decisionsCount}>
                  {recentDecisions.length} RECORDS
                </span>
              </div>

              {recentDecisions.length === 0 ? (
                <div className={styles.emptyState}>No recent decisions recorded yet.</div>
              ) : (
                <div className={styles.decisionList}>
                  {recentDecisions.map((dec) => (
                    <div
                      key={dec.decision_id}
                      className={styles.decisionRow}
                      onClick={() => onSelectDecision?.(dec.decision_id)}
                      title="Inspect Decision Details"
                    >
                      <div className={styles.decisionMeta}>
                        <span className={styles.scenarioTag}>{dec.scenario_id}</span>
                        <span
                          className={`${styles.tierTag} ${
                            dec.escalation_tier === "HUMAN_ESCALATION"
                              ? styles.tierEscalated
                              : styles.tierFast
                          }`}
                        >
                          {dec.escalation_tier}
                        </span>
                      </div>
                      <div className={styles.decisionRec}>
                        {dec.final_recommendation || "Consensus action recommended"}
                      </div>
                      <div className={styles.decisionFooter}>
                        <span className={styles.confidenceVal}>
                          Confidence: {(dec.decision_confidence * 100).toFixed(1)}%
                        </span>
                        <span>{dec.decision_method || "CD2F"}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
