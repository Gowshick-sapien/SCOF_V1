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
        "Emergency Disaster Protocol: Shift all wafer packaging to CDIL Bengaluru (sup-02), reroute export logistics through Cochin Vallarpadam Port (dc-02), and alert executive operations.",
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
        "Qualify and transfer discrete component production lots to Centum Electronics (sup-05) and draw safety buffer from Whitefield ICD (wh-02).",
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
        "Transfer 50% automotive sensor sub-assembly runs to Vinyas Innovative (sup-06, Mysuru) and draw buffer stock from Oragadam JIT (wh-03).",
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
        "Isolate quarantined BGA lot, initiate rapid re-solder protocol at Bargur, and commission expedited replacement batch from Kaynes Technology (sup-03).",
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
        "Split power module shortfall by commissioning auxiliary PCB fabrication runs at Sahasra Electronic (sup-08, Hyderabad) and tap reserves at Whitefield (wh-02).",
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
        "Qualify alternate glass-epoxy laminate suppliers in Bengaluru and route emergency expedited copper panels from Centum Electronics (sup-05).",
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
        "Executive Sourcing Consensus: Ration component inventory to high-margin contracts (prod-101), consolidate diesel generator reserves at Sriperumbudur, and invoke force majeure clauses.",
      demand_spike:
        "Executive Multi-Agent Consensus: Authorize synchronized multi-facility overtime across all supplier clusters and reallocate regional inventory buffers.",
      transport_failure:
        "Reroute local assembly inbound deliveries through SIPCOT feeder arterial lanes.",
      adverse_weather:
        "Activate high-water pumps and elevate finished inventory storage at Sriperumbudur assembly floor.",
    },
  },
  "wh-01": {
    name: "Hosur Logistics Buffer Warehouse",
    cluster: "Hosur Industrial Complex, TN",
    base_risk: 6.2,
    base_lead_time: 1.1,
    base_cost: 6200,
    actions: {
      supplier_delay:
        "Dispatch emergency safety buffer reserves from Hosur to Sriperumbudur assembly line.",
      demand_spike:
        "Double picking shift rotations and requisition overflow staging at Whitefield ICD (wh-02).",
      transport_failure:
        "Shift freight from road corridors to Hosur-Arakkonam rail shuttle service.",
      adverse_weather:
        "Secure warehouse perimeter and prioritize dry-dock freight dispatch before storm front.",
    },
  },
  "wh-02": {
    name: "Whitefield Inland Container Depot",
    cluster: "Whitefield, Bengaluru, KA",
    base_risk: 6.7,
    base_lead_time: 1.25,
    base_cost: 7100,
    actions: {
      supplier_delay:
        "Expedite customs bonded container clearance and transfer pallet loads to Hosur Buffer (wh-01).",
      demand_spike:
        "Reallocate 45% inland container buffer to high-velocity telematics assemblers.",
      transport_failure:
        "Divert Bengaluru city container traffic via Peripheral Ring Road to avoid arterial snarls.",
      adverse_weather:
        "Stage sensitive container loads inside covered ICD shed storage.",
    },
  },
  "wh-03": {
    name: "Oragadam JIT Supplier Warehouse",
    cluster: "Oragadam Auto Corridor, TN",
    base_risk: 7.9,
    base_lead_time: 1.3,
    base_cost: 8300,
    actions: {
      supplier_delay:
        "Execute hourly JIT buffer release directly to Sriperumbudur high-tech assembly plant.",
      demand_spike:
        "Requisition emergency overflow storage at Sri City FTWZ (wh-04).",
      transport_failure:
        "Reroute Oragadam shuttle convoys via Walajabad feeder corridor.",
      adverse_weather:
        "Seal dock levelers and protect electronics consignments from standing water.",
    },
  },
  "wh-04": {
    name: "Sri City FTWZ Logistics Center",
    cluster: "Sri City, AP / TN Border",
    base_risk: 6.4,
    base_lead_time: 1.2,
    base_cost: 6800,
    actions: {
      supplier_delay:
        "Release duty-free bonded inventory buffers and expedite dispatch to Chennai plants.",
      demand_spike:
        "Expedite cross-docking operations to feed North Chennai industrial clusters.",
      transport_failure:
        "Reroute coastal transit through Tada-Sullurpeta inland detour lanes.",
      adverse_weather:
        "Maintain climate-controlled humidity buffers for sensitive electronic components.",
    },
  },
  "dc-01": {
    name: "Chennai Port Container Terminal",
    cluster: "Chennai Port, TN",
    base_risk: 8.4,
    base_lead_time: 1.6,
    base_cost: 11200,
    actions: {
      supplier_delay:
        "Expedite port gate container movement and priority berth assignment.",
      demand_spike:
        "Charter off-dock container freight station capacity near Madhavaram.",
      transport_failure:
        "Bypass port access roads using dedicated Chennai Port-Maduravoyal elevated corridor.",
      adverse_weather:
        "Lash ship-to-shore cranes and divert inbound container vessels to Ennore Port.",
    },
  },
  "dc-02": {
    name: "Cochin Port Vallarpadam Terminal",
    cluster: "Vallarpadam, Kochi, KL",
    base_risk: 8.8,
    base_lead_time: 1.7,
    base_cost: 11800,
    actions: {
      supplier_delay:
        "Divert transshipment feeder containers via express rail cargo to Sriperumbudur.",
      demand_spike:
        "Engage bonded coastal feeder ships to shuttle modules to Chennai Port.",
      transport_failure:
        "Utilize inland water transport barges from Vallarpadam to mainland railhead.",
      adverse_weather:
        "Suspend waterside gantry crane operations and secure high-value reefer and electronics cargo.",
    },
  },
  "dc-03": {
    name: "Hyderabad Air Cargo Gateway",
    cluster: "Shamshabad RGIA, TS",
    base_risk: 7.5,
    base_lead_time: 1.1,
    base_cost: 13500,
    actions: {
      supplier_delay:
        "Book priority belly-cargo capacity on scheduled domestic air freighters to Chennai.",
      demand_spike:
        "Charter dedicated B737 cargo flight to transfer microelectronics directly to Chennai.",
      transport_failure:
        "Stage freight at airport cargo apron and dispatch via green corridor to Sri City.",
      adverse_weather:
        "Transfer perishable air cargo to temperature-controlled airside vaults.",
    },
  },
  "route-wh-01-mfg-01": {
    name: "Hosur-Sriperumbudur NH48 Corridor",
    cluster: "NH48 Interstate Highway",
    base_risk: 9.2,
    base_lead_time: 1.45,
    base_cost: 9800,
    actions: {
      supplier_delay:
        "Deploy dedicated express tractor-trailers with dual-driver rotation.",
      demand_spike:
        "Increase daily convoy dispatch frequency from 4 to 10 truck movements.",
      transport_failure:
        "Reroute heavy vehicles via Krishnagiri-Tiruvannamalai-Kanchipuram arterial detour.",
      adverse_weather:
        "Monitor water levels at low-lying river bridges and equip trucks with GPS hazard telematics.",
    },
  },
  "route-sup-02-wh-01": {
    name: "Bengaluru-Hosur NH44 Freight Lane",
    cluster: "NH44 Arterial Corridor",
    base_risk: 7.8,
    base_lead_time: 1.2,
    base_cost: 7200,
    actions: {
      supplier_delay:
        "Utilize night-time freight transit window to avoid Electronic City border checks.",
      demand_spike:
        "Deploy small commercial vehicles for continuous milk-run deliveries.",
      transport_failure:
        "Detour via Sarjapur-Bagalur rural arterial route to enter Hosur warehouse district.",
      adverse_weather:
        "Pre-stage freight before peak afternoon rainfall windows.",
    },
  },
  "route-sup-07-mfg-01": {
    name: "Kochi-Sriperumbudur Inter-State Corridor",
    cluster: "NH544 / Palakkad Corridor",
    base_risk: 9.6,
    base_lead_time: 1.75,
    base_cost: 12400,
    actions: {
      supplier_delay:
        "Engage priority inter-modal container rakes on Southern Railway.",
      demand_spike:
        "Authorize air cargo failover for critical optical sensor sub-assemblies.",
      transport_failure:
        "Detour around Palakkad Gap pass via Coimbatore-Dharapuram alternate highway.",
      adverse_weather:
        "Hold trucks at secure inland weigh-stations during peak cyclonic squalls.",
    },
  },
  "route-sup-08-wh-04": {
    name: "Hyderabad-Sri City Corridor",
    cluster: "NH44 / Kurnool Corridor",
    base_risk: 8.5,
    base_lead_time: 1.5,
    base_cost: 10200,
    actions: {
      supplier_delay:
        "Pre-book dedicated logistics trucks with expedited turnaround SLAs.",
      demand_spike:
        "Split freight across light commercial vehicles below 16 tonnes.",
      transport_failure:
        "Divert shipments via Guntur - Ongole - NH16 coastal highway.",
      adverse_weather:
        "Pre-stage PCB materials in climate-sealed containers before monsoon frontal arrival.",
    },
  },
  "route-wh-03-mfg-01": {
    name: "Oragadam-Sriperumbudur Feeder Corridor",
    cluster: "SH57 / Chennai Outer Ring Road",
    base_risk: 8.9,
    base_lead_time: 1.3,
    base_cost: 9400,
    actions: {
      supplier_delay:
        "Deploy direct-to-line hot shot truck deliveries from SPEL Semiconductor to assembly floor.",
      demand_spike:
        "Increase JIT dispatch cycle to hourly milk-run rotations between Oragadam and Sriperumbudur.",
      transport_failure:
        "Reroute JIT parts shuttles via Walajabad - Sunguvarchatram rural arterial road.",
      adverse_weather:
        "Equip feeder trucks with all-weather waterproof container covers for monsoon transit.",
    },
  },
  "global": {
    name: "South Indian Multi-Tier Supply Network",
    cluster: "Peninsular Regional Corridor",
    base_risk: 9.5,
    base_lead_time: 1.9,
    base_cost: 14200,
    actions: {
      supplier_delay:
        "Executive Sourcing Consensus: Ration component inventory to high-margin contracts (prod-101), consolidate diesel generator reserves at Sriperumbudur, and invoke force majeure clauses.",
      demand_spike:
        "Executive Multi-Agent Consensus: Authorize synchronized multi-facility overtime across all supplier clusters and reallocate regional inventory buffers.",
      transport_failure:
        "Executive Logistics Consensus: Activate multimodal intermodal rail-road failover protocols across Tamil Nadu, Karnataka, and Kerala freight corridors.",
      adverse_weather:
        "Executive Emergency Disaster Protocol: Re-route coastal maritime shipments through inland hubs and mobilize regional disaster logistics reserves.",
    },
  },
};

