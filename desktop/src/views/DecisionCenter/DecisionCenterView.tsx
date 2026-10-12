import React, { useEffect, useState } from "react";
import styles from "./DecisionCenter.module.css";
import { useDecisions } from "../../hooks/useDecisions";
import { apiClient } from "../../api/client";
import type { DecisionRecord, MeetingLogEntry } from "../../api/types";
import { ContextualDrawer } from "../../components/common/ContextualDrawer";

interface DecisionCenterViewProps {
  selectedDecisionId?: string;
  onOpenTrace?: (decisionId: string) => void;
}

export const DecisionCenterView: React.FC<DecisionCenterViewProps> = ({
  selectedDecisionId,
  onOpenTrace,
}) => {
  const liveEvents = useDecisions();
  const [decisions, setDecisions] = useState<DecisionRecord[]>([]);
  const [activeId, setActiveId] = useState<string | null>(selectedDecisionId || null);
  const [isClaimsDrawerOpen, setIsClaimsDrawerOpen] = useState<boolean>(false);
  const [acknowledgedDecisions, setAcknowledgedDecisions] = useState<Set<string>>(new Set());

  useEffect(() => {
    let mounted = true;
    apiClient
      .listDecisions()
      .then((data: DecisionRecord[]) => {
        if (mounted && Array.isArray(data)) {
          setDecisions(data);
          if (!activeId && data.length > 0) {
            setActiveId(data[0].decision_id);
          }
        }
      })
      .catch(() => {
        // Handled
      });
    return () => {
      mounted = false;
    };
  }, []);

  useEffect(() => {
    if (selectedDecisionId) {
      setActiveId(selectedDecisionId);
    }
  }, [selectedDecisionId]);

  // Merge live decisions from event bus
  const allDecisions = [...decisions];
  liveEvents.forEach((ev) => {
    if (ev.type === "completed" && ev.payload.decision_record) {
      const rec = ev.payload.decision_record;
      if (!allDecisions.some((existing) => existing.decision_id === rec.decision_id)) {
        allDecisions.unshift(rec);
      }
    }
  });

  const activeDecision = allDecisions.find((d) => d.decision_id === activeId) || allDecisions[0];

  const getDerivedStatus = (dec: DecisionRecord) => {
    if (dec.escalation_tier === "HUMAN_ESCALATION" || dec.decision_confidence < 0.8) {
      return {
        label: "HUMAN ESCALATION REQUIRED",
        styleClass: styles.statusEscalated,
        tierStyle: styles.tierHuman,
      };
    }
    if (dec.escalation_tier === "SLOW_PATH") {
      return {
        label: "DELIBERATED CONSENSUS",
        styleClass: styles.statusConsensus,
        tierStyle: styles.tierFast,
      };
    }
    return {
      label: "FAST-PATH RECOMMENDATION",
      styleClass: styles.statusFast,
      tierStyle: styles.tierFast,
    };
  };

  const toggleAcknowledge = (decisionId: string) => {
    setAcknowledgedDecisions((prev) => {
      const next = new Set(prev);
      if (next.has(decisionId)) {
        next.delete(decisionId);
      } else {
        next.add(decisionId);
      }
      return next;
    });
  };

  const isCurrentAcknowledged = activeDecision
    ? acknowledgedDecisions.has(activeDecision.decision_id)
    : false;

  const getStatementTypeClass = (stmtType: string) => {
    switch (stmtType) {
      case "CLAIM":
        return styles.chipClaim;
      case "WEIGHT_REPORT":
        return styles.chipWeight;
      case "TALLY":
        return styles.chipTally;
      case "ESCALATION":
        return styles.chipEscalation;
      case "DECISION":
        return styles.chipDecision;
      default:
        return styles.chipClaim;
    }
  };

  return (
    <div className={styles.container}>
      {/* Master Decision Stream (Left Column) */}
      <div className={styles.leftColumn}>
        <div className={styles.columnHeader}>
          <span className={styles.columnTitle}>Decisions Stream</span>
          <span className={styles.recordCount}>
            {allDecisions.length} RECORDED
          </span>
        </div>

        <div className={styles.feedList}>
          {allDecisions.length === 0 ? (
            <div className={styles.emptyState}>No decisions recorded yet.</div>
          ) : (
            allDecisions.map((dec) => {
              const isSelected = dec.decision_id === activeDecision?.decision_id;
              const statusInfo = getDerivedStatus(dec);
              const isAcked = acknowledgedDecisions.has(dec.decision_id);
              const formattedTime = new Date(dec.timestamp)
                .toISOString()
                .substring(11, 19) + " UTC";

              return (
                <div
                  key={dec.decision_id}
                  className={`${styles.feedCard} ${isSelected ? styles.feedCardActive : ""}`}
                  onClick={() => setActiveId(dec.decision_id)}
                >
                  <div className={styles.feedCardHeader}>
                    <span className={styles.scenarioTag}>{dec.scenario_id}</span>
                    <div className={styles.headerBadges}>
                      {isAcked && (
                        <span className={styles.ackedTag}>ACKNOWLEDGED</span>
                      )}
                      <span className={`${styles.statusTag} ${statusInfo.styleClass}`}>
                        {statusInfo.label}
                      </span>
                      <span className={styles.confidenceBadge}>
                        {(dec.decision_confidence * 100).toFixed(1)}% WCS
                      </span>
                    </div>
                  </div>
                  <div className={styles.recommendationSnippet}>
                    {dec.final_recommendation || "Consensus action recommended"}
                  </div>
                  <div className={styles.feedCardFooter}>
                    <span className={`${styles.tierTag} ${statusInfo.tierStyle}`}>
                      {dec.escalation_tier}
                    </span>
                    <span>{formattedTime}</span>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* Selected Decision Detail Inspection (Right Column) */}
      <div className={styles.detailColumn}>
        {!activeDecision ? (
          <div className={styles.emptyState}>Select a decision from the stream to view details.</div>
        ) : (
          <>
            <div className={styles.detailHeader}>
              <div className={styles.detailTitleRow}>
                <div>
                  <h3 className={styles.detailTitle}>
                    Scenario: {activeDecision.scenario_id.toUpperCase()}
                  </h3>
                  <span className={styles.decisionIdTag}>
                    ID: {activeDecision.decision_id}
                  </span>
                </div>

                <div className={styles.headerButtonRow}>
                  <button
                    className={
                      isCurrentAcknowledged
                        ? styles.ackButtonActive
                        : styles.ackButton
                    }
                    onClick={() => toggleAcknowledge(activeDecision.decision_id)}
                    title="Toggle In-Session Operator Review Acknowledgment"
                    aria-label="Acknowledge Recommendation"
                  >
                    {isCurrentAcknowledged
                      ? "Acknowledged (Session)"
                      : "Acknowledge Recommendation"}
                  </button>

                  <button
                    className={styles.claimsButton}
                    onClick={() => setIsClaimsDrawerOpen(true)}
                    title="Inspect Specialist Deliberation Claims"
                    aria-label="Inspect Claims"
                  >
                    Deliberation Claims
                  </button>

                  {onOpenTrace && (
                    <button
                      className={styles.traceButton}
                      onClick={() => onOpenTrace(activeDecision.decision_id)}
                      title="Navigate directly to Reasoning Trace workspace"
                      aria-label="Explore Reasoning Trace"
                    >
                      Explore Reasoning Trace
                    </button>
                  )}
                </div>
              </div>

              <div className={styles.metaGrid}>
                <div className={styles.metaItem}>
                  <span className={styles.metaLabel}>Derived Decision Status</span>
                  <span className={styles.metaValue}>
                    {getDerivedStatus(activeDecision).label}
                  </span>
                </div>
                <div className={styles.metaItem}>
                  <span className={styles.metaLabel}>Escalation Tier</span>
                  <span className={styles.metaValue}>{activeDecision.escalation_tier}</span>
                </div>
                <div className={styles.metaItem}>
                  <span className={styles.metaLabel}>Consensus Stability (WCS)</span>
                  <span className={styles.metaValue}>
                    {activeDecision.weighted_consensus_stability !== null &&
                    activeDecision.weighted_consensus_stability !== undefined
                      ? `${(activeDecision.weighted_consensus_stability * 100).toFixed(1)}%`
                      : `${(activeDecision.decision_confidence * 100).toFixed(1)}%`}
                  </span>
                </div>
                <div className={styles.metaItem}>
                  <span className={styles.metaLabel}>Arbitration Engine</span>
                  <span className={styles.metaValue}>{activeDecision.decision_method || "CD2F"}</span>
                </div>
              </div>
            </div>

            {/* Arbitrated Consensus Recommendation Panel */}
            <div className={styles.winningBanner}>
              <span className={styles.winningLabel}>Arbitrated Consensus Recommendation</span>
              <p className={styles.winningText}>
                {activeDecision.final_recommendation || "No action recommended."}
              </p>
              {activeDecision.escalation_rationale && (
                <div className={styles.rationaleBox}>
                  <span className={styles.rationaleLabel}>Arbitration Rationale:</span>
                  <span className={styles.rationaleText}>
                    {activeDecision.escalation_rationale}
                  </span>
                </div>
              )}
            </div>

            {/* Downstream Execution Boundary (Preserves Recommendation vs Action Distinction) */}
            <div className={styles.executionBoundaryCard}>
              <div className={styles.boundaryHeader}>
                <span className={styles.boundaryTitle}>
                  Execution Integration: External ERP / WMS / TMS (Unlinked)
                </span>
                <span className={styles.boundaryBadge}>ADVISORY BOUNDARY</span>
              </div>
              <p className={styles.boundaryText}>
                SCOF acts strictly as an analytical decision twin. Direct automated dispatch to physical ERP/WMS execution adapters is unlinked in advisory simulation mode. Real-world purchase orders or freight re-routes require manual authorization in downstream systems.
              </p>
              <div className={styles.boundaryActions}>
                <button
                  className={styles.executeDisabledBtn}
                  disabled
                  title="Direct execution disabled in advisory cognitive twin mode"
                  aria-label="Direct execution disabled"
                >
                  Execute Order Adjustment via ERP (Unlinked)
                </button>
                <span className={styles.boundaryHint}>
                  Status: Advisory Recommendation Only
                </span>
              </div>
            </div>

            {/* Specialist Deliberation Summary */}
            <div className={styles.section}>
              <div className={styles.sectionHeaderRow}>
                <span className={styles.sectionTitle}>
                  Specialist Deliberation Summary
                </span>
                <button
                  className={styles.inspectClaimsLink}
                  onClick={() => setIsClaimsDrawerOpen(true)}
                >
                  Open Full Claims Inspector ({activeDecision.meeting_log_entries?.length || 0} entries)
                </button>
              </div>

              <div className={styles.meetingLogSummary}>
                {activeDecision.meeting_log_entries && activeDecision.meeting_log_entries.length > 0 ? (
                  activeDecision.meeting_log_entries.slice(0, 3).map((entry: MeetingLogEntry, idx: number) => {
                    const entryTime = new Date(entry.timestamp)
                      .toISOString()
                      .substring(11, 19) + " UTC";
                    return (
                      <div key={idx} className={styles.logSummaryItem}>
                        <div className={styles.logSummaryHeader}>
                          <span className={styles.speakerTag}>{entry.speaker}</span>
                          <span className={`${styles.statementChip} ${getStatementTypeClass(entry.statement_type)}`}>
                            {entry.statement_type}
                          </span>
                          <span className={styles.logTime}>{entryTime}</span>
                        </div>
                        <div className={styles.logSnippet}>{entry.content}</div>
                      </div>
                    );
                  })
                ) : (
                  <div className={styles.emptyState}>No meeting log entries available for this record.</div>
                )}
              </div>
            </div>
          </>
        )}
      </div>

      {/* Contextual Drawer: Full Specialist Deliberation Claims */}
      {activeDecision && (
        <ContextualDrawer
          isOpen={isClaimsDrawerOpen}
          title={`Deliberation Claims: ${activeDecision.scenario_id.toUpperCase()}`}
          badge={activeDecision.decision_method || "CD2F"}
          mode="overlay"
          onClose={() => setIsClaimsDrawerOpen(false)}
        >
          <div className={styles.drawerClaimsList}>
            <div className={styles.drawerIntro}>
              <span>Chronological Multi-Agent Deliberation Trace (Meeting Log)</span>
            </div>
            {activeDecision.meeting_log_entries && activeDecision.meeting_log_entries.length > 0 ? (
              activeDecision.meeting_log_entries.map((entry: MeetingLogEntry, idx: number) => {
                const entryTime = new Date(entry.timestamp)
                  .toISOString()
                  .substring(11, 19) + " UTC";
                return (
                  <div key={idx} className={styles.drawerLogCard}>
                    <div className={styles.drawerLogHeader}>
                      <span className={styles.drawerSpeaker}>{entry.speaker}</span>
                      <span className={`${styles.statementChip} ${getStatementTypeClass(entry.statement_type)}`}>
                        {entry.statement_type}
                      </span>
                      <span className={styles.logTime}>{entryTime}</span>
                    </div>
                    <div className={styles.drawerLogContent}>{entry.content}</div>
                  </div>
                );
              })
            ) : (
              <div className={styles.emptyState}>No log entries available.</div>
            )}
          </div>
        </ContextualDrawer>
      )}
    </div>
  );
};
