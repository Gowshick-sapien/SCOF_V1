import React, { useEffect, useState } from "react";
import styles from "./Operations.module.css";
import { useDashboardState } from "../../hooks/useDashboardState";
import { apiClient } from "../../api/client";
import type { DecisionRecord } from "../../api/types";

interface OperationsViewProps {
  onSelectDecision?: (decisionId: string) => void;
}

export const OperationsView: React.FC<OperationsViewProps> = ({ onSelectDecision }) => {
  const dashboardState = useDashboardState();
  const [persistedDecisions, setPersistedDecisions] = useState<DecisionRecord[]>([]);

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
            <span className={styles.sectionTitle}>Global Supply Network Topology</span>
            <span className={styles.sectionBadge}>MVP-ELECTRONICS REGION</span>
          </div>

          <div className={styles.topologyVisualizer}>
            <svg width="100%" height="100%" viewBox="0 0 680 340" preserveAspectRatio="xMidYMid meet">
              <defs>
                <linearGradient id="routeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="#38bdf8" stopOpacity="0.8" />
                  <stop offset="100%" stopColor="#3b82f6" stopOpacity="0.8" />
                </linearGradient>
                <filter id="glow">
                  <feGaussianBlur stdDeviation="3" result="coloredBlur" />
                  <feMerge>
                    <feMergeNode in="coloredBlur" />
                    <feMergeNode in="SourceGraphic" />
                  </feMerge>
                </filter>
              </defs>

              {/* Route lines */}
              <path d="M 120 80 Q 240 120 340 160" stroke="#334155" strokeWidth="2" strokeDasharray="4 4" fill="none" />
              <path d="M 120 180 Q 240 170 340 160" stroke="#38bdf8" strokeWidth="2.5" fill="none" filter="url(#glow)" />
              <path d="M 120 280 Q 240 220 340 160" stroke="#334155" strokeWidth="2" strokeDasharray="4 4" fill="none" />
              <path d="M 340 160 Q 440 140 540 110" stroke="#10b981" strokeWidth="2.5" fill="none" />
              <path d="M 340 160 Q 440 190 540 230" stroke="#10b981" strokeWidth="2.5" fill="none" />

              {/* Tier 1 Suppliers */}
              <g transform="translate(120, 80)">
                <circle r="16" fill="#1e293b" stroke="#64748b" strokeWidth="2" />
                <circle r="6" fill="#64748b" />
                <text x="-50" y="-22" fill="#94a3b8" fontSize="11" fontFamily="sans-serif">Global Silicon (sup-01)</text>
              </g>

              <g transform="translate(120, 180)">
                <circle r="18" fill="#1e293b" stroke="#38bdf8" strokeWidth="2.5" filter="url(#glow)" />
                <circle r="7" fill="#38bdf8" />
                <text x="-50" y="-24" fill="#38bdf8" fontWeight="bold" fontSize="11" fontFamily="sans-serif">Pacific Semi (sup-02)</text>
              </g>

              <g transform="translate(120, 280)">
                <circle r="16" fill="#1e293b" stroke="#64748b" strokeWidth="2" />
                <circle r="6" fill="#64748b" />
                <text x="-50" y="32" fill="#94a3b8" fontSize="11" fontFamily="sans-serif">Apex Micro (sup-03)</text>
              </g>

              {/* Central Assembly Hub */}
              <g transform="translate(340, 160)">
                <rect x="-24" y="-24" width="48" height="48" rx="8" fill="#1f293d" stroke="#f59e0b" strokeWidth="2.5" />
                <text x="0" y="5" fill="#f8fafc" fontSize="12" fontWeight="bold" textAnchor="middle" fontFamily="sans-serif">MFG-01</text>
                <text x="0" y="40" fill="#fbbf24" fontSize="11" fontWeight="600" textAnchor="middle" fontFamily="sans-serif">Shenzhen Plant</text>
              </g>

              {/* Distribution Hubs */}
              <g transform="translate(540, 110)">
                <circle r="18" fill="#1e293b" stroke="#10b981" strokeWidth="2.5" />
                <circle r="7" fill="#10b981" />
                <text x="30" y="4" fill="#10b981" fontWeight="600" fontSize="11" fontFamily="sans-serif">WH-01 Frankfurt</text>
              </g>

              <g transform="translate(540, 230)">
                <circle r="18" fill="#1e293b" stroke="#10b981" strokeWidth="2.5" />
                <circle r="7" fill="#10b981" />
                <text x="30" y="4" fill="#10b981" fontWeight="600" fontSize="11" fontFamily="sans-serif">DC-02 Amsterdam</text>
              </g>
            </svg>
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
                  No unhandled disruptions active. Real-time agent monitoring listening on Kafka bus.
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
