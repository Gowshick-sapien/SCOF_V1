import React, { useEffect, useState } from "react";
import styles from "./TopBar.module.css";
import { useConnection } from "../../state/connection";

interface TopBarProps {
  currentViewLabel: string;
  isChatOpen: boolean;
  onToggleChat: () => void;
}

export const TopBar: React.FC<TopBarProps> = ({
  currentViewLabel,
  isChatOpen,
  onToggleChat,
}) => {
  const { state } = useConnection();
  const [timeStr, setTimeStr] = useState("");

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTimeStr(now.toISOString().replace("T", " ").substring(0, 19) + " UTC");
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className={styles.topbar}>
      <div className={styles.leftSection}>
        <h2 className={styles.viewTitle}>{currentViewLabel}</h2>
        <div className={styles.profileBadge}>
          <span>PROFILE: MVP-ELECTRONICS</span>
        </div>
        <div style={{ fontSize: "12px", display: "flex", alignItems: "center", gap: "6px" }}>
          <span
            style={{
              width: "8px",
              height: "8px",
              borderRadius: "50%",
              backgroundColor:
                state.overallStatus === "Connected"
                  ? "var(--status-healthy)"
                  : state.overallStatus === "Reconnecting"
                  ? "var(--status-warning)"
                  : "var(--status-critical)",
            }}
          />
          <span style={{ color: "var(--text-muted)", fontSize: "11px", fontFamily: "var(--font-mono)" }}>
            {state.overallStatus.toUpperCase()}
          </span>
        </div>
      </div>

      <div className={styles.rightSection}>
        <div className={styles.clock}>{timeStr}</div>

        <button
          className={`${styles.chatToggleBtn} ${isChatOpen ? styles.chatToggleBtnActive : ""}`}
          onClick={onToggleChat}
        >
          <span>AI Assistant</span>
        </button>
      </div>
    </header>
  );
};
