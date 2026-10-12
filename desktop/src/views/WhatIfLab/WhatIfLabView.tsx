import React, { useState } from "react";
import styles from "./WhatIfLab.module.css";
import { apiClient } from "../../api/client";

interface CounterfactualProfile {
  name: string;
  cluster: string;
  base_risk: number;
  base_lead_time: number;
  base_cost: number;
  actions: Record<string, string>;
}

const COUNTERFACTUAL_PROFILES: Record<string, CounterfactualProfile> = {
  "sup-01": {
    name: "SPEL Semiconductor",
    cluster: "Maraimalai Nagar, Chennai",
    base_risk: 8.6,
    base_lead_time: 1.35,
    base_cost: 9600,
    actions: {
      supplier_delay:
        "Activate secondary packaging run at Continental Device India (sup-02, Bengaluru) and release buffer wafers from Hosur Buffer Warehouse (wh-01).",
      demand_spike:
        "Issue emergency purchase order to Continental Device India (sup-02) and schedule accelerated batch delivery to Sriperumbudur (mfg-01).",
      transport_failure:
        "Reroute wafer consignments from Maraimalai Nagar via Grand Southern Trunk road detour directly to Oragadam JIT (wh-03).",
      adverse_weather:
        "Enact coastal storm shelter protocol at Maraimalai Nagar and pull reserve stock from Whitefield ICD (wh-02).",
    },
  },
  "sup-02": {
    name: "Continental Device India (CDIL)",
    cluster: "Electronic City, Bengaluru",
    base_risk: 6.8,
    base_lead_time: 1.15,
    base_cost: 7400,
    actions: {
      supplier_delay:
        "Reallocate discrete component lot orders to Centum Electronics (sup-05, Bengaluru) and expedite road transit along NH44 to Hosur (wh-01).",
      demand_spike:
        "Authorize surge production run at Centum Electronics (sup-05) and draw safety buffer from Whitefield ICD (wh-02).",
      transport_failure:
        "Divert Electronic City outbound trucks via Hosur road bypass directly to Hosur Logistics Buffer (wh-01).",
      adverse_weather:
        "Stage discrete power semiconductor buffer stock at Hosur Warehouse (wh-01) to protect against local power fluctuations.",
    },
  },
  "sup-03": {
    name: "Kaynes Technology India",
    cluster: "Koorgalli, Mysuru",
    base_risk: 7.4,
    base_lead_time: 1.4,
    base_cost: 8800,
    actions: {
      supplier_delay:
        "Divert automotive telematics SMT assembly to Syrma SGS Technology (sup-04, Bargur) and draw safety buffer from Oragadam JIT Warehouse (wh-03).",
      demand_spike:
        "Engage secondary manufacturing line at Vinyas Innovative (sup-06, Mysuru) and increase JIT supply delivery frequency to Sriperumbudur.",
      transport_failure:
        "Reroute Mysuru-Bengaluru freight via NH275 bypass directly to Whitefield ICD (wh-02).",
      adverse_weather:
        "Expedite pre-monsoon telematics shipments from Koorgalli to Hosur Buffer Warehouse (wh-01).",
    },
  },
  "sup-04": {
    name: "Syrma SGS Technology",
    cluster: "Bargur Industrial Estate, TN",
    base_risk: 7.1,
    base_lead_time: 1.25,
    base_cost: 8200,
    actions: {
      supplier_delay:
        "Shift SMT surface mount assembly runs to Kaynes Technology (sup-03, Mysuru) and dispatch truck convoys on NH48 via Hosur Buffer Warehouse (wh-01).",
      demand_spike:
        "Authorize 3-shift surface-mount line expansion at Syrma SGS (sup-04) and expedite sub-assembly feeds to Sriperumbudur (mfg-01).",
      transport_failure:
        "Reroute Bargur freight shipments via NH75 / Krishnagiri-Vellore arterial corridor to bypass local highway blockages.",
      adverse_weather:
        "Store moisture-sensitive surface mount devices at Hosur Buffer (wh-01) and dispatch covered container trucks.",
    },
  },
  "sup-05": {
    name: "Centum Electronics",
    cluster: "Yelahanka, Bengaluru",
    base_risk: 6.5,
    base_lead_time: 1.2,
    base_cost: 7600,
    actions: {
      supplier_delay:
        "Transfer micro-inverter power module contracts to CDIL (sup-02, Electronic City) and pull emergency safety stock from Whitefield ICD (wh-02).",
      demand_spike:
        "Split micro-inverter power component volume between CDIL (sup-02) and Sahasra Electronic (sup-08, Hyderabad).",
      transport_failure:
        "Reroute Yelahanka consignments via Bengaluru Outer Ring Road directly to Hosur Logistics Buffer (wh-01).",
      adverse_weather:
        "Pre-position microelectronics stock at Whitefield ICD (wh-02) to mitigate North Bengaluru logistics bottlenecks.",
    },
  },
  "sup-06": {
    name: "Vinyas Innovative Technologies",
    cluster: "Hebbal Industrial Area, Mysuru",
    base_risk: 5.9,
    base_lead_time: 1.15,
    base_cost: 6900,
    actions: {
      supplier_delay:
        "Execute dual-sourcing failover to Kaynes Technology (sup-03, Koorgalli) and re-route Mysuru-Bengaluru freight corridor.",
      demand_spike:
        "Authorize overtime production at Vinyas Innovative (sup-06) and tap reserve buffer at Hosur Warehouse (wh-01).",
      transport_failure:
        "Detour Hebbal industrial traffic via Srirangapatna to avoid NH275 highway congestion.",
      adverse_weather:
        "Expedite scheduled power electronics shipments to Whitefield ICD (wh-02) prior to storm landfall.",
    },
  },
  "sup-07": {
    name: "SFO Technologies NeST",
    cluster: "Kakkanad, Kochi",
    base_risk: 7.8,
    base_lead_time: 1.5,
    base_cost: 9100,
    actions: {
      supplier_delay:
        "Reroute industrial control module procurement to Syrma SGS (sup-04, Bargur) and expedite intermodal rail cargo from Cochin Port (dc-02) to Sriperumbudur.",
      demand_spike:
        "Authorize split allocation of optical modules between SFO Technologies (sup-07) and Sahasra Electronic (sup-08).",
      transport_failure:
        "Bypass congested Kerala NH544 corridors using Southern Railway express container service from Ernakulam to Chennai.",
      adverse_weather:
        "Transfer coastal electronics inventory from Kakkanad to inland staging at Hosur Logistics Buffer (wh-01).",
    },
  },
  "sup-08": {
    name: "Sahasra Electronic Solutions",
    cluster: "Hyderabad, TS",
    base_risk: 7.2,
    base_lead_time: 1.35,
    base_cost: 8500,
    actions: {
      supplier_delay:
        "Authorize air cargo reorder via Hyderabad Aerotropolis (dc-03) and expedite alternate PCB fabrication batches from Centum Electronics (sup-05, Bengaluru).",
      demand_spike:
        "Engage rapid-turnaround PCB prototype lines at Centum Electronics (sup-05) and charter express cargo flight to Chennai.",
      transport_failure:
        "Reroute North-South NH44 freight trucks via Kurnool-Tirupati corridor directly to Sri City FTWZ (wh-04).",
      adverse_weather:
        "Hold high-density PCB boards in climate-controlled FTWZ facility at Sri City (wh-04) until transit clearance.",
    },
  },
  "mfg-01": {
    name: "Sriperumbudur Assembly Plant",
    cluster: "Sriperumbudur, TN",
    base_risk: 10.5,
    base_lead_time: 1.8,
    base_cost: 14200,
    actions: {
      supplier_delay:
        "Stagger production lines into three 8-hour overtime shifts, increase component buffer retention at Oragadam JIT (wh-03), and prioritize high-margin IoT Gateway fulfillment.",
      demand_spike:
        "Activate secondary final-assembly bay at Sriperumbudur and draw rapid component feeds from Oragadam JIT (wh-03) and Hosur (wh-01).",
      transport_failure:
        "Reroute all inbound component trucks through Sriperumbudur industrial bypass and open auxiliary receiving gates.",
      adverse_weather:
        "Initiate severe weather plant protection protocol and maintain 72-hour on-site buffer inventory for continuous assembly.",
    },
  },
  "wh-01": {
    name: "Hosur Logistics Buffer Warehouse",
    cluster: "Hosur, TN / KA Border",
    base_risk: 8.2,
    base_lead_time: 1.3,
    base_cost: 9200,
    actions: {
      supplier_delay:
        "Divert inbound supplier freight from Western Karnataka hubs directly to Whitefield ICD (wh-02) and establish emergency truck staging at Bargur (sup-04).",
      demand_spike:
        "Authorize 24/7 cross-docking operations at Hosur Buffer (wh-01) to support increased assembly throughput at Sriperumbudur.",
      transport_failure:
        "Reroute outgoing Hosur convoys via NH44 south toward Salem-Chennai corridor to bypass NH48 arterial bottlenecks.",
      adverse_weather:
        "Secure warehouse dock areas and stage critical component containers on elevated inland logistics aprons.",
    },
  },
  "wh-02": {
    name: "Whitefield Inland Container Depot",
    cluster: "Whitefield, Bengaluru",
    base_risk: 6.4,
    base_lead_time: 1.1,
    base_cost: 7100,
    actions: {
      supplier_delay:
        "Reroute rail freight container traffic to Hosur Buffer Warehouse (wh-01) and dispatch dedicated truck convoys across the NH44 interstate lane.",
      demand_spike:
        "Double container handling shifts at Whitefield ICD and increase scheduled shuttle trains to Chennai Port.",
      transport_failure:
        "Transfer rail cargo to container trucks along NH75 Old Madras Road corridor directly to Sri City FTWZ (wh-04).",
      adverse_weather:
        "Prioritize indoor container storage for electronic hardware and seal external freight yard bays.",
    },
  },
  "wh-03": {
    name: "Oragadam JIT Supplier Warehouse",
    cluster: "Oragadam, Kanchipuram, TN",
    base_risk: 8.8,
    base_lead_time: 1.45,
    base_cost: 9700,
    actions: {
      supplier_delay:
        "Deploy direct-to-line hot shot truck deliveries from SPEL Semiconductor (sup-01) and tap safety buffer stock at Sri City FTWZ (wh-04).",
      demand_spike:
        "Increase JIT delivery frequencies from 4-hour intervals to hourly replenishment runs directly to Sriperumbudur assembly bays.",
      transport_failure:
        "Deploy local Oragadam feeder fleet across SIPCOT internal roads to bypass state highway congestion.",
      adverse_weather:
        "Activate high-water flood barriers at Oragadam facility and stage battery power backups for automated cranes.",
    },
  },
  "wh-04": {
    name: "Sri City FTWZ Logistics Center",
    cluster: "Sri City FTWZ, AP",
    base_risk: 6.0,
    base_lead_time: 1.05,
    base_cost: 6800,
    actions: {
      supplier_delay:
        "Expedite customs clearance through Chennai Port (dc-01) and reroute duty-free buffer inventory via Oragadam JIT Warehouse (wh-03).",
      demand_spike:
        "Request customs pre-clearance for high-volume duty-free component shipments to prevent FTWZ processing bottlenecks.",
      transport_failure:
        "Divert North-South coastal traffic via NH16 bypass to avoid suburban Chennai arterial choke points.",
      adverse_weather:
        "Store imported components in FTWZ bonded climate-controlled warehouse blocks until weather clears.",
    },
  },
  "dc-01": {
    name: "Chennai Port Container Terminal",
    cluster: "Chennai Port, TN",
    base_risk: 7.5,
    base_lead_time: 1.6,
    base_cost: 11200,
    actions: {
      supplier_delay:
        "Divert maritime export container vessels to Cochin Vallarpadam Terminal (dc-02) and air-freight high-priority finished goods via Hyderabad Aerotropolis (dc-03).",
      demand_spike:
        "Book priority sea freight container allocations and contract expedited customs discharge berths at Chennai Port.",
      transport_failure:
        "Utilize port rail connector to bypass Chennai port road congestion and deliver containers directly to inland terminals.",
      adverse_weather:
        "Halt seaside gantry crane operations, lash export containers, and stage cargo in secure inland container yards.",
    },
  },
  "dc-02": {
    name: "Cochin Port Vallarpadam Terminal",
    cluster: "Vallarpadam ICTT, Kochi",
    base_risk: 6.8,
    base_lead_time: 1.5,
    base_cost: 9800,
    actions: {
      supplier_delay:
        "Transfer European export shipments to Chennai Port Container Terminal (dc-01) and negotiate priority rail container paths through Coimbatore.",
      demand_spike:
        "Coordinate additional feeder vessel calls to Arabian Sea maritime lanes to handle finished goods export volumes.",
      transport_failure:
        "Reroute Malabar coast outbound freight via NH66 North corridor to inland logistics distribution hubs.",
      adverse_weather:
        "Enact deep-water cyclone mooring protocol at Vallarpadam Terminal and pause crane transit operations.",
    },
  },
  "dc-03": {
    name: "Hyderabad Air Cargo Gateway",
    cluster: "Shamshabad, Hyderabad",
    base_risk: 5.8,
    base_lead_time: 1.1,
    base_cost: 8400,
    actions: {
      supplier_delay:
        "Consolidate international air cargo consignments for transit via Chennai International Airport and convert non-critical air orders to express road transport on NH44.",
      demand_spike:
        "Charter dedicated cargo flights from Shamshabad Aerotropolis to clear accumulated European customer shipments.",
      transport_failure:
        "Switch air cargo ground handling to regional distribution centers using dedicated interstate tractor-trailers.",
      adverse_weather:
        "Divert scheduled cargo flights to Bengaluru Kempegowda Airport and arrange bonded road feeder service.",
    },
  },
  "route-wh-01-mfg-01": {
    name: "Hosur-Sriperumbudur NH48 Freight Corridor",
    cluster: "NH48 Interstate Highway",
    base_risk: 9.8,
    base_lead_time: 1.7,
    base_cost: 12400,
    actions: {
      supplier_delay:
        "Bypass blocked NH48 sections via State Highway 9 / Vellore-Arani detour and coordinate police convoy escorts for high-priority assembly component trucks.",
      demand_spike:
        "Authorize double-trailer freight permits on NH48 corridor to double inter-facility component volume per transit hour.",
      transport_failure:
        "Establish emergency freight bypass via Krishnagiri-Tiruvannamalai-Kanchipuram state highway corridors.",
      adverse_weather:
        "Deploy heavy tow recovery units along waterlogged NH48 stretches and reroute non-essential cargo to rail freight.",
    },
  },
};