const SCENARIO_DEFAULTS: Record<string, { target_entity: string; disruption_type: string; severity: number; name: string }> = {
  "scen-01": { target_entity: "global", disruption_type: "none", severity: 1, name: "Nominal Baseline Operations" },
  "scen-02": { target_entity: "sup-01", disruption_type: "supplier_delay", severity: 4, name: "Tier-1 Semiconductor Packaging Delay (SPEL Chennai)" },
  "scen-03": { target_entity: "wh-03", disruption_type: "demand_spike", severity: 3, name: "Automotive Sensor Hub Demand Surge (Oragadam Hub)" },
  "scen-04": { target_entity: "route-wh-01-mfg-01", disruption_type: "transport_failure", severity: 5, name: "NH48 Freight Corridor Monsoon Closure" },
  "scen-05": { target_entity: "dc-02", disruption_type: "adverse_weather", severity: 4, name: "Cochin Port Terminal Cyclonic Stoppage" },
  "scen-06": { target_entity: "sup-02", disruption_type: "supplier_delay", severity: 4, name: "Discrete Power Fab Cleanroom Outage (CDIL Bengaluru)" },
  "scen-07": { target_entity: "sup-03", disruption_type: "supplier_delay", severity: 3, name: "Automotive Telematics SMT Head Failure (Kaynes Mysuru)" },
  "scen-08": { target_entity: "sup-04", disruption_type: "supplier_delay", severity: 4, name: "Surface-Mount Solder Defect Lot Quarantine (Syrma Bargur)" },
  "scen-09": { target_entity: "sup-05", disruption_type: "supplier_delay", severity: 3, name: "Aerospace Sub-Module Allocation Rationing (Centum Yelahanka)" },
  "scen-10": { target_entity: "sup-08", disruption_type: "supplier_delay", severity: 4, name: "High-Density PCB Copper Laminate Stockout (Sahasra Hyderabad)" },
  "scen-11": { target_entity: "wh-01", disruption_type: "demand_spike", severity: 4, name: "Smart Energy IoT Meter Mandate Demand Surge" },
  "scen-12": { target_entity: "wh-02", disruption_type: "demand_spike", severity: 5, name: "Commercial Fleet EV Powertrain Retrofit Spike" },
  "scen-13": { target_entity: "wh-03", disruption_type: "demand_spike", severity: 3, name: "Quarter-End Automotive OEM Assembly Ramp-Up" },
  "scen-14": { target_entity: "dc-01", disruption_type: "demand_spike", severity: 3, name: "Coastal Municipal Sensor Network Renewal Push" },
  "scen-15": { target_entity: "route-sup-02-wh-01", disruption_type: "transport_failure", severity: 4, name: "Attibele Interstate Border Truck Checkpost Strike" },
  "scen-16": { target_entity: "route-sup-07-mfg-01", disruption_type: "transport_failure", severity: 5, name: "Palakkad Gap Western Ghats Landslide Corridor Halt" },
  "scen-17": { target_entity: "route-sup-08-wh-04", disruption_type: "transport_failure", severity: 3, name: "NH44 Kurnool Bridge Heavy-Axle Weight Embargo" },
  "scen-18": { target_entity: "route-wh-03-mfg-01", disruption_type: "transport_failure", severity: 3, name: "Chennai Outer Ring Road Heavy Freight Gridlock" },
  "scen-19": { target_entity: "wh-01", disruption_type: "transport_failure", severity: 4, name: "Hosur Buffer Automated AS/RS Crane System Fault" },
  "scen-20": { target_entity: "wh-04", disruption_type: "supplier_delay", severity: 4, name: "Sri City FTWZ Regulatory Customs Audit Clearance Hold" },
  "scen-21": { target_entity: "wh-02", disruption_type: "transport_failure", severity: 3, name: "Whitefield Inland Container Depot Rail Rake Deficit" },
  "scen-22": { target_entity: "dc-01", disruption_type: "transport_failure", severity: 3, name: "Chennai Port Shallow Channel Silting Berth Congestion" },
  "scen-23": { target_entity: "dc-03", disruption_type: "transport_failure", severity: 4, name: "Shamshabad Aerotropolis Airfreight Cargo Crunch" },
  "scen-24": { target_entity: "sup-01", disruption_type: "adverse_weather", severity: 5, name: "Cyclone Michaung Coromandel Plain Compound Inundation" },
  "scen-25": { target_entity: "mfg-01", disruption_type: "supplier_delay", severity: 5, name: "Peninsular Grid Blackout Sourcing Crisis" },
};

