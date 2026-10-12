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
      {/* Trace Explorer Header */}
      <div className={styles.header}>
        <div className={styles.headerInfo}>
          <h3 className={styles.title}>Reasoning Trace Explorer (CD2F Provenance)</h3>
          <div className={styles.headerMetaRow}>
            <span className={styles.traceIdTag}>
              TRACE ID: {activeDecision?.trace_id || "trace-pending"}
            </span>
            {activeDecision && (
              <>
                <span className={styles.metaDivider}>|</span>
                <span className={styles.metaSnippet}>
                  METHOD: {activeDecision.decision_method || "CD2F"}
                </span>
                <span className={styles.metaDivider}>|</span>
                <span className={styles.metaSnippet}>
                  CONFIDENCE: {(activeDecision.decision_confidence * 100).toFixed(1)}%
                </span>
              </>
            )}
          </div>
        </div>

        <div className={styles.selectorRow}>
          <span className={styles.selectorLabel}>Inspect Decision:</span>
          <select
            className={styles.select}
            value={activeDecision?.decision_id || ""}
            onChange={(e) => setActiveId(e.target.value)}
          >
            {decisions.map((d) => (
              <option key={d.decision_id} value={d.decision_id}>
                {d.scenario_id.toUpperCase()} - {d.decision_id.substring(0, 8)} ({(d.decision_confidence * 100).toFixed(0)}% WCS)
              </option>
            ))}
          </select>
        </div>
      </div>

      {!activeDecision ? (
        <div className={styles.emptyState}>
          No reasoning trace records available. Trigger a scenario from the Scenario Catalog to generate multi-agent arbitration traces.
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
              <p className={styles.nodeDesc}>
                Disruption scenario <strong>{activeDecision.scenario_id.toUpperCase()}</strong> ingested via Kafka bus. SCOF Coordinator initialized arbitration, discovered registered specialists on A2A protocol, and published target context envelope.
              </p>
              <div className={styles.phase1Meta}>
                <div className={styles.phase1Item}>
                  <span className={styles.phase1Label}>Consensus Bundle:</span>
                  <span className={styles.phase1Val}>{activeDecision.consensus_bundle_id || "bundle-default"}</span>
                </div>
                <div className={styles.phase1Item}>
                  <span className={styles.phase1Label}>Source Envelope:</span>
                  <span className={styles.phase1Val}>{activeDecision.source_bundle_id || "envelope-default"}</span>
                </div>
              </div>
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
                      <div className={styles.claimHeader}>
                        <span className={styles.claimAgent}>{claimStep.data?.agent_id || "specialist"}</span>
                        <span className={styles.claimConfidence}>
                          {((claimStep.data?.stated_confidence || 0) * 100).toFixed(1)}% CONF
                        </span>
                      </div>
                      <p className={styles.claimText}>{claimStep.data?.recommendation || claimStep.content}</p>
                      <div className={styles.claimMeta}>
                        <span>Impact: {claimStep.data?.parsed_impact_level || "EVALUATED"}</span>
                        <span>Step #{claimStep.step_index || idx + 1}</span>
                      </div>
                      {/* Expandable Raw Claim JSON */}
                      <details className={styles.stepRawDetails}>
                        <summary className={styles.stepRawSummary}>View Raw Claim JSON</summary>
                        <pre className={styles.stepRawPre}>
                          {JSON.stringify(claimStep.data || claimStep, null, 2)}
                        </pre>
                      </details>
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
                      <div className={styles.stepContentCol}>
                        <span className={styles.stepText}>{step.content}</span>
                        {/* Expandable Step Payload */}
                        {step.data && (
                          <details className={styles.stepRawDetailsInline}>
                            <summary className={styles.stepRawSummaryInline}>Raw Step JSON</summary>
                            <pre className={styles.stepRawPre}>
                              {JSON.stringify(step.data, null, 2)}
                            </pre>
                          </details>
                        )}
                      </div>
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
                <span className={`${styles.nodeBadge} ${
                  activeDecision.escalation_tier === "HUMAN_ESCALATION"
                    ? styles.badgeEscalated
                    : styles.badgeNominal
                }`}>
                  {activeDecision.escalation_tier}
                </span>
              </div>

              <div className={styles.decisionHighlightBox}>
                <div className={styles.decisionHighlightLabel}>
                  Selected Recommendation (Stability: {(activeDecision.decision_confidence * 100).toFixed(1)}%):
                </div>
                <div className={styles.decisionHighlightText}>
                  "{activeDecision.final_recommendation || "Consensus action approved"}"
                </div>
              </div>

              {steps
                .filter((s: any) => s.step_type === "ESCALATION")
                .map((esc: any, idx: number) => (
                  <div key={idx} className={styles.escalationRationaleText}>
                    {esc.content}
                  </div>
                ))}
            </div>
          </div>

          {/* Expandable Complete Decision Record JSON Payload */}
          <div className={styles.rawJsonSection}>
            <details className={styles.jsonDetails}>
              <summary className={styles.jsonSummary}>
                Expand Complete Decision Record Raw JSON Payload ({activeDecision.decision_id})
              </summary>
              <pre className={styles.jsonPre}>
                {JSON.stringify(activeDecision, null, 2)}
              </pre>
            </details>
          </div>
        </div>
      )}
    </div>
  );
};