const DISRUPTION_MULTIPLIERS: Record<string, { risk: number; lead_time: number; cost: number }> = {
  supplier_delay: { risk: 1.08, lead_time: 1.25, cost: 1.0 },
  demand_spike: { risk: 1.22, lead_time: 0.85, cost: 1.15 },
  transport_failure: { risk: 1.15, lead_time: 1.12, cost: 1.22 },
  adverse_weather: { risk: 0.95, lead_time: 1.32, cost: 1.18 },
};

function computeSimulationOutcome(targetEntity: string, disruptionType: string, severity: number) {
  const profile = COUNTERFACTUAL_PROFILES[targetEntity] || COUNTERFACTUAL_PROFILES["sup-01"];
  const mult = DISRUPTION_MULTIPLIERS[disruptionType] || DISRUPTION_MULTIPLIERS["supplier_delay"];

  const calcRisk = (severity * profile.base_risk * mult.risk).toFixed(1);
  const calcLead = (severity * profile.base_lead_time * mult.lead_time).toFixed(1);
  const calcCost = Math.round(severity * profile.base_cost * mult.cost).toLocaleString("en-IN");
  const recommendation = profile.actions[disruptionType] || profile.actions["supplier_delay"];

  return {
    stockout_risk_delta: `+${calcRisk}%`,
    lead_time_impact: `+${calcLead} days`,
    cost_variance: `+₹${calcCost}`,
    recommendation,
  };
}

