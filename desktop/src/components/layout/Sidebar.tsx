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
  badge?: string;
}

const NAV_ITEMS: NavConfig[] = [
  { key: "operations", label: "Operations" },
  { key: "decisions", label: "Decision Center" },
  { key: "scenarios", label: "Scenarios" },
  { key: "agents", label: "Agent Command" },
  { key: "whatif", label: "What-If Lab" },
  { key: "traces", label: "Reasoning Traces" },
  { key: "evaluation", label: "Evaluation" },
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