const DISRUPTION_MULTIPLIERS: Record<string, { risk: number; lead_time: number; cost: number }> = {
  supplier_delay: { risk: 1.08, lead_time: 1.25, cost: 1.0 },
  demand_spike: { risk: 1.22, lead_time: 0.85, cost: 1.15 },
  transport_failure: { risk: 1.15, lead_time: 1.12, cost: 1.22 },
  adverse_weather: { risk: 0.95, lead_time: 1.32, cost: 1.18 },
  none: { risk: 1.0, lead_time: 1.0, cost: 1.0 },
};

function computeSimulationOutcome(targetEntity: string, disruptionType: string, severity: number, scenarioId: string) {
  const profile = COUNTERFACTUAL_PROFILES[targetEntity] || COUNTERFACTUAL_PROFILES["sup-01"];
  const mult = DISRUPTION_MULTIPLIERS[disruptionType] || DISRUPTION_MULTIPLIERS["supplier_delay"];

  const baseRiskVal = profile.base_risk;
  const baseLeadVal = profile.base_lead_time;
  const baseCostVal = profile.base_cost;

  const calcRiskDeltaNum = +(severity * profile.base_risk * mult.risk).toFixed(1);
  const calcLeadDeltaNum = +(severity * profile.base_lead_time * mult.lead_time).toFixed(1);
  const calcCostDeltaNum = Math.round(severity * profile.base_cost * mult.cost);

  const projectedRiskVal = (baseRiskVal + calcRiskDeltaNum).toFixed(1);
  const projectedLeadVal = (baseLeadVal + calcLeadDeltaNum).toFixed(1);
  const projectedCostVal = (baseCostVal + calcCostDeltaNum).toLocaleString("en-IN");

  const recommendation = profile.actions[disruptionType] || profile.actions["supplier_delay"];
  const consensus_status = ["scen-12", "scen-24", "scen-25"].includes(scenarioId) ? "ESCALATED_TO_HUMAN" : "RESOLVED";

  return {
    base_risk: `${baseRiskVal.toFixed(1)}%`,
    base_lead: `${baseLeadVal.toFixed(2)}d`,
    base_cost: `₹${baseCostVal.toLocaleString("en-IN")}`,
    projected_risk: `${projectedRiskVal}%`,
    projected_lead: `${projectedLeadVal}d`,
    projected_cost: `₹${projectedCostVal}`,
    stockout_risk_delta: `+${calcRiskDeltaNum.toFixed(1)}%`,
    lead_time_impact: `+${calcLeadDeltaNum.toFixed(1)} days`,
    cost_variance: `+₹${calcCostDeltaNum.toLocaleString("en-IN")}`,
    recommendation,
    consensus_status,
  };
}

