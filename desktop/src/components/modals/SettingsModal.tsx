import React, { useState } from "react";
import styles from "./SettingsModal.module.css";
import { useConnection } from "../../state/connection";

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({ isOpen, onClose }) => {
  const [activeTab, setActiveTab] = useState<"diagnostics" | "profile" | "shortcuts" | "about">("diagnostics");
  const { state } = useConnection();

  if (!isOpen) return null;

  return (
    <div className={styles.backdrop} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div className={styles.header}>
          <h3 className={styles.title}>System Settings & Diagnostics</h3>
          <button className={styles.closeButton} onClick={onClose} aria-label="Close Settings">
            x
          </button>
        </div>

        <div className={styles.tabBar}>
          <button
            className={`${styles.tabBtn} ${activeTab === "diagnostics" ? styles.tabBtnActive : ""}`}
            onClick={() => setActiveTab("diagnostics")}
          >
            Diagnostics
          </button>
          <button
            className={`${styles.tabBtn} ${activeTab === "profile" ? styles.tabBtnActive : ""}`}
            onClick={() => setActiveTab("profile")}
          >
            Active Profile
          </button>
          <button
            className={`${styles.tabBtn} ${activeTab === "shortcuts" ? styles.tabBtnActive : ""}`}
            onClick={() => setActiveTab("shortcuts")}
          >
            Keyboard Shortcuts
          </button>
          <button
            className={`${styles.tabBtn} ${activeTab === "about" ? styles.tabBtnActive : ""}`}
            onClick={() => setActiveTab("about")}
          >
            About
          </button>
        </div>

        <div className={styles.content}>
          {activeTab === "diagnostics" && (
            <div className={styles.section}>
              <span className={styles.sectionHeading}>Connection & Service Readiness</span>
              <div className={styles.infoGrid}>
                <span className={styles.label}>Gateway Status</span>
                <div className={styles.statusRow}>
                  <span
                    className={styles.statusDot}
                    style={{
                      backgroundColor:
                        state.overallStatus === "Connected"
                          ? "var(--status-success)"
                          : "var(--status-warning)",
                    }}
                  />
                  <span className={styles.value}>{state.overallStatus}</span>
                </div>

                <span className={styles.label}>API Base URL</span>
                <span className={styles.value}>http://localhost:8000</span>

                <span className={styles.label}>A2A Coordinator</span>
                <span className={styles.value}>http://localhost:8010 (LangGraph Multi-Agent Kernel)</span>

                <span className={styles.label}>Message Bus</span>
                <span className={styles.value}>Kafka 9092 (Topics: disruptions.triggered, decisions.emitted)</span>

                <span className={styles.label}>Relational Ledger</span>
                <span className={styles.value}>PostgreSQL 5432 (scof.decision_records, scof.scenarios)</span>

                <span className={styles.label}>Graph Topology</span>
                <span className={styles.value}>Neo4j Bolt 7687 (18 Nodes, 48 Supply Corridors)</span>
              </div>
            </div>
          )}

          {activeTab === "profile" && (
            <div className={styles.section}>
              <span className={styles.sectionHeading}>Active Domain Profile Specifications</span>
              <div className={styles.infoGrid}>
                <span className={styles.label}>Profile ID</span>
                <span className={styles.value}>mvp-electronics</span>

                <span className={styles.label}>Manufacturing Region</span>
                <span className={styles.value}>Peninsular South Indian Electronics Corridor (TN, KA, KL, AP, TS)</span>

                <span className={styles.label}>Assembly Anchor</span>
                <span className={styles.value}>mfg-01 (Sriperumbudur High-Tech Assembly Plant)</span>

                <span className={styles.label}>Tier-1 Suppliers</span>
                <span className={styles.value}>8 Contracted Facilities (SPEL, CDIL, Kaynes, Syrma, Centum, Vinyas, SFO, Sahasra)</span>

                <span className={styles.label}>Logistics Buffers</span>
                <span className={styles.value}>4 Warehouses & FTWZs (Hosur wh-01, Whitefield wh-02, Oragadam wh-03, Sri City wh-04)</span>

                <span className={styles.label}>Export Gateways</span>
                <span className={styles.value}>3 Multimodal Ports (Chennai Port dc-01, Cochin ICTT dc-02, Hyderabad Air Cargo dc-03)</span>

                <span className={styles.label}>Configured Scenarios</span>
                <span className={styles.value}>25 Production Scenarios (scen-01 to scen-25)</span>
              </div>
            </div>
          )}

          {activeTab === "shortcuts" && (
            <div className={styles.section}>
              <span className={styles.sectionHeading}>Canonical Navigation Hotkeys</span>
              <div className={styles.infoGrid}>
                <span className={styles.label}>Operations Overview</span>
                <span className={styles.value}>Ctrl + 1</span>

                <span className={styles.label}>Decision Center</span>
                <span className={styles.value}>Ctrl + 2</span>

                <span className={styles.label}>Scenario Launcher</span>
                <span className={styles.value}>Ctrl + 3</span>

                <span className={styles.label}>Agent Command</span>
                <span className={styles.value}>Ctrl + 4</span>

                <span className={styles.label}>What-If Simulation</span>
                <span className={styles.value}>Ctrl + 5</span>

                <span className={styles.label}>Reasoning Traces</span>
                <span className={styles.value}>Ctrl + 6</span>

                <span className={styles.label}>Evaluation Matrix</span>
                <span className={styles.value}>Ctrl + 7</span>

                <span className={styles.label}>Shortcuts HUD</span>
                <span className={styles.value}>Shift + ?</span>

                <span className={styles.label}>Dismiss Modal</span>
                <span className={styles.value}>Esc</span>
              </div>
            </div>
          )}

          {activeTab === "about" && (
            <div className={styles.section}>
              <span className={styles.sectionHeading}>Platform Information</span>
              <div className={styles.infoGrid}>
                <span className={styles.label}>Platform</span>
                <span className={styles.value}>SCOF (Supply Chain Cognitive Orchestration Framework)</span>

                <span className={styles.label}>Console Version</span>
                <span className={styles.value}>v1.0.0 (Enterprise South Indian Release)</span>

                <span className={styles.label}>Decision Engine</span>
                <span className={styles.value}>Fast-Path Sub-500ms CD2F Multi-Agent Consensus</span>

                <span className={styles.label}>Design Standard</span>
                <span className={styles.value}>Calm Enterprise Operations Console (docs/desktop_console_ui_update.md)</span>
              </div>
            </div>
          )}
        </div>

        <div className={styles.footer}>
          <button className={styles.doneBtn} onClick={onClose}>
            Done
          </button>
        </div>
      </div>
    </div>
  );
};
