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

const DISRUPTION_TYPE_OPTIONS = [
  { value: "supplier_delay", label: "supplier_delay (Tier-1 Semiconductor Supplier Delay)" },
  { value: "demand_spike", label: "demand_spike (Consumer Electronics Demand Surge)" },
  { value: "transport_failure", label: "transport_failure (Cross-Border Route Blockage)" },
  { value: "adverse_weather", label: "adverse_weather (Severe Weather Logistics Delay)" },
  { value: "none", label: "none (Nominal Baseline Operations)" },
];

const TARGET_ENTITY_OPTIONS = [
  { value: "sup-01", label: "sup-01 (Pacific Semi - Tier 1 Supplier)" },
  { value: "sup-02", label: "sup-02 (Global Silicon - Tier 1 Supplier)" },
  { value: "sup-03", label: "sup-03 (Apex Microdevices - Alternate Supplier)" },
  { value: "mfg-01", label: "mfg-01 (Shenzhen Assembly Hub)" },
  { value: "wh-01", label: "wh-01 (Frankfurt Regional Distribution Center)" },
  { value: "route-sup-01-wh-01", label: "route-sup-01-wh-01 (Primary Freight Shipping Lane)" },
  { value: "global", label: "global (Global Supply Chain Network)" },
];

const DEFAULT_SCENARIOS: ScenarioItem[] = [
  {
    scenario_id: "scen-01",
    name: "Baseline Nominal Operations",
    disruption_type: "none",
    target_entity: "global",
    description: "Standard operating environment with predictable supply and demand.",
    severity: 1,
  },
  {
    scenario_id: "scen-02",
    name: "Tier-1 Semiconductor Supplier Delay",
    disruption_type: "supplier_delay",
    target_entity: "sup-01",
    description: "5-day component delivery delay from Pacific Semi triggering inventory and supplier arbitration.",
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
    name: "Cross-Border Logistics Route Failure",
    disruption_type: "transport_failure",
    target_entity: "route-sup-01-wh-01",
    description: "Customs blockage and freight route delay along primary shipping lane.",
    severity: 5,
  },
];

export const ScenariosView: React.FC = () => {
  const [scenarios, setScenarios] = useState<ScenarioItem[]>(DEFAULT_SCENARIOS);
  const [selectedScenario, setSelectedScenario] = useState<ScenarioItem>(DEFAULT_SCENARIOS[1]);
  const [customDisruptionType, setCustomDisruptionType] = useState<string>("supplier_delay");
  const [customTarget, setCustomTarget] = useState<string>("sup-01");
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
        if (mounted && res && Array.isArray(res.scenarios) && res.scenarios.length > 0) {
          // Merge API results with rich scenario definitions
          const merged = res.scenarios.map((apiScen: any) => {
            const def = DEFAULT_SCENARIOS.find((d) => d.scenario_id === apiScen.scenario_id);
            return {
              scenario_id: apiScen.scenario_id,
              name: def?.name || apiScen.name || apiScen.scenario_id,
              disruption_type: apiScen.disruption_type || def?.disruption_type || "none",
              target_entity: apiScen.target_entity || def?.target_entity || "global",
              description: apiScen.description || def?.description || "",
              severity: apiScen.severity || def?.severity || 3,
            };
          });

          // Ensure all default catalog scenarios are visible
          DEFAULT_SCENARIOS.forEach((def) => {
            if (!merged.some((m: ScenarioItem) => m.scenario_id === def.scenario_id)) {
              merged.push(def);
            }
          });

          setScenarios(merged);

          // Default selection to scen-02 if available
          const scen02 = merged.find((s: ScenarioItem) => s.scenario_id === "scen-02") || merged[0];
          setSelectedScenario(scen02);
          setCustomDisruptionType(scen02.disruption_type);
          setCustomTarget(scen02.target_entity);
          setSeverity(scen02.severity);
        }
      })
      .catch(() => {
        // Fall back to predefined defaults
      });
    return () => {
      mounted = false;
    };
  }, []);

  const handleSelectScenario = (scen: ScenarioItem) => {
    setSelectedScenario(scen);
    setCustomDisruptionType(scen.disruption_type);
    setCustomTarget(scen.target_entity);
    setSeverity(scen.severity || 3);
  };

  const handleTrigger = async () => {
    if (!selectedScenario) return;
    setIsTriggering(true);
    setTriggerResult(null);

    try {
      const res = await apiClient.triggerScenario(selectedScenario.scenario_id, {
        disruption_type: customDisruptionType,
        target_entity_id: customTarget,
        severity: severity,
      });

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
            {scenarios.length} SCENARIOS AVAILABLE
          </span>
        </div>

        <div className={styles.tableWrapper}>
          <table className={styles.scenarioTable}>
            <thead>
              <tr>
                <th>ID</th>
                <th>Scenario Title</th>
                <th>Disruption Type</th>
                <th>Target Node</th>
                <th>Severity</th>
                <th style={{ textAlign: "right" }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {scenarios.map((scen) => {
                const isSelected = selectedScenario?.scenario_id === scen.scenario_id;
                return (
                  <tr
                    key={scen.scenario_id}
                    className={`${styles.scenarioRow} ${isSelected ? styles.scenarioRowSelected : ""}`}
                    onClick={() => handleSelectScenario(scen)}
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
                    <td style={{ textAlign: "right" }}>
                      {isSelected ? (
                        <button className={styles.activeBtn} disabled>
                          ACTIVE
                        </button>
                      ) : (
                        <button
                          className={styles.selectBtn}
                          onClick={(e) => {
                            e.stopPropagation();
                            handleSelectScenario(scen);
                          }}
                        >
                          Select
                        </button>
                      )}
                    </td>
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

          {/* Scenario Selector */}
          <div className={styles.formGroup}>
            <label className={styles.label}>Active Scenario</label>
            <select
              className={styles.select}
              value={selectedScenario.scenario_id}
              onChange={(e) => {
                const found = scenarios.find((s) => s.scenario_id === e.target.value);
                if (found) {
                  handleSelectScenario(found);
                }
              }}
            >
              {scenarios.map((s) => (
                <option key={s.scenario_id} value={s.scenario_id}>
                  [{s.scenario_id}] {s.name}
                </option>
              ))}
            </select>
          </div>

          {/* Disruption Type Selector */}
          <div className={styles.formGroup}>
            <label className={styles.label}>Disruption Type</label>
            <select
              className={styles.select}
              value={customDisruptionType}
              onChange={(e) => setCustomDisruptionType(e.target.value)}
            >
              {DISRUPTION_TYPE_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>

          {/* Target Node Selector */}
          <div className={styles.formGroup}>
            <label className={styles.label}>Target Node</label>
            <select
              className={styles.select}
              value={customTarget}
              onChange={(e) => setCustomTarget(e.target.value)}
            >
              {TARGET_ENTITY_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>

          {/* Severity Level Slider */}
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
              <span className={styles.sliderValue}>{severity} / 5</span>
            </div>
          </div>

          {/* Explicit Trigger Button */}
          <button
            className={styles.triggerButton}
            onClick={handleTrigger}
            disabled={isTriggering}
          >
            {isTriggering
              ? "Publishing Disruption to Kafka Bus..."
              : `Trigger Disruption: [${selectedScenario.scenario_id.toUpperCase()}] ${selectedScenario.name}`}
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
