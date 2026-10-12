import React, { useEffect, useState, useMemo } from "react";
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
  { value: "demand_spike", label: "demand_spike (Automotive / IoT Demand Surge)" },
  { value: "transport_failure", label: "transport_failure (Interstate Highway / Logistics Corridor Breakdown)" },
  { value: "adverse_weather", label: "adverse_weather (Coastal Monsoon & Cyclonic Inundation)" },
  { value: "none", label: "none (Nominal Baseline Operations)" },
];

const TARGET_ENTITY_OPTIONS = [
  { value: "sup-01", label: "sup-01 (SPEL Semiconductor - Maraimalai Nagar, Chennai)" },
  { value: "sup-02", label: "sup-02 (Continental Device India CDIL - Electronic City, Bengaluru)" },
  { value: "sup-03", label: "sup-03 (Kaynes Technology - Koorgalli, Mysuru)" },
  { value: "sup-04", label: "sup-04 (Syrma SGS Technology - Bargur Industrial Estate)" },
  { value: "sup-05", label: "sup-05 (Centum Electronics - Yelahanka, Bengaluru)" },
  { value: "sup-06", label: "sup-06 (Vinyas Innovative Technologies - Hebbal, Mysuru)" },
  { value: "sup-07", label: "sup-07 (SFO Technologies NeST - Kakkanad, Kochi)" },
  { value: "sup-08", label: "sup-08 (Sahasra Electronic Solutions - Hyderabad)" },
  { value: "mfg-01", label: "mfg-01 (Sriperumbudur High-Tech Assembly Plant)" },
  { value: "wh-01", label: "wh-01 (Hosur Logistics Buffer Warehouse)" },
  { value: "wh-02", label: "wh-02 (Whitefield Inland Container Depot)" },
  { value: "wh-03", label: "wh-03 (Oragadam JIT Supplier Warehouse)" },
  { value: "wh-04", label: "wh-04 (Sri City FTWZ Logistics Center)" },
  { value: "dc-01", label: "dc-01 (Chennai Port Container Terminal)" },
  { value: "dc-02", label: "dc-02 (Cochin Port Vallarpadam Terminal)" },
  { value: "dc-03", label: "dc-03 (Hyderabad Air Cargo Gateway)" },
  { value: "route-wh-01-mfg-01", label: "route-wh-01-mfg-01 (Hosur-Sriperumbudur NH48 Freight Corridor)" },
  { value: "route-sup-02-wh-01", label: "route-sup-02-wh-01 (Bengaluru-Hosur NH44 Freight Lane)" },
  { value: "route-sup-07-mfg-01", label: "route-sup-07-mfg-01 (Kochi-Sriperumbudur Inter-State Corridor)" },
  { value: "route-sup-08-wh-04", label: "route-sup-08-wh-04 (Hyderabad-Sri City Corridor)" },
  { value: "route-wh-03-mfg-01", label: "route-wh-03-mfg-01 (Oragadam-Sriperumbudur Feeder Corridor)" },
  { value: "global", label: "global (South Indian Multi-Tier Supply Network)" },
];

