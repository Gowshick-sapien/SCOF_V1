import React from "react";
import styles from "./ConnectionBanner.module.css";
import { useConnection } from "../../state/connection";

export const ConnectionBanner: React.FC = () => {
  const { state } = useConnection();

  if (state.derivedStatus === "CONNECTED") {
    return null;
  }

  const formatSyncTime = (iso: string | null) => {
    if (!iso) return "None";
    try {
      const d = new Date(iso);
      return d.toISOString().substring(11, 19) + " UTC";
    } catch {
      return "Unknown";
    }
  };

  const isOffline = state.derivedStatus === "OFFLINE_CACHED";
  const isReconnecting = state.derivedStatus === "RECONNECTING";
  const isDegraded = state.derivedStatus === "DEGRADED";

  const bannerClass = isOffline
    ? styles.disconnected
    : isReconnecting
    ? styles.reconnecting
    : styles.degraded;

  const dotClass = isOffline
    ? styles.dotDisconnected
    : isReconnecting
    ? styles.dotReconnecting
    : styles.dotDegraded;

  return (
    <div className={`${styles.banner} ${bannerClass}`}>
      <div className={styles.left}>
        <span className={`${styles.dot} ${dotClass}`} />
        <span>
          {isOffline && (
            <>
              Connection to SCOF backend offline.{" "}
              <span className={styles.cachedTag}>
                [CACHED DATA - Last synced: {formatSyncTime(state.lastSuccessfulSync)}]
              </span>
            </>
          )}
          {isReconnecting && (
            <>
              Reconnecting to SCOF event streams ({state.streamsConnected}/3 connected)... Live telemetry may lag.
            </>
          )}
          {isDegraded && (
            <>
              Event streams degraded ({state.streamsConnected}/3 connected). REST API nominal.
            </>
          )}
        </span>
      </div>

      <div className={styles.retryText}>
        {isOffline && "A2A Gateway Unreachable (:8000) - Check Docker stack"}
        {isReconnecting && "Auto-retrying WebSocket transport"}
        {isDegraded && state.footerTag}
      </div>
    </div>
  );
};
