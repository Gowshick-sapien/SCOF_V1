import React, { useState } from "react";
import styles from "./Sidebar.module.css";
import { getCurrentWindow } from "@tauri-apps/api/window";
import { useConnection } from "../../state/connection";

export type ViewKey =
  | "operations"
  | "decisions"
  | "scenarios"
  | "agents"
  | "whatif"
  | "traces"
  | "evaluation";

interface SidebarProps {
  activeView: ViewKey;
  onSelectView: (view: ViewKey) => void;
  onOpenSettings?: () => void;
  isExpanded?: boolean;
  onToggleExpand?: () => void;
}

interface NavItemConfig {
  key: ViewKey;
  label: string;
  shortcut: string;
  icon: React.ReactNode;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeView,
  onSelectView,
  onOpenSettings,
  isExpanded: externalIsExpanded,
  onToggleExpand: externalToggleExpand,
}) => {
  const [internalExpanded, setInternalExpanded] = useState(false);
  const isExpanded = externalIsExpanded !== undefined ? externalIsExpanded : internalExpanded;
  const toggleExpand = externalToggleExpand || (() => setInternalExpanded((prev) => !prev));

  const { state } = useConnection();

  const handleClose = async () => {
    try {
      const appWindow = getCurrentWindow();
      await appWindow.close();
    } catch {
      window.close();
    }
  };

  const handleMinimize = async () => {
    try {
      const appWindow = getCurrentWindow();
      await appWindow.minimize();
    } catch {
      console.log("Minimize window");
    }
  };

  const handleMaximize = async () => {
    try {
      const appWindow = getCurrentWindow();
      await appWindow.toggleMaximize();
    } catch {
      if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch(() => {});
      } else {
        document.exitFullscreen().catch(() => {});
      }
    }
  };

  const navigationItems: NavItemConfig[] = [
    {
      key: "operations",
      label: "Operations Overview",
      shortcut: "Ctrl 1",
      icon: (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="3" y="3" width="7" height="7" rx="1" />
          <rect x="14" y="3" width="7" height="7" rx="1" />
          <rect x="14" y="14" width="7" height="7" rx="1" />
          <rect x="3" y="14" width="7" height="7" rx="1" />
        </svg>
      ),
    },
    {
      key: "decisions",
      label: "Decision Center",
      shortcut: "Ctrl 2",
      icon: (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
        </svg>
      ),
    },
    {
      key: "scenarios",
      label: "Scenario Launcher",
      shortcut: "Ctrl 3",
      icon: (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
        </svg>
      ),
    },
    {
      key: "agents",
      label: "Agent Command",
      shortcut: "Ctrl 4",
      icon: (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="4" y="4" width="16" height="16" rx="2" />
          <rect x="9" y="9" width="6" height="6" />
          <line x1="9" y1="1" x2="9" y2="4" />
          <line x1="15" y1="1" x2="15" y2="4" />
          <line x1="9" y1="20" x2="9" y2="23" />
          <line x1="15" y1="20" x2="15" y2="23" />
          <line x1="20" y1="9" x2="23" y2="9" />
          <line x1="20" y1="14" x2="23" y2="14" />
          <line x1="1" y1="9" x2="4" y2="9" />
          <line x1="1" y1="14" x2="4" y2="14" />
        </svg>
      ),
    },
    {
      key: "whatif",
      label: "What-If Simulation Lab",
      shortcut: "Ctrl 5",
      icon: (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <line x1="4" y1="21" x2="4" y2="14" />
          <line x1="4" y1="10" x2="4" y2="3" />
          <line x1="12" y1="21" x2="12" y2="12" />
          <line x1="12" y1="8" x2="12" y2="3" />
          <line x1="20" y1="21" x2="20" y2="16" />
          <line x1="20" y1="12" x2="20" y2="3" />
          <line x1="1" y1="14" x2="7" y2="14" />
          <line x1="9" y1="8" x2="15" y2="8" />
          <line x1="17" y1="16" x2="23" y2="16" />
        </svg>
      ),
    },
    {
      key: "traces",
      label: "Reasoning Traces",
      shortcut: "Ctrl 6",
      icon: (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <line x1="6" y1="3" x2="6" y2="15" />
          <circle cx="18" cy="6" r="3" />
          <circle cx="6" cy="18" r="3" />
          <path d="M18 9a9 9 0 0 1-9 9" />
        </svg>
      ),
    },
    {
      key: "evaluation",
      label: "Evaluation Matrix",
      shortcut: "Ctrl 7",
      icon: (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <line x1="18" y1="20" x2="18" y2="10" />
          <line x1="12" y1="20" x2="12" y2="4" />
          <line x1="6" y1="20" x2="6" y2="14" />
        </svg>
      ),
    },
  ];

  return (
    <aside
      className={`${styles.sidebar} ${isExpanded ? styles.sidebarExpanded : styles.sidebarCollapsed}`}
      aria-label="Application Navigation Rail"
    >
      {/* Functional Window Traffic Dots */}
      <div className={styles.trafficLights}>
        <button
          className={`${styles.trafficDot} ${styles.dotRed}`}
          onClick={handleClose}
          title="Close Window"
          aria-label="Close Window"
        >
          <span className={styles.dotIcon}>x</span>
        </button>
        <button
          className={`${styles.trafficDot} ${styles.dotYellow}`}
          onClick={handleMinimize}
          title="Minimize Window"
          aria-label="Minimize Window"
        >
          <span className={styles.dotIcon}>-</span>
        </button>
        <button
          className={`${styles.trafficDot} ${styles.dotGreen}`}
          onClick={handleMaximize}
          title="Zoom / Maximize Window"
          aria-label="Zoom Window"
        >
          <span className={styles.dotIcon}>+</span>
        </button>
      </div>

      {/* Brand Header */}
      <div
        className={styles.brand}
        onClick={toggleExpand}
        title={isExpanded ? "Click to collapse rail" : "Click to expand rail"}
      >
        <div className={styles.brandIcon}>S</div>
        {isExpanded && <div className={styles.brandTitle}>SCOF Operations</div>}
      </div>

      {/* Primary Navigation: 7 Canonical Destinations */}
      <nav className={styles.nav}>
        {isExpanded ? (
          <div className={styles.sectionHeading}>Platform Workspaces</div>
        ) : (
          <div className={styles.sectionDivider} />
        )}

        {navigationItems.map((item) => {
          const isActive = activeView === item.key;
          return (
            <button
              key={item.key}
              className={`${styles.navItem} ${isActive ? styles.navItemActive : ""}`}
              onClick={() => onSelectView(item.key)}
              title={`${item.label} (${item.shortcut})`}
              aria-label={item.label}
            >
              <div className={styles.itemLeft}>
                <span className={styles.navIcon}>{item.icon}</span>
                {isExpanded && <span className={styles.navLabel}>{item.label}</span>}
              </div>
              {isExpanded && (
                <span className={styles.shortcutBadge}>{item.shortcut}</span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Operations Footer */}
      <div className={styles.footer}>
        <div
          className={styles.statusIndicator}
          title={`Status: ${state.statusLabel} - ${state.footerTag}`}
        >
          <span
            className={styles.statusDot}
            style={{ backgroundColor: state.statusColor }}
          />
          {isExpanded && (
            <span className={styles.statusText}>{state.footerTag}</span>
          )}
        </div>

        <div
          className={styles.profileBadge}
          title="Active Domain Profile: MVP-ELECTRONICS (Peninsular Corridor)"
        >
          <span>{isExpanded ? "MVP-ELECTRONICS" : "MVP"}</span>
        </div>

        {onOpenSettings && (
          <button
            className={styles.actionBtn}
            onClick={onOpenSettings}
            title="Settings & Diagnostics"
            aria-label="Settings and Diagnostics"
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="3" />
              <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" />
            </svg>
            {isExpanded && <span>Settings</span>}
          </button>
        )}

        <button
          className={styles.railToggleBtn}
          onClick={toggleExpand}
          title={isExpanded ? "Collapse rail (Ctrl + B)" : "Expand rail (Ctrl + B)"}
          aria-label={isExpanded ? "Collapse Navigation Rail" : "Expand Navigation Rail"}
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            {isExpanded ? (
              <polyline points="11 19 4 12 11 5" />
            ) : (
              <polyline points="13 5 20 12 13 19" />
            )}
          </svg>
          {isExpanded && <span>Collapse</span>}
        </button>
      </div>
    </aside>
  );
};
