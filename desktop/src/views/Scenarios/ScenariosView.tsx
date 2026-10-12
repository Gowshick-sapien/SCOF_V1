import React, { useEffect, useState, useMemo, useRef } from "react";
import styles from "./Scenarios.module.css";
import { apiClient } from "../../api/client";
import { ContextualDrawer } from "../../components/common/ContextualDrawer";

interface ScenarioItem {
  scenario_id: string;
  name: string;
  disruption_type: string;
  target_entity: string;
  description: string;
  severity: number;
}

interface ScenarioDraft {
  disruption_type: string;
  target_entity: string;
  severity: number;
  isDirty: boolean;
}

type DispatchStatus =
  | "IDLE"
  | "SUBMITTING"
  | "ACCEPTED"
  | "REJECTED"
  | "FAILED"
  | "UNKNOWN";

interface DispatchResult {
  status: DispatchStatus;
  event_id?: string;
  trace_id?: string;
  message?: string;
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

const SEVERITY_DESCRIPTIONS: Record<number, string> = {
  1: "Level 1: Nominal baseline operating conditions",
  2: "Level 2: Minor operational schedule variance",
  3: "Level 3: Moderate tier-1 delivery or demand deviation",
  4: "Level 4: Acute localized disruption requiring CD2F arbitration",
  5: "Level 5: Critical corridor or plant shutdown / severe shock",
};

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
  const [activeScenario, setActiveScenario] = useState<ScenarioItem>(DEFAULT_SCENARIOS[1]);
  const [isDrawerOpen, setIsDrawerOpen] = useState<boolean>(false);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [dispatchResult, setDispatchResult] = useState<DispatchResult | null>(null);

  // In-session memory drafts storage (Scenario ID -> DraftConfig)
  const [scenarioDrafts, setScenarioDrafts] = useState<Record<string, ScenarioDraft>>({});

  const containerRef = useRef<HTMLDivElement>(null);
  const [containerWidth, setContainerWidth] = useState<number>(1200);

