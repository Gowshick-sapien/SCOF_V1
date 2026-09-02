import React, { useEffect, useState } from "react";
import styles from "./NotificationToast.module.css";
import { useDecisions } from "../../hooks/useDecisions";
import type { DecisionRecord } from "../../api/types";

interface ToastItem {
  id: string;
  scenarioId: string;
  recommendation: string;
  confidence: number;
  escalationTier: string;
}

interface NotificationToastProps {
  onSelectDecision?: (decisionId: string) => void;
}

export const NotificationToast: React.FC<NotificationToastProps> = ({ onSelectDecision }) => {
  const liveEvents = useDecisions();
  const [toasts, setToasts] = useState<ToastItem[]>([]);

  useEffect(() => {
    if (liveEvents.length === 0) return;
    const latest = liveEvents[0];
    if (latest.type === "completed" && latest.payload.decision_record) {
      const rec: DecisionRecord = latest.payload.decision_record;
      const toastId = rec.decision_id;

      setToasts((prev) => {
        if (prev.some((t) => t.id === toastId)) return prev;
        const newToast: ToastItem = {
          id: toastId,
          scenarioId: rec.scenario_id,
          recommendation: rec.final_recommendation || "Arbitration complete.",
          confidence: rec.decision_confidence,
          escalationTier: rec.escalation_tier,
        };
        return [newToast, ...prev].slice(0, 3);
      });

      // Auto-dismiss after 7 seconds
      const timer = setTimeout(() => {
        setToasts((prev) => prev.filter((t) => t.id !== toastId));
      }, 7000);

      return () => clearTimeout(timer);
    }
  }, [liveEvents]);

  const handleDismiss = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  const handleInspect = (id: string) => {
    handleDismiss(id);
    onSelectDecision?.(id);
  };

  if (toasts.length === 0) return null;

  return (
    <div className={styles.container}>
      {toasts.map((toast) => {
        const isEscalated = toast.escalationTier === "HUMAN_ESCALATION";
        return (
          <div
            key={toast.id}
            className={`${styles.toast} ${isEscalated ? styles.escalated : styles.normal}`}
          >
            <div className={styles.header}>
              <div className={styles.titleRow}>
                <span className={styles.scenarioTag}>{toast.scenarioId.toUpperCase()}</span>
                <span
                  className={`${styles.tierBadge} ${
                    isEscalated ? styles.tierEscalated : styles.tierStandard
                  }`}
                >
                  {toast.escalationTier}
                </span>
              </div>
              <button
                className={styles.closeBtn}
                onClick={() => handleDismiss(toast.id)}
                aria-label="Dismiss"
              >
                ✕
              </button>
            </div>

            <p className={styles.recommendation}>{toast.recommendation}</p>

            <div className={styles.footer}>
              <span>WCS: {(toast.confidence * 100).toFixed(1)}%</span>
              <button
                className={styles.inspectBtn}
                onClick={() => handleInspect(toast.id)}
              >
                Inspect Decision →
              </button>
            </div>
          </div>
        );
      })}
    </div>
  );
};
