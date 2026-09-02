import React from "react";
import styles from "./Sidebar.module.css";

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

interface NavConfig {
  key: ViewKey;
  label: string;
  shortcut: string;
}

const NAV_ITEMS: NavConfig[] = [
  { key: "operations", label: "Operations", shortcut: "Ctrl+1" },
  { key: "decisions", label: "Decision Center", shortcut: "Ctrl+2" },
  { key: "scenarios", label: "Scenarios", shortcut: "Ctrl+3" },
  { key: "agents", label: "Agent Command", shortcut: "Ctrl+4" },
  { key: "whatif", label: "What-If Lab", shortcut: "Ctrl+5" },
  { key: "traces", label: "Reasoning Traces", shortcut: "Ctrl+6" },
  { key: "evaluation", label: "Evaluation", shortcut: "Ctrl+7" },
];

export const Sidebar: React.FC<SidebarProps> = ({ activeView, onSelectView }) => {
  return (
    <aside className={styles.sidebar}>
      <div className={styles.brand}>
        <div className={styles.brandIcon}>S</div>
        <div className={styles.brandTitle}>SCOF CONSOLE</div>
      </div>

      <nav className={styles.nav}>
        {NAV_ITEMS.map((item) => {
          const isActive = activeView === item.key;
          return (
            <button
              key={item.key}
              className={`${styles.navItem} ${isActive ? styles.navItemActive : ""}`}
              onClick={() => onSelectView(item.key)}
            >
              <span>{item.label}</span>
              <span className={styles.shortcutBadge}>{item.shortcut}</span>
            </button>
          );
        })}
      </nav>

      <div className={styles.footer}>
        <span>Tauri Native</span>
        <span className={styles.versionTag}>v1.0.0</span>
      </div>
    </aside>
  );
};
