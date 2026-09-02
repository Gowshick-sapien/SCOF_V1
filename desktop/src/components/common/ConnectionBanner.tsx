import React from "react";
import styles from "./ConnectionBanner.module.css";
import { useConnection } from "../../state/connection";

export const ConnectionBanner: React.FC = () => {
  const { state } = useConnection();

  if (state.overallStatus === "Connected") {
    return null;
  }

  const isReconnecting = state.overallStatus === "Reconnecting";

  return (
    <div
      className={`${styles.banner} ${
        isReconnecting ? styles.reconnecting : styles.disconnected
      }`}
    >
      <div className={styles.left}>
        <span
          className={`${styles.dot} ${
            isReconnecting ? styles.dotReconnecting : styles.dotDisconnected
          }`}
        />
        <span>
          {isReconnecting
            ? "Reconnecting to SCOF API Gateway and Event Bus..."
            : "Connection to SCOF backend lost. Operating in offline/cached mode."}
        </span>
      </div>

      <div className={styles.retryText}>
        {isReconnecting ? "Auto-retrying WebSocket stream" : "Check Docker stack & services"}
      </div>
    </div>
  );
};
