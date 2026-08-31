import React, { useEffect, useState } from "react";
import styles from "./Scenarios.module.css";
import { apiClient } from "../../api/client";

interface ScenarioItem {
  scenario_id: string;
  name: string;
  disruption_type: string;
  target_entity: string;
  description: string;
  severity: number;
}

const DEFAULT_SCENARIOS: ScenarioItem[] = [
  {
    scenario_id: "scen-01",
    name: "Baseline Nominal Operations",
    disruption_type: "none",
    target_entity: "global",
    description: "Standard operating environment with predictable supply & demand.",
    severity: 1,
  },
  {
    scenario_id: "scen-02",
    name: "Tier-1 Semiconductor Supplier Delay",
    disruption_type: "supplier_delay",
    target_entity: "sup-01",
    description: "5-day component delivery delay from Global Silicon triggering inventory alerts.",
    severity: 4,
  },
  {
    scenario_id: "scen-03",
    name: "Consumer Electronics Demand Spike",
    disruption_type: "demand_spike",
    target_entity: "wh-01",
    description: "Sudden 45% surge in regional customer orders.",
    severity: 3,
  },
  {
    scenario_id: "scen-04",
    name: "Cross-Border Logistics Port Congestion",
    disruption_type: "transport_failure",
    target_entity: "mfg-01",
    description: "Customs blockage and freight route delay along primary shipping lane.",
    severity: 4,
  },
];

export const ScenariosView: React.FC = () => {
  const [scenarios, setScenarios] = useState<ScenarioItem[]>(DEFAULT_SCENARIOS);
  const [selectedScenario, setSelectedScenario] = useState<ScenarioItem>(DEFAULT_SCENARIOS[1]);
  const [severity, setSeverity] = useState<number>(4);
  const [isTriggering, setIsTriggering] = useState<boolean>(false);
  const [triggerResult, setTriggerResult] = useState<{
    event_id?: string;
    trace_id?: string;
    status?: string;
  } | null>(null);

  useEffect(() => {
    let mounted = true;
    apiClient
      .getScenarios()
      .then((res: any) => {
        if (mounted && res && Array.isArray(res.scenarios)) {
          setScenarios(res.scenarios);
        }
      })
      .catch(() => {
        // Fall back to predefined defaults
      });
    return () => {
      mounted = false;
    };
  }, []);

  const handleTrigger = async () => {
    if (!selectedScenario) return;
    setIsTriggering(true);
    setTriggerResult(null);

    try {
      const res = await apiClient.triggerScenario(selectedScenario.scenario_id);
      setTriggerResult({
        event_id: res.event_id,
        trace_id: res.trace_id,
        status: res.status || "TRIGGERED",
      });
    } catch (err: any) {
      setTriggerResult({
        status: "FAILED: " + (err.message || "Could not trigger disruption"),
      });
    } finally {
      setIsTriggering(false);
    }
  };

  return (
    <div className={styles.container}>
      {/* Left Column: Scenario Catalog */}
      <div className={styles.libraryColumn}>
        <div className={styles.sectionHeader}>
          <span className={styles.sectionTitle}>Scenario Library</span>
          <span style={{ fontSize: "11px", color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>
            {scenarios.length} SCENARIOS
          </span>
        </div>

        <div className={styles.tableWrapper}>
          <table className={styles.scenarioTable}>
            <thead>
              <tr>
                <th>ID</th>
                <th>Scenario Name</th>
                <th>Disruption Type</th>
                <th>Target</th>
                <th>Severity</th>
              </tr>
            </thead>
            <tbody>
              {scenarios.map((scen) => {
                const isSelected = selectedScenario?.scenario_id === scen.scenario_id;
                return (
                  <tr
                    key={scen.scenario_id}
                    className={`${styles.scenarioRow} ${isSelected ? styles.scenarioRowSelected : ""}`}
                    onClick={() => {
                      setSelectedScenario(scen);
                      setSeverity(scen.severity || 3);
                    }}
                  >
                    <td className={styles.scenarioId}>{scen.scenario_id}</td>
                    <td style={{ fontWeight: 600, color: "var(--text-primary)" }}>{scen.name}</td>
                    <td>
                      <span className={styles.disruptionTag}>{scen.disruption_type}</span>
                    </td>
                    <td style={{ fontFamily: "var(--font-mono)", fontSize: "12px" }}>
                      {scen.target_entity}
                    </td>
                    <td style={{ fontFamily: "var(--font-mono)" }}>{scen.severity || 1} / 5</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Right Column: Scenario Trigger Launcher */}
      <div className={styles.launcherColumn}>
        <div className={styles.formCard}>
          <div className={styles.sectionHeader} style={{ padding: 0, border: "none" }}>
            <span className={styles.sectionTitle}>Disruption Trigger Launcher</span>
          </div>

          <div className={styles.formGroup}>
            <label className={styles.label}>Selected Scenario</label>
            <select
              className={styles.select}
              value={selectedScenario.scenario_id}
              onChange={(e) => {
                const found = scenarios.find((s) => s.scenario_id === e.target.value);
                if (found) {
                  setSelectedScenario(found);
                  setSeverity(found.severity || 3);
                }
              }}
            >
              {scenarios.map((s) => (
                <option key={s.scenario_id} value={s.scenario_id}>
                  {s.scenario_id} - {s.name}
                </option>
              ))}
            </select>
          </div>

          <div className={styles.formGroup}>
            <label className={styles.label}>Disruption Type</label>
            <input
              type="text"
              className={styles.input}
              value={selectedScenario.disruption_type}
              readOnly
            />
          </div>

          <div className={styles.formGroup}>
            <label className={styles.label}>Target Node</label>
            <input
              type="text"
              className={styles.input}
              value={selectedScenario.target_entity}
              readOnly
            />
          </div>

          <div className={styles.formGroup}>
            <label className={styles.label}>Severity Level</label>
            <div className={styles.sliderRow}>
              <input
                type="range"
                min="1"
                max="5"
                value={severity}
                onChange={(e) => setSeverity(Number(e.target.value))}
                className={styles.slider}
              />
              <span className={styles.sliderValue}>{severity}</span>
            </div>
          </div>

          <button
            className={styles.triggerButton}
            onClick={handleTrigger}
            disabled={isTriggering}
          >
            {isTriggering ? "Publishing to Kafka Bus..." : "Trigger Scenario Disruption"}
          </button>
        </div>

        {triggerResult && (
          <div className={styles.statusCard}>
            <span className={styles.statusTitle}>Dispatch Result</span>
            {triggerResult.event_id && (
              <span className={styles.statusItem}>Event ID: {triggerResult.event_id}</span>
            )}
            {triggerResult.trace_id && (
              <span className={styles.statusItem}>Trace ID: {triggerResult.trace_id}</span>
            )}
            {triggerResult.status && (
              <span className={styles.statusItem} style={{ color: "var(--accent-cyan)", fontWeight: "bold" }}>
                Status: {triggerResult.status}
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