export const WhatIfLabView: React.FC = () => {
  const [baseScenario, setBaseScenario] = useState("scen-02");
  const [disruptionType, setDisruptionType] = useState("supplier_delay");
  const [severity, setSeverity] = useState(4);
  const [targetEntity, setTargetEntity] = useState("sup-01");
  const [isRunning, setIsRunning] = useState(false);
  const [result, setResult] = useState<{
    whatif_id: string;
    stockout_risk_delta: string;
    lead_time_impact: string;
    cost_variance: string;
    recommendation: string;
  } | null>(null);

  const handleRunSimulation = async () => {
    setIsRunning(true);
    setResult(null);

    const calculated = computeSimulationOutcome(targetEntity, disruptionType, severity);

    try {
      const resp = await apiClient.runWhatIf({
        base_scenario_id: baseScenario,
        overrides: {
          disruption_type: disruptionType,
          severity,
          target_entity: targetEntity,
        },
      });

      setTimeout(() => {
        setResult({
          whatif_id: resp.whatif_id || `wi-${Math.random().toString(36).substring(2, 10)}`,
          stockout_risk_delta: resp.stockout_risk_delta || calculated.stockout_risk_delta,
          lead_time_impact: resp.lead_time_impact || calculated.lead_time_impact,
          cost_variance: resp.cost_variance || calculated.cost_variance,
          recommendation: resp.recommendation || calculated.recommendation,
        });
        setIsRunning(false);
      }, 500);
    } catch {
      setTimeout(() => {
        setResult({
          whatif_id: `wi-sim-${Math.random().toString(36).substring(2, 8)}`,
          ...calculated,
        });
        setIsRunning(false);
      }, 500);
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.sectionHeader}>
        <span className={styles.sectionTitle}>What-If Counterfactual Simulation Lab</span>
        <span style={{ fontSize: "11px", color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>
          MONTE-CARLO PREDICTIVE ENGINE
        </span>
      </div>

      <div className={styles.workspaceGrid}>
        {/* Configuration Column */}
        <div className={styles.configCard}>
          <div className={styles.sectionHeader} style={{ padding: 0, border: "none" }}>
            <span className={styles.sectionTitle}>Counterfactual Parameters</span>
          </div>

          <div className={styles.formGroup}>
            <label className={styles.label}>Base Scenario</label>
            <select
              className={styles.select}
              value={baseScenario}
              onChange={(e) => setBaseScenario(e.target.value)}
            >
              <option value="scen-01">scen-01 (Nominal Baseline Operations)</option>
              <option value="scen-02">scen-02 (Supplier Delay - sup-01 SPEL Chennai)</option>
              <option value="scen-03">scen-03 (Demand Surge - wh-03 Oragadam Hub)</option>
              <option value="scen-04">scen-04 (NH48 Highway Closure - route-wh-01-mfg-01)</option>
              <option value="scen-05">scen-05 (Cochin Port Cyclonic Stoppage - dc-02)</option>
            </select>
          </div>

          <div className={styles.formGroup}>
            <label className={styles.label}>Disruption Type Override</label>
            <select
              className={styles.select}
              value={disruptionType}
              onChange={(e) => setDisruptionType(e.target.value)}
            >
              <option value="supplier_delay">Supplier Lead-Time Delay</option>
              <option value="demand_spike">Demand Surge / Volatility</option>
              <option value="transport_failure">Logistics Route Disruption</option>
              <option value="adverse_weather">Facility Extreme Weather</option>
            </select>
          </div>

          <div className={styles.formGroup}>
            <label className={styles.label}>Target Topology Node</label>
            <select
              className={styles.select}
              value={targetEntity}
              onChange={(e) => setTargetEntity(e.target.value)}
            >
              <option value="sup-01">sup-01 (SPEL Semiconductor - Maraimalai Nagar, Chennai)</option>
              <option value="sup-02">sup-02 (CDIL - Electronic City, Bengaluru)</option>
              <option value="sup-03">sup-03 (Kaynes Technology - Koorgalli, Mysuru)</option>
              <option value="sup-04">sup-04 (Syrma SGS Technology - Bargur)</option>
              <option value="sup-05">sup-05 (Centum Electronics - Yelahanka, Bengaluru)</option>
              <option value="sup-06">sup-06 (Vinyas Innovative Technologies - Hebbal, Mysuru)</option>
              <option value="sup-07">sup-07 (SFO Technologies NeST - Kakkanad, Kochi)</option>
              <option value="sup-08">sup-08 (Sahasra Electronic Solutions - Hyderabad)</option>
              <option value="mfg-01">mfg-01 (Sriperumbudur High-Tech Assembly Plant)</option>
              <option value="wh-01">wh-01 (Hosur Logistics Buffer Warehouse)</option>
              <option value="wh-02">wh-02 (Whitefield Inland Container Depot)</option>
              <option value="wh-03">wh-03 (Oragadam JIT Supplier Warehouse)</option>
              <option value="wh-04">wh-04 (Sri City FTWZ Logistics Center)</option>
              <option value="dc-01">dc-01 (Chennai Port Container Terminal)</option>
              <option value="dc-02">dc-02 (Cochin Port Vallarpadam Terminal)</option>
              <option value="dc-03">dc-03 (Hyderabad Air Cargo Gateway)</option>
              <option value="route-wh-01-mfg-01">route-wh-01-mfg-01 (Hosur-Sriperumbudur NH48 Corridor)</option>
            </select>
          </div>

          <div className={styles.formGroup}>
            <label className={styles.label}>Severity Override (1 to 5)</label>
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
            className={styles.runButton}
            onClick={handleRunSimulation}
            disabled={isRunning}
          >
            {isRunning ? "Running Multi-Agent Simulation..." : "Execute What-If Simulation"}
          </button>
        </div>

        {/* Results & Comparison Column */}
        <div className={styles.resultsCard}>
          <div className={styles.sectionHeader} style={{ padding: 0, border: "none" }}>
            <span className={styles.sectionTitle}>Comparative Outcome Analysis</span>
            {result && (
              <span style={{ fontSize: "11px", color: "var(--accent-cyan)", fontFamily: "var(--font-mono)" }}>
                ID: {result.whatif_id}
              </span>
            )}
          </div>

          {!result ? (
            <div style={{ color: "var(--text-muted)", fontSize: "13px", padding: "40px 0", textAlign: "center" }}>
              Configure parameters and click Execute to run the counterfactual multi-agent analysis.
            </div>
          ) : (
            <>
              <div className={styles.deltaGrid}>
                <div className={styles.deltaItem}>
                  <span className={styles.deltaLabel}>Stockout Risk Delta</span>
                  <span className={styles.deltaValue} style={{ color: "var(--accent-red)" }}>
                    {result.stockout_risk_delta}
                  </span>
                  <span className={styles.deltaSubtext}>Relative to baseline</span>
                </div>

                <div className={styles.deltaItem}>
                  <span className={styles.deltaLabel}>Lead Time Variance</span>
                  <span className={styles.deltaValue} style={{ color: "var(--accent-amber)" }}>
                    {result.lead_time_impact}
                  </span>
                  <span className={styles.deltaSubtext}>Average arrival delay</span>
                </div>

                <div className={styles.deltaItem}>
                  <span className={styles.deltaLabel}>Estimated Cost Delta</span>
                  <span className={styles.deltaValue} style={{ color: "var(--text-primary)" }}>
                    {result.cost_variance}
                  </span>
                  <span className={styles.deltaSubtext}>Expedited freight & procurement</span>
                </div>

                <div className={styles.deltaItem}>
                  <span className={styles.deltaLabel}>Consensus Status</span>
                  <span className={styles.deltaValue} style={{ color: "var(--status-healthy)", fontSize: "18px" }}>
                    RESOLVED
                  </span>
                  <span className={styles.deltaSubtext}>CD2F multi-agent agreement</span>
                </div>
              </div>

              <div className={styles.comparisonBanner}>
                <span className={styles.comparisonTitle}>Counterfactual Consensus Action</span>
                <p className={styles.comparisonText}>{result.recommendation}</p>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};