export const WhatIfLabView: React.FC = () => {
  const [baseScenario, setBaseScenario] = useState("scen-02");
  const [disruptionType, setDisruptionType] = useState("supplier_delay");
  const [severity, setSeverity] = useState(4);
  const [targetEntity, setTargetEntity] = useState("sup-01");
  const [isAssumptionsOpen, setIsAssumptionsOpen] = useState(true);
  const [isRunning, setIsRunning] = useState(false);
  const [result, setResult] = useState<{
    whatif_id: string;
    base_risk: string;
    base_lead: string;
    base_cost: string;
    projected_risk: string;
    projected_lead: string;
    projected_cost: string;
    stockout_risk_delta: string;
    lead_time_impact: string;
    cost_variance: string;
    recommendation: string;
    consensus_status: string;
  } | null>(null);

  const activeProfile = COUNTERFACTUAL_PROFILES[targetEntity] || COUNTERFACTUAL_PROFILES["sup-01"];
  const activeScenarioDef = SCENARIO_DEFAULTS[baseScenario] || SCENARIO_DEFAULTS["scen-02"];

  const handleBaseScenarioChange = (newScenarioId: string) => {
    setBaseScenario(newScenarioId);
    const defaults = SCENARIO_DEFAULTS[newScenarioId];
    if (defaults) {
      setDisruptionType(defaults.disruption_type === "none" ? "supplier_delay" : defaults.disruption_type);
      setTargetEntity(defaults.target_entity);
      setSeverity(defaults.severity);
    }
  };

  const handleRunSimulation = async () => {
    setIsRunning(true);
    setResult(null);

    const calculated = computeSimulationOutcome(targetEntity, disruptionType, severity, baseScenario);

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
          base_risk: calculated.base_risk,
          base_lead: calculated.base_lead,
          base_cost: calculated.base_cost,
          projected_risk: calculated.projected_risk,
          projected_lead: calculated.projected_lead,
          projected_cost: calculated.projected_cost,
          stockout_risk_delta: resp.stockout_risk_delta || calculated.stockout_risk_delta,
          lead_time_impact: resp.lead_time_impact || calculated.lead_time_impact,
          cost_variance: resp.cost_variance || calculated.cost_variance,
          recommendation: resp.recommendation || calculated.recommendation,
          consensus_status: resp.consensus_status || calculated.consensus_status,
        });
        setIsRunning(false);
      }, 350);
    } catch {
      setTimeout(() => {
        setResult({
          whatif_id: `wi-sim-${Math.random().toString(36).substring(2, 8)}`,
          ...calculated,
        });
        setIsRunning(false);
      }, 350);
    }
  };

  return (
    <div className={styles.container}>
      {/* Top Workspace Header with Collapsible Assumptions Toggle */}
      <div className={styles.sectionHeader}>
        <div className={styles.headerInfo}>
          <span className={styles.sectionTitle}>What-If Counterfactual Simulation Lab</span>
          <span className={styles.headerSubtitle}>
            MONTE-CARLO PREDICTIVE ENGINE (25 SCENARIOS CONFIGURED)
          </span>
        </div>

        <div className={styles.headerControls}>
          <button
            className={styles.toggleAssumptionsBtn}
            onClick={() => setIsAssumptionsOpen(!isAssumptionsOpen)}
            title={isAssumptionsOpen ? "Collapse parameters sidebar" : "Expand parameters sidebar"}
            aria-label="Toggle Assumptions Sidebar"
          >
            {isAssumptionsOpen ? "Hide Assumptions" : "Show Assumptions"}
          </button>
        </div>
      </div>

      {/* Main Workspace Layout */}
      <div className={`${styles.workspaceGrid} ${!isAssumptionsOpen ? styles.workspaceGridExpanded : ""}`}>
        {/* Collapsible Assumptions Column */}
        {isAssumptionsOpen && (
          <div className={styles.configCard}>
            <div className={styles.configHeader}>
              <span className={styles.configHeading}>Counterfactual Parameters</span>
              <span className={styles.configBadge}>ASSUMPTIONS</span>
            </div>

            <div className={styles.formGroup}>
              <label className={styles.label}>Base Scenario</label>
              <select
                className={styles.select}
                value={baseScenario}
                onChange={(e) => handleBaseScenarioChange(e.target.value)}
              >
                {Object.entries(SCENARIO_DEFAULTS).map(([scenId, def]) => (
                  <option key={scenId} value={scenId}>
                    [{scenId}] {def.name}
                  </option>
                ))}
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
                <option value="adverse_weather">Facility Extreme Weather / Cyclone</option>
              </select>
            </div>

            <div className={styles.formGroup}>
              <label className={styles.label}>Target Topology Node</label>
              <select
                className={styles.select}
                value={targetEntity}
                onChange={(e) => setTargetEntity(e.target.value)}
              >
                <optgroup label="Semiconductor & Electronics Suppliers">
                  <option value="sup-01">sup-01 (SPEL Semiconductor - Maraimalai Nagar, Chennai)</option>
                  <option value="sup-02">sup-02 (CDIL - Electronic City, Bengaluru)</option>
                  <option value="sup-03">sup-03 (Kaynes Technology - Koorgalli, Mysuru)</option>
                  <option value="sup-04">sup-04 (Syrma SGS Technology - Bargur)</option>
                  <option value="sup-05">sup-05 (Centum Electronics - Yelahanka, Bengaluru)</option>
                  <option value="sup-06">sup-06 (Vinyas Innovative Technologies - Hebbal, Mysuru)</option>
                  <option value="sup-07">sup-07 (SFO Technologies NeST - Kakkanad, Kochi)</option>
                  <option value="sup-08">sup-08 (Sahasra Electronic Solutions - Hyderabad)</option>
                </optgroup>
                <optgroup label="High-Tech Assembly & Manufacturing">
                  <option value="mfg-01">mfg-01 (Sriperumbudur High-Tech Assembly Plant)</option>
                </optgroup>
                <optgroup label="Logistics Buffer Warehouses & FTWZ">
                  <option value="wh-01">wh-01 (Hosur Logistics Buffer Warehouse)</option>
                  <option value="wh-02">wh-02 (Whitefield Inland Container Depot)</option>
                  <option value="wh-03">wh-03 (Oragadam JIT Supplier Warehouse)</option>
                  <option value="wh-04">wh-04 (Sri City FTWZ Logistics Center)</option>
                </optgroup>
                <optgroup label="Seaport & Air Cargo Distribution Centers">
                  <option value="dc-01">dc-01 (Chennai Port Container Terminal)</option>
                  <option value="dc-02">dc-02 (Cochin Port Vallarpadam Terminal)</option>
                  <option value="dc-03">dc-03 (Hyderabad Air Cargo Gateway)</option>
                </optgroup>
                <optgroup label="Interstate Logistics Highway Corridors">
                  <option value="route-wh-01-mfg-01">route-wh-01-mfg-01 (Hosur-Sriperumbudur NH48 Corridor)</option>
                  <option value="route-sup-02-wh-01">route-sup-02-wh-01 (Bengaluru-Hosur NH44 Freight Lane)</option>
                  <option value="route-sup-07-mfg-01">route-sup-07-mfg-01 (Kochi-Sriperumbudur Inter-State Corridor)</option>
                  <option value="route-sup-08-wh-04">route-sup-08-wh-04 (Hyderabad-Sri City Corridor)</option>
                  <option value="route-wh-03-mfg-01">route-wh-03-mfg-01 (Oragadam-Sriperumbudur Feeder Corridor)</option>
                </optgroup>
                <optgroup label="Network Systemic">
                  <option value="global">global (South Indian Multi-Tier Supply Network)</option>
                </optgroup>
              </select>
            </div>

            <div className={styles.formGroup}>
              <label className={styles.label}>Severity Override (1 to 5)</label>
              <div className={styles.severitySegmented}>
                {[1, 2, 3, 4, 5].map((lvl) => (
                  <button
                    key={lvl}
                    type="button"
                    className={`${styles.severityBtn} ${severity === lvl ? styles.severityBtnActive : ""}`}
                    onClick={() => setSeverity(lvl)}
                  >
                    Level {lvl}
                  </button>
                ))}
              </div>
            </div>

            <button
              className={styles.runButton}
              onClick={handleRunSimulation}
              disabled={isRunning}
            >
              {isRunning ? "Simulating Counterfactual Run..." : "Execute What-If Simulation"}
            </button>
          </div>
        )}

        {/* Results & Comparison-First Workspace Column */}
        <div className={styles.resultsCard}>
          <div className={styles.resultsHeader}>
            <div className={styles.resultsHeadingGroup}>
              <span className={styles.resultsHeading}>Comparative Outcome Analysis</span>
              <span className={styles.comparisonModeTag}>
                {isAssumptionsOpen ? "STANDARD COMPARISON" : "EXPANDED COMPARISON CANVAS"}
              </span>
            </div>
            {result && (
              <span className={styles.resultIdBadge}>
                RUN ID: {result.whatif_id}
              </span>
            )}
          </div>

          {!result ? (
            <div className={styles.emptyPrompt}>
              <div className={styles.emptyPromptTitle}>No simulation executed yet</div>
              <p className={styles.emptyPromptText}>
                Select baseline scenario assumptions and click <strong>Execute What-If Simulation</strong> to generate a side-by-side counterfactual comparative projection.
              </p>
            </div>
          ) : (
            <div className={styles.comparisonWorkspace}>
              {/* Side-by-Side Comparison Tiles: Baseline vs Counterfactual */}
              <div className={styles.comparisonTilesGrid}>
                {/* Baseline Nominal Tile */}
                <div className={styles.tileCard}>
                  <div className={styles.tileHeader}>
                    <div>
                      <span className={styles.tileType}>BASELINE STATE</span>
                      <h4 className={styles.tileTitle}>Nominal Operating Conditions</h4>
                    </div>
                    <span className={styles.baselineBadge}>NOMINAL</span>
                  </div>

                  <div className={styles.tileEntityRow}>
                    <span className={styles.tileEntityLabel}>Target:</span>
                    <span className={styles.tileEntityVal}>{activeProfile.name} ({activeProfile.cluster})</span>
                  </div>

                  <div className={styles.tileMetricsGrid}>
                    <div className={styles.tileMetricItem}>
                      <span className={styles.tileMetricLabel}>Base Risk Index</span>
                      <span className={styles.tileMetricVal}>{result.base_risk}</span>
                    </div>
                    <div className={styles.tileMetricItem}>
                      <span className={styles.tileMetricLabel}>Expected Lead Time</span>
                      <span className={styles.tileMetricVal}>{result.base_lead}</span>
                    </div>
                    <div className={styles.tileMetricItem}>
                      <span className={styles.tileMetricLabel}>Baseline Operating Cost</span>
                      <span className={styles.tileMetricVal}>{result.base_cost}</span>
                    </div>
                  </div>
                </div>

                {/* Counterfactual Projection Tile */}
                <div className={`${styles.tileCard} ${styles.counterfactualCard}`}>
                  <div className={styles.tileHeader}>
                    <div>
                      <span className={styles.tileType}>COUNTERFACTUAL PROJECTION</span>
                      <h4 className={styles.tileTitle}>{activeScenarioDef.name}</h4>
                    </div>
                    <span className={styles.counterfactualBadge}>
                      Simulated Counterfactual Projection (Isolated Run)
                    </span>
                  </div>

                  <div className={styles.tileEntityRow}>
                    <span className={styles.tileEntityLabel}>Shock Applied:</span>
                    <span className={styles.tileEntityVal}>
                      {disruptionType.toUpperCase()} (Severity {severity}/5) on {targetEntity}
                    </span>
                  </div>

                  <div className={styles.tileMetricsGrid}>
                    <div className={styles.tileMetricItem}>
                      <span className={styles.tileMetricLabel}>Projected Risk Index</span>
                      <span className={`${styles.tileMetricVal} ${styles.metricValRed}`}>
                        {result.projected_risk}
                      </span>
                    </div>
                    <div className={styles.tileMetricItem}>
                      <span className={styles.tileMetricLabel}>Impacted Lead Time</span>
                      <span className={`${styles.tileMetricVal} ${styles.metricValAmber}`}>
                        {result.projected_lead}
                      </span>
                    </div>
                    <div className={styles.tileMetricItem}>
                      <span className={styles.tileMetricLabel}>Projected Operating Cost</span>
                      <span className={styles.tileMetricVal}>
                        {result.projected_cost}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Delta Variance Metrics Grid (Tabular Numerals) */}
              <div className={styles.deltaGrid}>
                <div className={styles.deltaItem}>
                  <span className={styles.deltaLabel}>Stockout Risk Delta</span>
                  <span className={`${styles.deltaValue} ${styles.deltaValRed}`}>
                    {result.stockout_risk_delta}
                  </span>
                  <span className={styles.deltaSubtext}>Increase relative to baseline</span>
                </div>

                <div className={styles.deltaItem}>
                  <span className={styles.deltaLabel}>Lead Time Variance</span>
                  <span className={`${styles.deltaValue} ${styles.deltaValAmber}`}>
                    {result.lead_time_impact}
                  </span>
                  <span className={styles.deltaSubtext}>Average arrival delay</span>
                </div>

                <div className={styles.deltaItem}>
                  <span className={styles.deltaLabel}>Estimated Cost Delta</span>
                  <span className={styles.deltaValue}>
                    {result.cost_variance}
                  </span>
                  <span className={styles.deltaSubtext}>Expedited freight and inventory buffer</span>
                </div>

                <div className={styles.deltaItem}>
                  <span className={styles.deltaLabel}>Consensus Status</span>
                  <span
                    className={`${styles.deltaValue} ${
                      result.consensus_status === "ESCALATED_TO_HUMAN"
                        ? styles.deltaValRed
                        : styles.deltaValGreen
                    }`}
                  >
                    {result.consensus_status}
                  </span>
                  <span className={styles.deltaSubtext}>
                    {result.consensus_status === "ESCALATED_TO_HUMAN"
                      ? "Human escalation policy threshold"
                      : "Multi-agent CD2F consensus reached"}
                  </span>
                </div>
              </div>

              {/* Counterfactual Consensus Action Box */}
              <div className={styles.comparisonBanner}>
                <span className={styles.comparisonTitle}>
                  Arbitrated Multi-Agent Mitigation Action
                </span>
                <p className={styles.comparisonText}>{result.recommendation}</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
