import React, { useEffect, useState } from "react";
import styles from "./TopBar.module.css";
import { useConnection } from "../../state/connection";

interface TopBarProps {
  currentViewLabel: string;
  isChatOpen?: boolean;
  onToggleChat?: () => void;
  onOpenShortcuts?: () => void;
}

export const TopBar: React.FC<TopBarProps> = ({
  currentViewLabel,
  onOpenShortcuts,
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

  const getStatusColor = () => {
    switch (state.overallStatus) {
      case "Connected":
        return "var(--status-healthy)";
      case "Reconnecting":
        return "var(--status-warning)";
      default:
        return "var(--status-critical)";
    }
  };

  return (
    <header className={styles.topbar}>
      <div className={styles.leftSection}>
        <h2 className={styles.viewTitle}>{currentViewLabel}</h2>
        <div className={styles.profileBadge}>
          <span>MVP-ELECTRONICS</span>
        </div>
        <div className={styles.statusPill}>
          <span
            className={styles.statusDot}
            style={{ backgroundColor: getStatusColor() }}
          />
          <span className={styles.statusLabel}>
            {state.overallStatus.toUpperCase()}
          </span>
        </div>
      </div>

      <div className={styles.rightSection}>
        <div className={styles.clock}>{timeStr}</div>

        {onOpenShortcuts && (
          <button
            className={styles.shortcutsBtn}
            onClick={onOpenShortcuts}
            title="Shortcuts HUD (Shift + ?)"
            aria-label="Keyboard Shortcuts"
          >
            ?
          </button>
        )}
      </div>
    </header>
  );
};
