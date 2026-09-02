import React from "react";
import styles from "./Sidebar.module.css";
import { getCurrentWindow } from "@tauri-apps/api/window";

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
}

interface NavItemConfig {
  key: ViewKey;
  label: string;
  shortcut: string;
  icon: React.ReactNode;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeView, onSelectView }) => {
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

  const controlRoomItems: NavItemConfig[] = [
    {
      key: "operations",
      label: "Operations",
      shortcut: "Ctrl 1",
      icon: (
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
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
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
        </svg>
      ),
    },
    {
      key: "scenarios",
      label: "Scenarios",
      shortcut: "Ctrl 3",
      icon: (
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
        </svg>
      ),
    },
    {
      key: "agents",
      label: "Agent Command",
      shortcut: "Ctrl 4",
      icon: (
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
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
  ];

  const intelligenceItems: NavItemConfig[] = [
    {
      key: "whatif",
      label: "What-If Lab",
      shortcut: "Ctrl 5",
      icon: (
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
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
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <line x1="6" y1="3" x2="6" y2="15" />
          <circle cx="18" cy="6" r="3" />
          <circle cx="6" cy="18" r="3" />
          <path d="M18 9a9 9 0 0 1-9 9" />
        </svg>
      ),
    },
    {
      key: "evaluation",
      label: "Evaluation",
      shortcut: "Ctrl 7",
      icon: (
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <line x1="18" y1="20" x2="18" y2="10" />
          <line x1="12" y1="20" x2="12" y2="4" />
          <line x1="6" y1="20" x2="6" y2="14" />
        </svg>
      ),
    },
  ];

  const renderNavGroup = (items: NavItemConfig[]) => {
    return items.map((item) => {
      const isActive = activeView === item.key;
      return (
        <button
          key={item.key}
          className={`${styles.navItem} ${isActive ? styles.navItemActive : ""}`}
          onClick={() => onSelectView(item.key)}
        >
          <div className={styles.itemLeft}>
            <span className={styles.navIcon}>{item.icon}</span>
            <span>{item.label}</span>
          </div>
          <span className={styles.shortcutBadge}>{item.shortcut}</span>
        </button>
      );
    });
  };

  return (
    <aside className={styles.sidebar}>
      {/* Functional macOS Window Traffic Lights */}
      <div className={styles.trafficLights}>
        <button
          className={`${styles.trafficDot} ${styles.dotRed}`}
          onClick={handleClose}
          title="Close Window"
          aria-label="Close Window"
        >
          <span className={styles.dotIcon}>✕</span>
        </button>
        <button
          className={`${styles.trafficDot} ${styles.dotYellow}`}
          onClick={handleMinimize}
          title="Minimize Window"
          aria-label="Minimize Window"
        >
          <span className={styles.dotIcon}>−</span>
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
      <div className={styles.brand}>
        <div className={styles.brandIcon}>S</div>
        <div className={styles.brandTitle}>SCOF Operations</div>
      </div>

      {/* Navigation Groups */}
      <nav className={styles.nav}>
        <div className={styles.sectionHeading}>Control Room</div>
        {renderNavGroup(controlRoomItems)}

        <div className={styles.sectionHeading}>Intelligence & Provenance</div>
        {renderNavGroup(intelligenceItems)}
      </nav>

      {/* macOS Minimal Footer */}
      <div className={styles.footer}>
        <div className={styles.statusIndicator}>
          <span className={styles.statusDot} />
          <span>A2A Live</span>
        </div>
        <span className={styles.versionTag}>v1.0.0</span>
      </div>
    </aside>
  );
};
