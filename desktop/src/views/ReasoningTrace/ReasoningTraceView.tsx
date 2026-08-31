import React, { useEffect, useState } from "react";
import styles from "./ReasoningTrace.module.css";
import { apiClient } from "../../api/client";
import type { DecisionRecord } from "../../api/types";

interface ReasoningTraceViewProps {
  selectedDecisionId?: string;
}

export const ReasoningTraceView: React.FC<ReasoningTraceViewProps> = ({
  selectedDecisionId,
}) => {
  const [decisions, setDecisions] = useState<DecisionRecord[]>([]);
  const [activeId, setActiveId] = useState<string | null>(selectedDecisionId || null);

  useEffect(() => {
    let mounted = true;
    apiClient
      .listDecisions()
      .then((data: DecisionRecord[]) => {
        if (mounted && Array.isArray(data) && data.length > 0) {
          setDecisions(data);
          if (!activeId) {
            setActiveId(data[0].decision_id);
          }
        }
      })
      .catch(() => {});
    return () => {
      mounted = false;
    };
  }, []);

  useEffect(() => {
    if (selectedDecisionId) {
      setActiveId(selectedDecisionId);
    }
  }, [selectedDecisionId]);

  const activeDecision = decisions.find((d) => d.decision_id === activeId) || decisions[0];

  const steps = activeDecision?.reasoning_trail || [];

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div>
          <h3 className={styles.title}>Reasoning Trace Explorer (CD2F Provenance)</h3>
          <span style={{ fontSize: "12px", color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>
            Trace ID: {activeDecision?.trace_id || "trace-pending"}
          </span>
        </div>

        <div className={styles.selectorRow}>
          <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>Inspect Decision:</span>
          <select
            className={styles.select}
            value={activeDecision?.decision_id || ""}
            onChange={(e) => setActiveId(e.target.value)}
          >
            {decisions.map((d) => (
              <option key={d.decision_id} value={d.decision_id}>
                {d.scenario_id.toUpperCase()} - {d.decision_id.substring(0, 8)}... ({(d.decision_confidence * 100).toFixed(0)}%)
              </option>
            ))}
          </select>
        </div>
      </div>

      {!activeDecision ? (
        <div style={{ color: "var(--text-muted)", padding: "40px", textAlign: "center" }}>
          No reasoning trace records available. Trigger a scenario to generate arbitration traces.
        </div>
      ) : (
        <div className={styles.pipeline}>
          {/* Phase 1: Disruption Trigger Context */}
          <div className={styles.node}>
            <div className={`${styles.nodeIcon} ${styles.nodeIconActive}`}>01</div>
            <div className={styles.nodeBody}>
              <div className={styles.nodeHeader}>
                <span className={styles.nodeTitle}>Phase 1: Disruption Context & Targeting</span>
                <span className={styles.nodeBadge}>KAFKA EVENT INGEST</span>
              </div>
              <p style={{ fontSize: "13px", color: "var(--text-secondary)" }}>
                Scenario <strong>{activeDecision.scenario_id}</strong> triggered. Coordinator discovered 4 specialist agents on A2A protocol and resolved target specialists.
              </p>
            </div>
          </div>

          {/* Phase 2: Specialist Evidence & Claims */}
          <div className={styles.node}>
            <div className={`${styles.nodeIcon} ${styles.nodeIconActive}`}>02</div>
            <div className={styles.nodeBody}>
              <div className={styles.nodeHeader}>
                <span className={styles.nodeTitle}>Phase 2: Specialist Evidence & Claims</span>
                <span className={styles.nodeBadge}>A2A PARALLEL DISPATCH</span>
              </div>

              <div className={styles.claimsGrid}>
                {steps
                  .filter((s: any) => s.step_type === "CLAIM")
                  .map((claimStep: any, idx: number) => (
                    <div key={idx} className={styles.claimBox}>
                      <span className={styles.claimAgent}>{claimStep.data.agent_id}</span>
                      <p className={styles.claimText}>{claimStep.data.recommendation}</p>
                      <div className={styles.claimMeta}>
                        <span>Confidence: {((claimStep.data.stated_confidence || 0) * 100).toFixed(1)}%</span>
                        <span>Impact: {claimStep.data.parsed_impact_level}</span>
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          </div>

          {/* Phase 3: Consensus Weighting & Tally */}
          <div className={styles.node}>
            <div className={`${styles.nodeIcon} ${styles.nodeIconActive}`}>03</div>
            <div className={styles.nodeBody}>
              <div className={styles.nodeHeader}>
                <span className={styles.nodeTitle}>Phase 3: Weighted Consensus Arbitration (CD2F)</span>
                <span className={styles.nodeBadge}>DYNAMIC WEIGHTING</span>
              </div>

              <div className={styles.stepList}>
                {steps
                  .filter((s: any) => s.step_type === "WEIGHT_REPORT" || s.step_type === "TALLY")
                  .map((step: any, idx: number) => (
                    <div key={idx} className={styles.stepItem}>
                      <span className={styles.stepIndex}>#{step.step_index}</span>
                      <span>{step.content}</span>
                    </div>
                  ))}
              </div>
            </div>
          </div>

          {/* Phase 4: Escalation Routing & Final Decision */}
          <div className={styles.node}>
            <div
              className={`${styles.nodeIcon} ${
                activeDecision.escalation_tier === "HUMAN_ESCALATION"
                  ? styles.nodeIconEscalated
                  : styles.nodeIconSuccess
              }`}
            >
              04
            </div>
            <div className={styles.nodeBody}>
              <div className={styles.nodeHeader}>
                <span className={styles.nodeTitle}>Phase 4: Policy Evaluation & Escalation</span>
                <span className={styles.nodeBadge}>{activeDecision.escalation_tier}</span>
              </div>

              <div
                style={{
                  background: "var(--bg-surface)",
                  padding: "12px 14px",
                  borderRadius: "var(--radius-md)",
                  border: "1px solid var(--border-subtle)",
                }}
              >
                <div style={{ fontWeight: 700, color: "var(--text-primary)", marginBottom: "4px" }}>
                  Selected Recommendation (WCS: {(activeDecision.decision_confidence * 100).toFixed(1)}%):
                </div>
                <div style={{ color: "var(--accent-cyan)", fontSize: "13px", lineHeight: "1.4" }}>
                  "{activeDecision.final_recommendation}"
                </div>
              </div>

              {steps
                .filter((s: any) => s.step_type === "ESCALATION")
                .map((esc: any, idx: number) => (
                  <div key={idx} style={{ fontSize: "12px", color: "var(--text-muted)" }}>
                    {esc.content}
                  </div>
                ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