  useEffect(() => {
    if (!containerRef.current) return;
    const updateSize = () => {
      if (containerRef.current) {
        setContainerWidth(containerRef.current.clientWidth);
      }
    };
    updateSize();

    const ro = new ResizeObserver((entries) => {
      for (const entry of entries) {
        setContainerWidth(entry.contentRect.width);
      }
    });
    ro.observe(containerRef.current);
    return () => ro.disconnect();
  }, []);

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
        }
      })
      .catch(() => {
        // Fall back to defaults
      });

    return () => {
      mounted = false;
    };
  }, []);

  const drawerMode: "docked" | "overlay" = containerWidth >= 1200 ? "docked" : "overlay";

  // Active configuration values (derived from session drafts or scenario baseline)
  const currentDraft = scenarioDrafts[activeScenario.scenario_id] || {
    disruption_type: activeScenario.disruption_type,
    target_entity: activeScenario.target_entity,
    severity: activeScenario.severity,
    isDirty: false,
  };

  const handleSelectScenario = (scen: ScenarioItem) => {
    setActiveScenario(scen);
    setIsDrawerOpen(true);
    setDispatchResult(null);
  };

  const updateDraft = (updates: Partial<ScenarioDraft>) => {
    setScenarioDrafts((prev) => ({
      ...prev,
      [activeScenario.scenario_id]: {
        ...currentDraft,
        ...updates,
        isDirty: true,
      },
    }));
  };

  const handleDiscardDraft = () => {
    setScenarioDrafts((prev) => {
      const next = { ...prev };
      delete next[activeScenario.scenario_id];
      return next;
    });
  };

  // Explicit 4-Outcome Dispatch Handler
  const handleTrigger = async () => {
    if (!activeScenario || isSubmitting) return;
    setIsSubmitting(true);
    setDispatchResult({ status: "SUBMITTING" });

    // 10-second client timeout promise to detect UNKNOWN outcome
    const timeoutPromise = new Promise<{ isTimeout: true }>((resolve) =>
      setTimeout(() => resolve({ isTimeout: true }), 10000)
    );

    try {
      const triggerPromise = apiClient.triggerScenario(activeScenario.scenario_id, {
        disruption_type: currentDraft.disruption_type,
        target_entity_id: currentDraft.target_entity,
        severity: currentDraft.severity,
      });

      const res = await Promise.race([triggerPromise, timeoutPromise]);

      if ("isTimeout" in res) {
        // 4. UNKNOWN Outcome
        setDispatchResult({
          status: "UNKNOWN",
          message:
            "Request timed out (>10s) without server confirmation. The disruption may have reached the backend API or event bus. Blind duplicate retry is blocked to prevent duplicate simulation shocks.",
        });
        return;
      }

      // 1. ACCEPTED Outcome
      setDispatchResult({
        status: "ACCEPTED",
        event_id: res.event_id,
        trace_id: res.trace_id,
        message:
          "Disruption accepted by API Gateway. Awaiting multi-agent deliberation on Kafka bus.",
      });
    } catch (err: any) {
      const statusCode = err.status || 0;
      if (statusCode >= 400 && statusCode < 500) {
        // 2. REJECTED Outcome
        setDispatchResult({
          status: "REJECTED",
          message:
            err.message ||
            "Scenario parameters rejected by API Gateway validation.",
        });
      } else {
        // 3. FAILED Outcome
        setDispatchResult({
          status: "FAILED",
          message:
            err.message ||
            "Server-side failure prior to event bus publication. Safe to retry.",
        });
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const supplierCount = useMemo(
    () => scenarios.filter((s) => s.disruption_type === "supplier_delay").length,
    [scenarios]
  );
  const demandCount = useMemo(
    () => scenarios.filter((s) => s.disruption_type === "demand_spike").length,
    [scenarios]
  );
  const transportCount = useMemo(
    () => scenarios.filter((s) => s.disruption_type === "transport_failure").length,
    [scenarios]
  );
  const weatherCount = useMemo(
    () =>
      scenarios.filter(
        (s) =>
          ["adverse_weather", "none"].includes(s.disruption_type) ||
          s.scenario_id === "scen-25"
      ).length,
    [scenarios]
  );

  const filteredScenarios = useMemo(() => {
    return scenarios.filter((scen) => {
      if (selectedCategory === "supplier" && scen.disruption_type !== "supplier_delay") return false;
      if (selectedCategory === "demand" && scen.disruption_type !== "demand_spike") return false;
      if (selectedCategory === "transport" && scen.disruption_type !== "transport_failure") return false;
      if (
        selectedCategory === "weather_systemic" &&
        !["adverse_weather", "none"].includes(scen.disruption_type) &&
        scen.scenario_id !== "scen-25"
      )
        return false;

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

  const renderConfigurationDrawer = () => (
    <div className={styles.drawerFormContent}>
      <div className={styles.drawerHeaderInfo}>
        <span className={styles.drawerScenarioTitle}>{activeScenario.name}</span>
        <span className={styles.drawerScenarioDesc}>{activeScenario.description}</span>
      </div>

      {/* Disruption Type Selector */}
      <div className={styles.formGroup}>
        <label className={styles.label}>Disruption Type</label>
        <select
          className={styles.select}
          value={currentDraft.disruption_type}
          onChange={(e) => updateDraft({ disruption_type: e.target.value })}
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
        <label className={styles.label}>Target Node / Corridor</label>
        <select
          className={styles.select}
          value={currentDraft.target_entity}
          onChange={(e) => updateDraft({ target_entity: e.target.value })}
        >
          {TARGET_ENTITY_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>

      {/* 5-Level Segmented Severity Stepper */}
      <div className={styles.formGroup}>
        <label className={styles.label}>Shock Severity Level</label>
        <div className={styles.severitySegmented}>
          {[1, 2, 3, 4, 5].map((lvl) => (
            <button
              key={lvl}
              type="button"
              className={`${styles.severityBtn} ${currentDraft.severity === lvl ? styles.severityBtnActive : ""}`}
              onClick={() => updateDraft({ severity: lvl })}
            >
              Level {lvl}
            </button>
          ))}
        </div>
        <div className={styles.severityDescription}>
          {SEVERITY_DESCRIPTIONS[currentDraft.severity]}
        </div>
      </div>

      {/* Pre-Flight Review Summary Card */}
      <div className={styles.summaryCard}>
        <span className={styles.summaryCardHeading}>Pre-Flight Dispatch Summary</span>
        <div className={styles.summaryRow}>
          <span className={styles.summaryLabel}>Scenario ID</span>
          <span className={styles.summaryValue}>{activeScenario.scenario_id}</span>
        </div>
        <div className={styles.summaryRow}>
          <span className={styles.summaryLabel}>Target Entity</span>
          <span className={styles.summaryValue}>{currentDraft.target_entity}</span>
        </div>
        <div className={styles.summaryRow}>
          <span className={styles.summaryLabel}>Shock Intensity</span>
          <span className={styles.summaryValue}>Level {currentDraft.severity} / 5</span>
        </div>
        <div className={styles.summaryRow}>
          <span className={styles.summaryLabel}>Event Routing Bus</span>
          <span className={styles.summaryValue}>Kafka :9092 (disruptions.triggered)</span>
        </div>
      </div>

      {/* Dispatch Trigger Button with In-Flight Debounce Lock */}
      <button
        className={styles.triggerButton}
        onClick={handleTrigger}
        disabled={isSubmitting || dispatchResult?.status === "UNKNOWN"}
        title={
          dispatchResult?.status === "UNKNOWN"
            ? "Duplicate submission blocked pending status reconciliation"
            : "Dispatch Disruption to Kafka Bus"
        }
      >
        {isSubmitting
          ? "Publishing Disruption to Kafka Bus..."
          : dispatchResult?.status === "UNKNOWN"
          ? "Duplicate Trigger Locked"
          : `Trigger Disruption: [${activeScenario.scenario_id.toUpperCase()}]`}
      </button>

      {/* 4-Outcome Dispatch Result Representation */}
      {dispatchResult && (
        <div className={`${styles.statusCard} ${
          dispatchResult.status === "ACCEPTED"
            ? styles.statusCardSuccess
            : dispatchResult.status === "REJECTED"
            ? styles.statusCardRejected
            : dispatchResult.status === "UNKNOWN"
            ? styles.statusCardUnknown
            : styles.statusCardFailed
        }`}>
          <div className={styles.statusCardHeader}>
            <span className={styles.statusTitle}>
              {dispatchResult.status === "ACCEPTED" && "DISPATCH ACCEPTED (Awaiting Deliberation)"}
              {dispatchResult.status === "REJECTED" && "DISPATCH REJECTED (Validation Error)"}
              {dispatchResult.status === "FAILED" && "DISPATCH FAILED (Server Error)"}
              {dispatchResult.status === "UNKNOWN" && "STATUS UNKNOWN (DISPATCH IN TRANSIT)"}
            </span>
          </div>

          {dispatchResult.event_id && (
            <div className={styles.resultRow}>
              <span className={styles.resultLabel}>Event ID:</span>
              <span className={styles.resultVal}>{dispatchResult.event_id}</span>
            </div>
          )}
          {dispatchResult.trace_id && (
            <div className={styles.resultRow}>
              <span className={styles.resultLabel}>Trace ID:</span>
              <span className={styles.resultVal}>{dispatchResult.trace_id}</span>
            </div>
          )}
          {dispatchResult.message && (
            <div className={styles.resultMessage}>{dispatchResult.message}</div>
          )}

          {/* Reconciliation Path on UNKNOWN Outcome */}
          {dispatchResult.status === "UNKNOWN" && (
            <div className={styles.reconciliationBox}>
              <span className={styles.reconciliationHeading}>Reconciliation Workflow:</span>
              <p className={styles.reconciliationText}>
                Because the dispatch status cannot be established, do not re-trigger this scenario immediately. Verify whether the coordinator initiated consensus:
              </p>
              <div className={styles.reconciliationActions}>
                <button
                  className={styles.reconcileBtn}
                  onClick={() => {
                    // Reset status to allow manual retry after inspection
                    setDispatchResult(null);
                  }}
                >
                  Clear Lock & Re-verify
                </button>
              </div>
            </div>
          )}

          {/* Retry Option on Confirmed FAILED Outcome */}
          {dispatchResult.status === "FAILED" && (
            <div className={styles.retryActionRow}>
              <button
                className={styles.retryBtn}
                onClick={handleTrigger}
                disabled={isSubmitting}
              >
                Retry Dispatch
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );

  return (
    <div className={styles.workspaceWrapper} ref={containerRef}>
      <div className={styles.workspaceMain}>
        {/* Scenario Catalog Header */}
        <div className={styles.sectionHeader}>
          <span className={styles.sectionTitle}>Scenario Catalog & Disruption Lab</span>
          <span className={styles.scenarioCounter}>
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
              Supplier ({supplierCount})
            </button>
            <button
              className={`${styles.tabBtn} ${selectedCategory === "demand" ? styles.tabBtnActive : ""}`}
              onClick={() => setSelectedCategory("demand")}
            >
              Demand ({demandCount})
            </button>
            <button
              className={`${styles.tabBtn} ${selectedCategory === "transport" ? styles.tabBtnActive : ""}`}
              onClick={() => setSelectedCategory("transport")}
            >
              Transport ({transportCount})
            </button>
            <button
              className={`${styles.tabBtn} ${selectedCategory === "weather_systemic" ? styles.tabBtnActive : ""}`}
              onClick={() => setSelectedCategory("weather_systemic")}
            >
              Weather & Systemic ({weatherCount})
            </button>
          </div>
          <input
            type="text"
            className={styles.searchInput}
            placeholder="Search scenarios by ID, name, facility, or description..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        {/* Full-Width Scenario Table */}
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
                const isSelected = activeScenario?.scenario_id === scen.scenario_id && isDrawerOpen;
                const hasDraft = scenarioDrafts[scen.scenario_id]?.isDirty;
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
                    <td className={styles.scenarioId}>
                      <span>{scen.scenario_id}</span>
                      {hasDraft && <span className={styles.draftBadge}>DRAFT</span>}
                    </td>
                    <td>
                      <div className={styles.scenarioName}>{scen.name}</div>
                      <div className={styles.scenarioDesc}>{scen.description}</div>
                    </td>
                    <td>
                      <span className={styles.disruptionTag}>{scen.disruption_type}</span>
                    </td>
                    <td className={styles.targetNode}>{scen.target_entity}</td>
                    <td className={`${styles.severityCell} ${severityClass}`}>
                      Level {scen.severity || 1} / 5
                    </td>
                    <td style={{ textAlign: "right" }}>
                      <button
                        className={isSelected ? styles.activeBtn : styles.selectBtn}
                        onClick={(e) => {
                          e.stopPropagation();
                          handleSelectScenario(scen);
                        }}
                      >
                        {isSelected ? "CONFIGURING" : "Configure & Trigger"}
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Stage 2: Slide-Over Configuration Drawer (Docked Mode when wide) */}
      {drawerMode === "docked" && (
        <ContextualDrawer
          isOpen={isDrawerOpen}
          title={`Configure: [${activeScenario.scenario_id.toUpperCase()}]`}
          badge={currentDraft.disruption_type}
          mode="docked"
          isDirty={currentDraft.isDirty}
          onClose={() => setIsDrawerOpen(false)}
          onDiscard={handleDiscardDraft}
        >
          {renderConfigurationDrawer()}
        </ContextualDrawer>
      )}

      {/* Stage 2: Slide-Over Configuration Drawer (Overlay Mode when compact) */}
      {drawerMode === "overlay" && (
        <ContextualDrawer
          isOpen={isDrawerOpen}
          title={`Configure: [${activeScenario.scenario_id.toUpperCase()}]`}
          badge={currentDraft.disruption_type}
          mode="overlay"
          isDirty={currentDraft.isDirty}
          onClose={() => setIsDrawerOpen(false)}
          onDiscard={handleDiscardDraft}
        >
          {renderConfigurationDrawer()}
        </ContextualDrawer>
      )}
    </div>
  );
};
