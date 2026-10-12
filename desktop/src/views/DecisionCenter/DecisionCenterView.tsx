import React, { useEffect, useState } from "react";
import styles from "./DecisionCenter.module.css";
import { useDecisions } from "../../hooks/useDecisions";
import { apiClient } from "../../api/client";
import type { DecisionRecord, MeetingLogEntry } from "../../api/types";

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

  const getLifecycleStatus = (dec: DecisionRecord) => {
    if (dec.escalation_tier === "HUMAN_ESCALATION") {
      return { label: "ESCALATED", styleClass: styles.statusEscalated };
    }
    return { label: "COMPLETED", styleClass: styles.statusCompleted };
  };

  return (
    <div className={styles.container}>
      {/* Master Decision Stream (Left Column) */}
      <div className={styles.leftColumn}>
        <div className={styles.columnHeader}>
          <span className={styles.columnTitle}>Decisions Stream</span>
          <span style={{ fontSize: "11px", color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>
            {allDecisions.length} RECORDED
          </span>
        </div>

        <div className={styles.feedList}>
          {allDecisions.length === 0 ? (
            <div className={styles.emptyState}>No decisions recorded yet.</div>
          ) : (
            allDecisions.map((dec) => {
              const isSelected = dec.decision_id === activeDecision?.decision_id;
              const lifecycle = getLifecycleStatus(dec);
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
                      <span className={`${styles.statusTag} ${lifecycle.styleClass}`}>
                        {lifecycle.label}
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
                    <span
                      className={`${styles.tierTag} ${
                        dec.escalation_tier === "HUMAN_ESCALATION"
                          ? styles.tierHuman
                          : styles.tierFast
                      }`}
                    >
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
                {onOpenTrace && (
                  <button
                    className={styles.traceButton}
                    onClick={() => onOpenTrace(activeDecision.decision_id)}
                  >
                    Explore Reasoning Trace
                  </button>
                )}
              </div>

              <div className={styles.metaGrid}>
                <div className={styles.metaItem}>
                  <span className={styles.metaLabel}>Lifecycle Status</span>
                  <span className={styles.metaValue}>
                    {activeDecision.escalation_tier === "HUMAN_ESCALATION"
                      ? "Escalated"
                      : "Completed"}
                  </span>
                </div>
                <div className={styles.metaItem}>
                  <span className={styles.metaLabel}>Escalation Tier</span>
                  <span className={styles.metaValue}>{activeDecision.escalation_tier}</span>
                </div>
                <div className={styles.metaItem}>
                  <span className={styles.metaLabel}>Consensus Stability</span>
                  <span className={styles.metaValue}>
                    {activeDecision.weighted_consensus_stability !== null &&
                    activeDecision.weighted_consensus_stability !== undefined
                      ? `${(activeDecision.weighted_consensus_stability * 100).toFixed(1)}%`
                      : `${(activeDecision.decision_confidence * 100).toFixed(1)}%`}
                  </span>
                </div>
                <div className={styles.metaItem}>
                  <span className={styles.metaLabel}>Decision Method</span>
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
            </div>

            {/* Specialist Meeting Log Deliberation */}
            <div className={styles.section}>
              <span className={styles.sectionTitle}>Deliberation Record & Specialist Claims</span>
              <div className={styles.meetingLogTimeline}>
                {activeDecision.meeting_log_entries && activeDecision.meeting_log_entries.length > 0 ? (
                  activeDecision.meeting_log_entries.map((entry: MeetingLogEntry, idx: number) => {
                    const entryTime = new Date(entry.timestamp)
                      .toISOString()
                      .substring(11, 19) + " UTC";
                    return (
                      <div key={idx} className={styles.logEntry}>
                        <div className={styles.logSpeaker}>
                          <span>{entry.speaker} ({entry.statement_type})</span>
                          <span className={styles.logTime}>{entryTime}</span>
                        </div>
                        <div className={styles.logContent}>{entry.content}</div>
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
    </div>
  );
};
