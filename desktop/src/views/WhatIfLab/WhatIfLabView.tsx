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
        "Authorize three-shift assembly expansion at Sriperumbudur, activate secondary SMT lines at Syrma SGS (sup-04), and establish daily rolling buffer shuttles.",
      transport_failure:
        "Activate manual picking crews in low-bay annex, deploy backup forklift fleet, and reassign urgent shipments to Oragadam JIT (wh-03).",
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
        "Escalate to Executive Operations: Propose phased customer allocation plan (50% delivery in 14 days, 50% in 45 days) and authorize emergency capacity expansion.",
      transport_failure:
        "Contract private container truck convoys via Krishnagiri-Vellore highway corridor to bypass CONCOR rail wagon shortage.",
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
        "Activate weekend overtime shifts at Oragadam JIT, draw safety stock from Hosur (wh-01), and prioritize telematics shipments.",
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
        "Submit expedited audit bond to customs commissionerate and draw duty-paid buffer reserves from Oragadam JIT (wh-03) and Hosur (wh-01).",
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
        "Coordinate advance bulk shipments with municipal contractors, release staged buffer gateways from Oragadam (wh-03), and increase production lines.",
      transport_failure:
        "Divert priority container vessels to Kattupalli Port deep-water berths (30km north) and lighterage cargo for shuttle transport to Sriperumbudur.",
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
        "Reroute European export container vessels to Ennore / Chennai Port (dc-01) and charter bonded road transit across Tamil Nadu.",
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
        "Divert urgent IoT telematics air consignments via Bengaluru Kempegowda International Airport bonded airfeeder truck network.",
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
        "Reroute critical truck convoys via Krishnagiri - Tiruvannamalai - Kanchipuram arterial detour and release emergency safety stock at Sriperumbudur.",
      adverse_weather:
        "Deploy heavy tow recovery units along waterlogged NH48 stretches and reroute non-essential cargo to rail freight.",
    },
  },
  "route-sup-02-wh-01": {
    name: "Bengaluru-Hosur NH44 Freight Lane",
    cluster: "NH44 Inter-State Corridor",
    base_risk: 8.4,
    base_lead_time: 1.4,
    base_cost: 9800,
    actions: {
      supplier_delay:
        "Reroute trucks through Anekal-Thally rural bypass to circumvent Attibele toll checkpost congestion.",
      demand_spike:
        "Double freight trailer rotations between Bengaluru Electronic City and Hosur Buffer Warehouse.",
      transport_failure:
        "Reroute trucks via Anekal - Thally rural highway corridor directly into Hosur buffer gates to bypass Attibele toll blockage.",
      adverse_weather:
        "Deploy covered high-cube trucks and hold delicate discrete components at Whitefield ICD (wh-02).",
    },
  },
  "route-sup-07-mfg-01": {
    name: "Kochi-Sriperumbudur Inter-State Corridor",
    cluster: "NH544 / Palakkad Gap Highway",
    base_risk: 9.6,
    base_lead_time: 1.8,
    base_cost: 13200,
    actions: {
      supplier_delay:
        "Divert industrial control assemblies to Southern Railway express freight container from Ernakulam to Chennai.",
      demand_spike:
        "Engage dedicated express logistics provider to run dual-driver night express cargo runs across Tamil Nadu.",
      transport_failure:
        "Commission coastal express container feeder vessel from Cochin Port (dc-02) around peninsular India to Chennai Port (dc-01) and activate substitute wire harness assembly at Syrma (sup-04).",
      adverse_weather:
        "Stage Cochin electronics inventory at Coimbatore inland transshipment depot during Western Ghats monsoon storms.",
    },
  },
  "route-sup-08-wh-04": {
    name: "Hyderabad-Sri City Corridor",
    cluster: "NH44 / NH16 Inter-State Corridor",
    base_risk: 8.7,
    base_lead_time: 1.5,
    base_cost: 10600,
    actions: {
      supplier_delay:
        "Air-freight urgent PCB layers from Shamshabad Airport (dc-03) to Chennai and truck directly to Sri City FTWZ.",
      demand_spike:
        "Charter dedicated multi-axle freight convoys from Hyderabad to Sri City FTWZ to meet volume surge.",
      transport_failure:
        "Split freight across light commercial vehicles (LCVs) below 16 tonnes and divert heavy shipments via Guntur - Ongole - NH16 coastal highway.",
      adverse_weather:
        "Pre-stage PCB materials in climate-sealed containers at Sri City FTWZ before monsoon frontal arrival.",
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
        "Deploy direct-to-line hot shot truck deliveries from SPEL Semiconductor (sup-01) to Sriperumbudur assembly floor.",
      demand_spike:
        "Increase JIT dispatch cycle to hourly milk-run rotations between Oragadam and Sriperumbudur.",
      transport_failure:
        "Reroute JIT parts shuttles via Walajabad - Sunguvarchatram rural arterial road and deploy dedicated green-corridor pilot vehicles.",
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

  const calcRisk = (severity * profile.base_risk * mult.risk).toFixed(1);
  const calcLead = (severity * profile.base_lead_time * mult.lead_time).toFixed(1);
  const calcCost = Math.round(severity * profile.base_cost * mult.cost).toLocaleString("en-IN");
  const recommendation = profile.actions[disruptionType] || profile.actions["supplier_delay"];
  const consensus_status = ["scen-12", "scen-24", "scen-25"].includes(scenarioId) ? "ESCALATED_TO_HUMAN" : "RESOLVED";

  return {
    stockout_risk_delta: `+${calcRisk}%`,
    lead_time_impact: `+${calcLead} days`,
    cost_variance: `+₹${calcCost}`,
    recommendation,
    consensus_status,
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
    consensus_status: string;
  } | null>(null);

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
          stockout_risk_delta: resp.stockout_risk_delta || calculated.stockout_risk_delta,
          lead_time_impact: resp.lead_time_impact || calculated.lead_time_impact,
          cost_variance: resp.cost_variance || calculated.cost_variance,
          recommendation: resp.recommendation || calculated.recommendation,
          consensus_status: resp.consensus_status || calculated.consensus_status,
        });
        setIsRunning(false);
      }, 400);
    } catch {
      setTimeout(() => {
        setResult({
          whatif_id: `wi-sim-${Math.random().toString(36).substring(2, 8)}`,
          ...calculated,
        });
        setIsRunning(false);
      }, 400);
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.sectionHeader}>
        <span className={styles.sectionTitle}>What-If Counterfactual Simulation Lab</span>
        <span style={{ fontSize: "11px", color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>
          MONTE-CARLO PREDICTIVE ENGINE (25 SCENARIOS CONFIGURED)
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
                  {lvl}
                </button>
              ))}
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
                  <span
                    className={styles.deltaValue}
                    style={{
                      color:
                        result.consensus_status === "ESCALATED_TO_HUMAN"
                          ? "var(--accent-red)"
                          : "var(--status-healthy)",
                      fontSize: "17px",
                    }}
                  >
                    {result.consensus_status}
                  </span>
                  <span className={styles.deltaSubtext}>
                    {result.consensus_status === "ESCALATED_TO_HUMAN"
                      ? "Human-in-the-loop escalation"
                      : "CD2F multi-agent agreement"}
                  </span>
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
