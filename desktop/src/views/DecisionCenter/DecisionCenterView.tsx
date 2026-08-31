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

  // Merge live decisions
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

  return (
    <div className={styles.container}>
      {/* Left Column: Decision Feed */}
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
              return (
                <div
                  key={dec.decision_id}
                  className={`${styles.feedCard} ${isSelected ? styles.feedCardActive : ""}`}
                  onClick={() => setActiveId(dec.decision_id)}
                >
                  <div className={styles.feedCardHeader}>
                    <span className={styles.scenarioTag}>{dec.scenario_id}</span>
                    <span className={styles.confidenceBadge}>
                      {(dec.decision_confidence * 100).toFixed(1)}% WCS
                    </span>
                  </div>
                  <div className={styles.recommendationSnippet}>
                    {dec.final_recommendation || "No recommendation"}
                  </div>
                  <div className={styles.feedCardFooter}>
                    <span>{dec.escalation_tier}</span>
                    <span>{new Date(dec.timestamp).toLocaleTimeString()}</span>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* Right Column: Selected Decision Detail Inspection */}
      <div className={styles.detailColumn}>
        {!activeDecision ? (
          <div className={styles.emptyState}>Select a decision from the feed to view details.</div>
        ) : (
          <>
            <div className={styles.detailHeader}>
              <div className={styles.detailTitleRow}>
                <div>
                  <h3 className={styles.detailTitle}>
                    Scenario: {activeDecision.scenario_id.toUpperCase()}
                  </h3>
                  <span className={styles.decisionIdTag}>ID: {activeDecision.decision_id}</span>
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
                  <span className={styles.metaLabel}>Escalation Tier</span>
                  <span className={styles.metaValue}>{activeDecision.escalation_tier}</span>
                </div>
                <div className={styles.metaItem}>
                  <span className={styles.metaLabel}>Consensus Stability</span>
                  <span className={styles.metaValue}>
                    {activeDecision.weighted_consensus_stability !== null && activeDecision.weighted_consensus_stability !== undefined
                      ? `${(activeDecision.weighted_consensus_stability * 100).toFixed(1)}%`
                      : `${(activeDecision.decision_confidence * 100).toFixed(1)}%`}
                  </span>
                </div>
                <div className={styles.metaItem}>
                  <span className={styles.metaLabel}>Decision Method</span>
                  <span className={styles.metaValue}>{activeDecision.decision_method || "CD2F"}</span>
                </div>
                <div className={styles.metaItem}>
                  <span className={styles.metaLabel}>Profile Scope</span>
                  <span className={styles.metaValue}>{activeDecision.profile_name || "mvp-electronics"}</span>
                </div>
              </div>
            </div>

            {/* Winning Recommendation Banner */}
            <div className={styles.winningBanner}>
              <span className={styles.winningLabel}>Arbitrated Consensus Recommendation</span>
              <p className={styles.winningText}>
                {activeDecision.final_recommendation || "No action recommended."}
              </p>
            </div>

            {/* AI Meeting Log Timeline */}
            <div className={styles.section}>
              <span className={styles.sectionTitle}>AI Meeting Log & Specialist Statements</span>
              <div className={styles.meetingLogTimeline}>
                {activeDecision.meeting_log_entries && activeDecision.meeting_log_entries.length > 0 ? (
                  activeDecision.meeting_log_entries.map((entry: MeetingLogEntry, idx: number) => (
                    <div key={idx} className={styles.logEntry}>
                      <div className={styles.logSpeaker}>
                        <span>{entry.speaker} ({entry.statement_type})</span>
                        <span className={styles.logTime}>
                          {new Date(entry.timestamp).toLocaleTimeString()}
                        </span>
                      </div>
                      <div className={styles.logContent}>{entry.content}</div>
                    </div>
                  ))
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