const DEFAULT_SCENARIOS: ScenarioItem[] = [
  {
    scenario_id: "scen-01",
    name: "Baseline Nominal Operations",
    disruption_type: "none",
    target_entity: "global",
    description: "Nominal operating baseline across peninsular South Indian corridors with predictable demand and on-time supplier deliveries.",
    severity: 1,
  },
  {
    scenario_id: "scen-02",
    name: "Tier-1 Semiconductor Packaging Delay (SPEL Chennai)",
    disruption_type: "supplier_delay",
    target_entity: "sup-01",
    description: "5-day wafer-level chip scale packaging delay at SPEL Semiconductor (sup-01) Maraimalai Nagar fab triggering inventory and dual-sourcing arbitration.",
    severity: 4,
  },
  {
    scenario_id: "scen-03",
    name: "Automotive Telematics Sensor Demand Surge (Oragadam Hub)",
    disruption_type: "demand_spike",
    target_entity: "wh-03",
    description: "Sudden 45% regional order surge for Automotive Sensor Hubs (prod-102) buffering at Oragadam JIT Warehouse (wh-03).",
    severity: 3,
  },
  {
    scenario_id: "scen-04",
    name: "NH48 Arterial Freight Corridor Monsoon Closure",
    disruption_type: "transport_failure",
    target_entity: "route-wh-01-mfg-01",
    description: "Severe monsoon waterlogging along the NH48 interstate freight lane halting truck transit from Hosur Buffer Warehouse (wh-01) to Sriperumbudur Assembly Hub (mfg-01).",
    severity: 5,
  },
  {
    scenario_id: "scen-05",
    name: "Cochin Port Deep-Water Terminal Cyclonic Stoppage",
    disruption_type: "adverse_weather",
    target_entity: "dc-02",
    description: "Arabian Sea cyclonic disturbance forcing 8-day operational container cranes shutdown at Cochin Vallarpadam International Terminal (dc-02).",
    severity: 4,
  },
  {
    scenario_id: "scen-06",
    name: "Discrete Power Fab Cleanroom Outage (CDIL Bengaluru)",
    disruption_type: "supplier_delay",
    target_entity: "sup-02",
    description: "HVAC failure and particulate contamination in Class 100 cleanroom halting power diode and rectifier wafer fabrication for 6 days.",
    severity: 4,
  },
  {
    scenario_id: "scen-07",
    name: "Automotive Telematics SMT Head Failure (Kaynes Mysuru)",
    disruption_type: "supplier_delay",
    target_entity: "sup-03",
    description: "High-speed pick-and-place placement head breakdown on primary surface-mount line in Koorgalli creating acute 5-day assembly deficit.",
    severity: 3,
  },
  {
    scenario_id: "scen-08",
    name: "Surface-Mount Solder Defect Lot Quarantine (Syrma Bargur)",
    disruption_type: "supplier_delay",
    target_entity: "sup-04",
    description: "Automated X-ray inspection detects BGA solder micro-voiding across 14,000 sub-assembly boards, triggering mandatory quality quarantine.",
    severity: 4,
  },
  {
    scenario_id: "scen-09",
    name: "Aerospace Sub-Module Allocation Rationing (Centum Yelahanka)",
    disruption_type: "supplier_delay",
    target_entity: "sup-05",
    description: "Statutory defense and satellite payload contracts preempt 40% of cleanroom capacity, forcing commercial micro-inverter module rationing.",
    severity: 3,
  },
  {
    scenario_id: "scen-10",
    name: "High-Density PCB Copper Laminate Stockout (Sahasra Hyderabad)",
    disruption_type: "supplier_delay",
    target_entity: "sup-08",
    description: "Global raw material delays for high-frequency copper-clad laminate halting multi-layer PCB pressing at Shamshabad facility.",
    severity: 4,
  },
  {
    scenario_id: "scen-11",
    name: "Smart Energy IoT Meter Mandate Demand Surge",
    disruption_type: "demand_spike",
    target_entity: "wh-01",
    description: "State electricity board smart meter rollout mandates create sudden 80% demand surge for Smart IoT Telematics Gateways.",
    severity: 4,
  },
  {
    scenario_id: "scen-12",
    name: "Commercial Fleet EV Powertrain Retrofit Spike",
    disruption_type: "demand_spike",
    target_entity: "wh-02",
    description: "Commercial logistics operator emergency retrofit of 10,000 delivery vans triggering 120% demand spike for power modules.",
    severity: 5,
  },
  {
    scenario_id: "scen-13",
    name: "Quarter-End Automotive OEM Assembly Ramp-Up",
    disruption_type: "demand_spike",
    target_entity: "wh-03",
    description: "Quarter-end vehicle export push across Chennai automotive assembly plants increasing JIT sensor intake by 35%.",
    severity: 3,
  },
  {
    scenario_id: "scen-14",
    name: "Coastal Municipal Sensor Network Renewal Push",
    disruption_type: "demand_spike",
    target_entity: "dc-01",
    description: "Smart City municipal sensor renewal tenders pull 25,000 environmental telemetry gateways, creating localized buffer stockout hazards.",
    severity: 3,
  },
  {
    scenario_id: "scen-15",
    name: "Attibele Interstate Border Truck Checkpost Strike",
    disruption_type: "transport_failure",
    target_entity: "route-sup-02-wh-01",
    description: "Commercial vehicle operators strike and flash roadblock at Attibele toll plaza on NH44 halting container movements into Hosur.",
    severity: 4,
  },
  {
    scenario_id: "scen-16",
    name: "Palakkad Gap Western Ghats Landslide Corridor Halt",
    disruption_type: "transport_failure",
    target_entity: "route-sup-07-mfg-01",
    description: "Western Ghats monsoon mudslide and boulder collapse on NH544 between Walayar and Palakkad severing Kerala-Tamil Nadu transit.",
    severity: 5,
  },
  {
    scenario_id: "scen-17",
    name: "NH44 Kurnool Bridge Heavy-Axle Weight Embargo",
    disruption_type: "transport_failure",
    target_entity: "route-sup-08-wh-04",
    description: "Emergency bridge pier reinforcement near Kurnool on NH44 restricting multi-axle freight trailers exceeding 16 tonnes.",
    severity: 3,
  },
  {
    scenario_id: "scen-18",
    name: "Chennai Outer Ring Road Heavy Freight Gridlock",
    disruption_type: "transport_failure",
    target_entity: "route-wh-03-mfg-01",
    description: "Hazardous material spill and highway pileup halting JIT component shuttles between Oragadam industrial hub and Sriperumbudur.",
    severity: 3,
  },
  {
    scenario_id: "scen-19",
    name: "Hosur Buffer Automated AS/RS Crane System Fault",
    disruption_type: "transport_failure",
    target_entity: "wh-01",
    description: "High-bay automated storage crane PLC failure and cable derailment locking 45,000 component totes in Hosur Buffer Warehouse.",
    severity: 4,
  },
  {
    scenario_id: "scen-20",
    name: "Sri City FTWZ Regulatory Customs Audit Clearance Hold",
    disruption_type: "supplier_delay",
    target_entity: "wh-04",
    description: "Customs authorities compliance audit placing a 72-hour regulatory hold on duty-free component disbursements at Sri City FTWZ.",
    severity: 4,
  },
  {
    scenario_id: "scen-21",
    name: "Whitefield Inland Container Depot Rail Rake Deficit",
    disruption_type: "transport_failure",
    target_entity: "wh-02",
    description: "Regional shortage of specialized CONCOR container flatbed rail wagons delaying intermodal movements to Chennai Port.",
    severity: 3,
  },
  {
    scenario_id: "scen-22",
    name: "Chennai Port Shallow Channel Silting Berth Congestion",
    disruption_type: "transport_failure",
    target_entity: "dc-01",
    description: "Post-monsoon littoral sediment accumulation reducing channel draft at Chennai Port, delaying container vessel discharge by 4 days.",
    severity: 3,
  },
  {
    scenario_id: "scen-23",
    name: "Shamshabad Aerotropolis Airfreight Cargo Crunch",
    disruption_type: "transport_failure",
    target_entity: "dc-03",
    description: "Scheduled widebody cargo freighter cancellation creating an international airfreight embargo at Hyderabad Airport.",
    severity: 4,
  },
  {
    scenario_id: "scen-24",
    name: "Cyclone Michaung Coromandel Plain Compound Inundation",
    disruption_type: "adverse_weather",
    target_entity: "sup-01",
    description: "Category-4 cyclonic storm simultaneously flooding SPEL Semiconductor in Maraimalai Nagar and halting Chennai Port operations.",
    severity: 5,
  },
  {
    scenario_id: "scen-25",
    name: "Peninsular Grid Blackout Sourcing Crisis",
    disruption_type: "supplier_delay",
    target_entity: "mfg-01",
    description: "Regional electricity transmission grid failure knocking out industrial power across Tamil Nadu and Karnataka, cutting fab throughput to 40%.",
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
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState<string>("");
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

          DEFAULT_SCENARIOS.forEach((def) => {
            if (!merged.some((m: ScenarioItem) => m.scenario_id === def.scenario_id)) {
              merged.push(def);
            }
          });

          setScenarios(merged);

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

  const filteredScenarios = useMemo(() => {
    return scenarios.filter((scen) => {
      if (selectedCategory === "supplier" && scen.disruption_type !== "supplier_delay") return false;
      if (selectedCategory === "demand" && scen.disruption_type !== "demand_spike") return false;
      if (selectedCategory === "transport" && scen.disruption_type !== "transport_failure") return false;
      if (selectedCategory === "weather_systemic" && !["adverse_weather", "none"].includes(scen.disruption_type) && scen.scenario_id !== "scen-25") return false;

      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const matchId = scen.scenario_id.toLowerCase().includes(q);
        const matchName = scen.name.toLowerCase().includes(q);
        const matchTarget = scen.target_entity.toLowerCase().includes(q);
        const matchDesc = scen.description.toLowerCase().includes(q);
        if (!matchId && !matchName && !matchTarget && !matchDesc) return false;
      }
      return true;
    });
  }, [scenarios, selectedCategory, searchQuery]);

  return (
    <div className={styles.container}>
      {/* Left Column: Scenario Catalog */}
      <div className={styles.libraryColumn}>
        <div className={styles.sectionHeader}>
          <span className={styles.sectionTitle}>Scenario Library</span>
          <span style={{ fontSize: "11px", color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>
            {filteredScenarios.length} OF {scenarios.length} SCENARIOS DISPLAYED
          </span>
        </div>

        {/* Toolbar: Category Filters and Search */}
        <div className={styles.toolbar}>
          <div className={styles.filterTabs}>
            <button
              className={`${styles.tabBtn} ${selectedCategory === "all" ? styles.tabBtnActive : ""}`}
              onClick={() => setSelectedCategory("all")}
            >
              All ({scenarios.length})
            </button>
            <button
              className={`${styles.tabBtn} ${selectedCategory === "supplier" ? styles.tabBtnActive : ""}`}
              onClick={() => setSelectedCategory("supplier")}
            >
              Supplier (8)
            </button>
            <button
              className={`${styles.tabBtn} ${selectedCategory === "demand" ? styles.tabBtnActive : ""}`}
              onClick={() => setSelectedCategory("demand")}
            >
              Demand (5)
            </button>
            <button
              className={`${styles.tabBtn} ${selectedCategory === "transport" ? styles.tabBtnActive : ""}`}
              onClick={() => setSelectedCategory("transport")}
            >
              Transport (9)
            </button>
            <button
              className={`${styles.tabBtn} ${selectedCategory === "weather_systemic" ? styles.tabBtnActive : ""}`}
              onClick={() => setSelectedCategory("weather_systemic")}
            >
              Weather & Systemic (3)
            </button>
          </div>
          <input
            type="text"
            className={styles.searchInput}
            placeholder="Search scenarios..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
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
              {filteredScenarios.map((scen) => {
                const isSelected = selectedScenario?.scenario_id === scen.scenario_id;
                const severityClass =
                  scen.severity >= 5
                    ? styles.severityHigh
                    : scen.severity >= 3
                    ? styles.severityMed
                    : styles.severityLow;

                return (
                  <tr
                    key={scen.scenario_id}
                    className={`${styles.scenarioRow} ${isSelected ? styles.scenarioRowSelected : ""}`}
                    onClick={() => handleSelectScenario(scen)}
                  >
                    <td className={styles.scenarioId}>{scen.scenario_id}</td>
                    <td>
                      <div style={{ fontWeight: 600, color: "var(--text-primary)" }}>{scen.name}</div>
                      <div style={{ fontSize: "11px", color: "var(--text-muted)", marginTop: "2px", lineHeight: "1.3" }}>
                        {scen.description}
                      </div>
                    </td>
                    <td>
                      <span className={styles.disruptionTag}>{scen.disruption_type}</span>
                    </td>
                    <td style={{ fontFamily: "var(--font-mono)", fontSize: "12px" }}>
                      {scen.target_entity}
                    </td>
                    <td style={{ fontFamily: "var(--font-mono)" }} className={severityClass}>
                      {scen.severity || 1} / 5
                    </td>
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
