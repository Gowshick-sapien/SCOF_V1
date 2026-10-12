from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uuid
import datetime
import json

from ..events.topics import TOPIC_WHATIF_REQUESTED

def get_event_bus(request: Request):
    return request.app.state.event_bus

def get_redis(request: Request):
    return request.app.state.redis_client

router = APIRouter(prefix="/whatif", tags=["whatif"])

class WhatIfRequest(BaseModel):
    scenario_id: Optional[str] = None
    base_scenario_id: Optional[str] = None
    severity_override: Optional[int] = None
    severity: Optional[int] = None
    disruption_type: Optional[str] = None
    target_entity: Optional[str] = None
    overrides: Optional[Dict[str, Any]] = None

SCENARIO_DEFAULTS: Dict[str, Dict[str, Any]] = {
    "scen-01": {"target_entity": "global", "disruption_type": "supplier_delay", "severity": 1},
    "scen-02": {"target_entity": "sup-01", "disruption_type": "supplier_delay", "severity": 4},
    "scen-03": {"target_entity": "wh-03", "disruption_type": "demand_spike", "severity": 3},
    "scen-04": {"target_entity": "route-wh-01-mfg-01", "disruption_type": "transport_failure", "severity": 5},
    "scen-05": {"target_entity": "dc-02", "disruption_type": "adverse_weather", "severity": 4},
    "scen-06": {"target_entity": "sup-02", "disruption_type": "supplier_delay", "severity": 4},
    "scen-07": {"target_entity": "sup-03", "disruption_type": "supplier_delay", "severity": 3},
    "scen-08": {"target_entity": "sup-04", "disruption_type": "supplier_delay", "severity": 4},
    "scen-09": {"target_entity": "sup-05", "disruption_type": "supplier_delay", "severity": 3},
    "scen-10": {"target_entity": "sup-08", "disruption_type": "supplier_delay", "severity": 4},
    "scen-11": {"target_entity": "wh-01", "disruption_type": "demand_spike", "severity": 4},
    "scen-12": {"target_entity": "wh-02", "disruption_type": "demand_spike", "severity": 5},
    "scen-13": {"target_entity": "wh-03", "disruption_type": "demand_spike", "severity": 3},
    "scen-14": {"target_entity": "dc-01", "disruption_type": "demand_spike", "severity": 3},
    "scen-15": {"target_entity": "route-sup-02-wh-01", "disruption_type": "transport_failure", "severity": 4},
    "scen-16": {"target_entity": "route-sup-07-mfg-01", "disruption_type": "transport_failure", "severity": 5},
    "scen-17": {"target_entity": "route-sup-08-wh-04", "disruption_type": "transport_failure", "severity": 3},
    "scen-18": {"target_entity": "route-wh-03-mfg-01", "disruption_type": "transport_failure", "severity": 3},
    "scen-19": {"target_entity": "wh-01", "disruption_type": "transport_failure", "severity": 4},
    "scen-20": {"target_entity": "wh-04", "disruption_type": "supplier_delay", "severity": 4},
    "scen-21": {"target_entity": "wh-02", "disruption_type": "transport_failure", "severity": 3},
    "scen-22": {"target_entity": "dc-01", "disruption_type": "transport_failure", "severity": 3},
    "scen-23": {"target_entity": "dc-03", "disruption_type": "transport_failure", "severity": 4},
    "scen-24": {"target_entity": "sup-01", "disruption_type": "adverse_weather", "severity": 5},
    "scen-25": {"target_entity": "mfg-01", "disruption_type": "supplier_delay", "severity": 5},
}

COUNTERFACTUAL_PROFILES: Dict[str, Dict[str, Any]] = {
    "sup-01": {
        "name": "SPEL Semiconductor",
        "cluster": "Maraimalai Nagar, Chennai",
        "base_risk": 8.6,
        "base_lead_time": 1.35,
        "base_cost": 9600,
        "actions": {
            "supplier_delay": "Activate secondary packaging run at Continental Device India (sup-02, Bengaluru) and release buffer wafers from Hosur Buffer Warehouse (wh-01).",
            "demand_spike": "Issue emergency purchase order to Continental Device India (sup-02) and schedule accelerated batch delivery to Sriperumbudur (mfg-01).",
            "transport_failure": "Reroute wafer consignments from Maraimalai Nagar via Grand Southern Trunk road detour directly to Oragadam JIT (wh-03).",
            "adverse_weather": "Emergency Disaster Protocol: Shift all wafer packaging to CDIL Bengaluru (sup-02), reroute export logistics through Cochin Vallarpadam Port (dc-02), and alert executive operations.",
        },
    },
    "sup-02": {
        "name": "Continental Device India (CDIL)",
        "cluster": "Electronic City, Bengaluru",
        "base_risk": 6.8,
        "base_lead_time": 1.15,
        "base_cost": 7400,
        "actions": {
            "supplier_delay": "Qualify and transfer discrete component production lots to Centum Electronics (sup-05) and draw safety buffer from Whitefield ICD (wh-02).",
            "demand_spike": "Authorize surge production run at Centum Electronics (sup-05) and draw safety buffer from Whitefield ICD (wh-02).",
            "transport_failure": "Divert Electronic City outbound trucks via Hosur road bypass directly to Hosur Logistics Buffer (wh-01).",
            "adverse_weather": "Stage discrete power semiconductor buffer stock at Hosur Warehouse (wh-01) to protect against local power fluctuations.",
        },
    },
    "sup-03": {
        "name": "Kaynes Technology India",
        "cluster": "Koorgalli, Mysuru",
        "base_risk": 7.4,
        "base_lead_time": 1.4,
        "base_cost": 8800,
        "actions": {
            "supplier_delay": "Transfer 50% automotive sensor sub-assembly runs to Vinyas Innovative (sup-06, Mysuru) and draw buffer stock from Oragadam JIT (wh-03).",
            "demand_spike": "Engage secondary manufacturing line at Vinyas Innovative (sup-06, Mysuru) and increase JIT supply delivery frequency to Sriperumbudur.",
            "transport_failure": "Reroute Mysuru-Bengaluru freight via NH275 bypass directly to Whitefield ICD (wh-02).",
            "adverse_weather": "Expedite pre-monsoon telematics shipments from Koorgalli to Hosur Buffer Warehouse (wh-01).",
        },
    },
    "sup-04": {
        "name": "Syrma SGS Technology",
        "cluster": "Bargur Industrial Estate, TN",
        "base_risk": 7.1,
        "base_lead_time": 1.25,
        "base_cost": 8200,
        "actions": {
            "supplier_delay": "Isolate quarantined BGA lot, initiate rapid re-solder protocol at Bargur, and commission expedited replacement batch from Kaynes Technology (sup-03).",
            "demand_spike": "Authorize 3-shift surface-mount line expansion at Syrma SGS (sup-04) and expedite sub-assembly feeds to Sriperumbudur (mfg-01).",
            "transport_failure": "Reroute Bargur freight shipments via NH75 / Krishnagiri-Vellore arterial corridor to bypass local highway blockages.",
            "adverse_weather": "Store moisture-sensitive surface mount devices at Hosur Buffer (wh-01) and dispatch covered container trucks.",
        },
    },
    "sup-05": {
        "name": "Centum Electronics",
        "cluster": "Yelahanka, Bengaluru",
        "base_risk": 6.5,
        "base_lead_time": 1.2,
        "base_cost": 7600,
        "actions": {
            "supplier_delay": "Split power module shortfall by commissioning auxiliary PCB fabrication runs at Sahasra Electronic (sup-08, Hyderabad) and tap reserves at Whitefield (wh-02).",
            "demand_spike": "Split micro-inverter power component volume between CDIL (sup-02) and Sahasra Electronic (sup-08, Hyderabad).",
            "transport_failure": "Reroute Yelahanka consignments via Bengaluru Outer Ring Road directly to Hosur Logistics Buffer (wh-01).",
            "adverse_weather": "Pre-position microelectronics stock at Whitefield ICD (wh-02) to mitigate North Bengaluru logistics bottlenecks.",
        },
    },
    "sup-06": {
        "name": "Vinyas Innovative Technologies",
        "cluster": "Hebbal Industrial Area, Mysuru",
        "base_risk": 5.9,
        "base_lead_time": 1.15,
        "base_cost": 6900,
        "actions": {
            "supplier_delay": "Execute dual-sourcing failover to Kaynes Technology (sup-03, Koorgalli) and re-route Mysuru-Bengaluru freight corridor.",
            "demand_spike": "Authorize overtime production at Vinyas Innovative (sup-06) and tap reserve buffer at Hosur Warehouse (wh-01).",
            "transport_failure": "Detour Hebbal industrial traffic via Srirangapatna to avoid NH275 highway congestion.",
            "adverse_weather": "Expedite scheduled power electronics shipments to Whitefield ICD (wh-02) prior to storm landfall.",
        },
    },
    "sup-07": {
        "name": "SFO Technologies NeST",
        "cluster": "Kakkanad, Kochi",
        "base_risk": 7.8,
        "base_lead_time": 1.5,
        "base_cost": 9100,
        "actions": {
            "supplier_delay": "Reroute industrial control module procurement to Syrma SGS (sup-04, Bargur) and expedite intermodal rail cargo from Cochin Port (dc-02) to Sriperumbudur.",
            "demand_spike": "Authorize split allocation of optical modules between SFO Technologies (sup-07) and Sahasra Electronic (sup-08).",
            "transport_failure": "Bypass congested Kerala NH544 corridors using Southern Railway express container service from Ernakulam to Chennai.",
            "adverse_weather": "Transfer coastal electronics inventory from Kakkanad to inland staging at Hosur Logistics Buffer (wh-01).",
        },
    },
    "sup-08": {
        "name": "Sahasra Electronic Solutions",
        "cluster": "Hyderabad, TS",
        "base_risk": 7.2,
        "base_lead_time": 1.35,
        "base_cost": 8500,
        "actions": {
            "supplier_delay": "Execute inter-facility raw material loan from Centum Electronics (sup-05) via air express cargo to resume multi-layer PCB pressing at Sahasra (sup-08).",
            "demand_spike": "Engage rapid-turnaround PCB prototype lines at Centum Electronics (sup-05) and charter express cargo flight to Chennai.",
            "transport_failure": "Reroute North-South NH44 freight trucks via Kurnool-Tirupati corridor directly to Sri City FTWZ (wh-04).",
            "adverse_weather": "Hold high-density PCB boards in climate-controlled FTWZ facility at Sri City (wh-04) until transit clearance.",
        },
    },
    "mfg-01": {
        "name": "Sriperumbudur Assembly Plant",
        "cluster": "Sriperumbudur, TN",
        "base_risk": 10.5,
        "base_lead_time": 1.8,
        "base_cost": 14200,
        "actions": {
            "supplier_delay": "Executive Sourcing Consensus: Ration component inventory to high-margin contracts (prod-101), consolidate diesel generator reserves at Sriperumbudur, and invoke force majeure clauses.",
            "demand_spike": "Activate secondary final-assembly bay at Sriperumbudur and draw rapid component feeds from Oragadam JIT (wh-03) and Hosur (wh-01).",
            "transport_failure": "Reroute all inbound component trucks through Sriperumbudur industrial bypass and open auxiliary receiving gates.",
            "adverse_weather": "Initiate severe weather plant protection protocol and maintain 72-hour on-site buffer inventory for continuous assembly.",
        },
    },
    "wh-01": {
        "name": "Hosur Logistics Buffer Warehouse",
        "cluster": "Hosur, TN / KA Border",
        "base_risk": 8.2,
        "base_lead_time": 1.3,
        "base_cost": 9200,
        "actions": {
            "supplier_delay": "Divert inbound supplier freight from Western Karnataka hubs directly to Whitefield ICD (wh-02) and establish emergency truck staging at Bargur (sup-04).",
            "demand_spike": "Authorize three-shift assembly expansion at Sriperumbudur, activate secondary SMT lines at Syrma SGS (sup-04), and establish daily rolling buffer shuttles.",
            "transport_failure": "Divert inbound supplier freight directly to Whitefield ICD (wh-02) and authorize manual staging retrieval for high-priority assembly totes at Hosur.",
            "adverse_weather": "Secure warehouse dock areas and stage critical component containers on elevated inland logistics aprons.",
        },
    },
    "wh-02": {
        "name": "Whitefield Inland Container Depot",
        "cluster": "Whitefield, Bengaluru",
        "base_risk": 6.4,
        "base_lead_time": 1.1,
        "base_cost": 7100,
        "actions": {
            "supplier_delay": "Reroute rail freight container traffic to Hosur Buffer Warehouse (wh-01) and dispatch dedicated truck convoys across the NH44 interstate lane.",
            "demand_spike": "Escalate to Executive Operations: Propose phased customer allocation plan (50% delivery in 14 days, 50% in 45 days) and authorize emergency capacity expansion.",
            "transport_failure": "Convert stranded intermodal rail containers to dedicated road freight convoys on NH75 directly to Chennai Port Terminal (dc-01).",
            "adverse_weather": "Prioritize indoor container storage for electronic hardware and seal external freight yard bays.",
        },
    },
    "wh-03": {
        "name": "Oragadam JIT Supplier Warehouse",
        "cluster": "Oragadam, Kanchipuram, TN",
        "base_risk": 8.8,
        "base_lead_time": 1.45,
        "base_cost": 9700,
        "actions": {
            "supplier_delay": "Deploy direct-to-line hot shot truck deliveries from SPEL Semiconductor (sup-01) and tap safety buffer stock at Sri City FTWZ (wh-04).",
            "demand_spike": "Deploy pre-positioned buffer from Sri City FTWZ (wh-04) and establish hourly dedicated micro-replenishment shuttles into Oragadam plant bays.",
            "transport_failure": "Deploy local Oragadam feeder fleet across SIPCOT internal roads to bypass state highway congestion.",
            "adverse_weather": "Activate high-water flood barriers at Oragadam facility and stage battery power backups for automated cranes.",
        },
    },
    "wh-04": {
        "name": "Sri City FTWZ Logistics Center",
        "cluster": "Sri City FTWZ, AP",
        "base_risk": 6.0,
        "base_lead_time": 1.05,
        "base_cost": 6800,
        "actions": {
            "supplier_delay": "Substitute bonded FTWZ components with domestic safety stock from Oragadam JIT (wh-03) and expedite customs pre-audit reconciliation paperwork.",
            "demand_spike": "Request customs pre-clearance for high-volume duty-free component shipments to prevent FTWZ processing bottlenecks.",
            "transport_failure": "Divert North-South coastal traffic via NH16 bypass to avoid suburban Chennai arterial choke points.",
            "adverse_weather": "Store imported components in FTWZ bonded climate-controlled warehouse blocks until weather clears.",
        },
    },
    "dc-01": {
        "name": "Chennai Port Container Terminal",
        "cluster": "Chennai Port, TN",
        "base_risk": 7.5,
        "base_lead_time": 1.6,
        "base_cost": 11200,
        "actions": {
            "supplier_delay": "Divert maritime export container vessels to Cochin Vallarpadam Terminal (dc-02) and air-freight high-priority finished goods via Hyderabad Aerotropolis (dc-03).",
            "demand_spike": "Reallocate 25% non-critical export staging inventory at Chennai Port (dc-01) to domestic municipal deployment and trigger rapid re-order at SPEL (sup-01).",
            "transport_failure": "Divert outbound container convoys from Chennai Port to Kattupalli Port Terminal and hold intermediate buffers at Sri City FTWZ (wh-04).",
            "adverse_weather": "Halt seaside gantry crane operations, lash export containers, and stage cargo in secure inland container yards.",
        },
    },
    "dc-02": {
        "name": "Cochin Port Vallarpadam Terminal",
        "cluster": "Vallarpadam ICTT, Kochi",
        "base_risk": 6.8,
        "base_lead_time": 1.5,
        "base_cost": 9800,
        "actions": {
            "supplier_delay": "Transfer European export shipments to Chennai Port Container Terminal (dc-01) and negotiate priority rail container paths through Coimbatore.",
            "demand_spike": "Coordinate additional feeder vessel calls to Arabian Sea maritime lanes to handle finished goods export volumes.",
            "transport_failure": "Reroute Malabar coast outbound freight via NH66 North corridor to inland logistics distribution hubs.",
            "adverse_weather": "Reroute European export container volume via electrified rail container shuttle from Ernakulam to Chennai Port Terminal (dc-01).",
        },
    },
    "dc-03": {
        "name": "Hyderabad Air Cargo Gateway",
        "cluster": "Shamshabad, Hyderabad",
        "base_risk": 5.8,
        "base_lead_time": 1.1,
        "base_cost": 8400,
        "actions": {
            "supplier_delay": "Consolidate international air cargo consignments for transit via Chennai International Airport and convert non-critical air orders to express road transport on NH44.",
            "demand_spike": "Charter dedicated cargo flights from Shamshabad Aerotropolis to clear accumulated European customer shipments.",
            "transport_failure": "Transfer urgent export consignments via bonded GPS-tracked road feeder trucks along NH44 to Bengaluru Kempegowda Airport for onward cargo flight.",
            "adverse_weather": "Divert scheduled cargo flights to Bengaluru Kempegowda Airport and arrange bonded road feeder service.",
        },
    },
    "route-wh-01-mfg-01": {
        "name": "Hosur-Sriperumbudur NH48 Freight Corridor",
        "cluster": "NH48 Interstate Highway",
        "base_risk": 9.8,
        "base_lead_time": 1.7,
        "base_cost": 12400,
        "actions": {
            "supplier_delay": "Bypass blocked NH48 sections via State Highway 9 / Vellore-Arani detour and coordinate police convoy escorts for high-priority assembly component trucks.",
            "demand_spike": "Authorize double-trailer freight permits on NH48 corridor to double inter-facility component volume per transit hour.",
            "transport_failure": "Detour priority truck convoys via Krishnagiri-Tiruvannamalai-Kanchipuram arterial roads and mobilize emergency coastal container rail from Katpadi.",
            "adverse_weather": "Deploy heavy tow recovery units along waterlogged NH48 stretches and reroute non-essential cargo to rail freight.",
        },
    },
    "route-sup-02-wh-01": {
        "name": "Bengaluru Electronic City - Hosur NH44 Interstate Corridor",
        "cluster": "NH44 Interstate Lane",
        "base_risk": 7.8,
        "base_lead_time": 1.3,
        "base_cost": 9000,
        "actions": {
            "supplier_delay": "Bypass Attibele checkpoint delays via Sarjapur-Bagalur state arterial detour directly into Hosur Buffer (wh-01).",
            "demand_spike": "Authorize multi-shift dedicated shuttle convoys across NH44 to transfer discrete components to Hosur.",
            "transport_failure": "Reroute component transport convoys via Sarjapur-Bagalur arterial detour into Hosur and pre-clear police freight escorts for priority containers.",
            "adverse_weather": "Stage waterproof tarp containers and maintain continuous GPS tracking through low-lying border segments.",
        },
    },
    "route-sup-07-mfg-01": {
        "name": "Kochi-Sriperumbudur Intermodal Freight Corridor",
        "cluster": "NH544 / Southern Railway Corridor",
        "base_risk": 8.9,
        "base_lead_time": 1.6,
        "base_cost": 11100,
        "actions": {
            "supplier_delay": "Switch Kerala freight to Southern Railway express container service from Ernakulam to Katpadi junction.",
            "demand_spike": "Double intermodal rail rake allocations from Cochin Port to Chennai Inland Terminal.",
            "transport_failure": "Commission coastal express container feeder vessel from Cochin Port (dc-02) around peninsular India to Chennai Port (dc-01) and activate substitute wire harness assembly at Syrma (sup-04).",
            "adverse_weather": "Enact Western Ghats monsoon detour via coastal rail avoiding Palakkad mountain pass.",
        },
    },
    "route-sup-08-wh-04": {
        "name": "Hyderabad-Sri City NH44/NH16 Freight Corridor",
        "cluster": "NH44 / NH16 Interstate Corridor",
        "base_risk": 7.4,
        "base_lead_time": 1.4,
        "base_cost": 8900,
        "actions": {
            "supplier_delay": "Expedite express trucking from Hyderabad to Sri City via Guntur-Nellore corridor to bypass inland slowdowns.",
            "demand_spike": "Contract articulated high-cube freight carriers on NH16 to double multi-layer PCB batch throughput.",
            "transport_failure": "Divert freight convoys via Guntur-Nellore NH16 coastal corridor to bypass Kurnool bridge weight restrictions and maintain multi-axle efficiency.",
            "adverse_weather": "Hold electronic board consignments in climate-controlled transit hub at Kurnool until storm clearance.",
        },
    },
    "route-wh-03-mfg-01": {
        "name": "Oragadam-Sriperumbudur Industrial Feeder Corridor",
        "cluster": "SIPCOT Industrial Arterial",
        "base_risk": 8.5,
        "base_lead_time": 1.2,
        "base_cost": 7800,
        "actions": {
            "supplier_delay": "Deploy direct hot-shot utility vans from SPEL Semiconductor (sup-01) to Sriperumbudur line-side receiving bays.",
            "demand_spike": "Increase JIT feeder frequency to 30-minute intervals from Oragadam warehouse.",
            "transport_failure": "Deploy internal SIPCOT service road bypass fleet and initiate direct line-side component hot-shot deliveries from SPEL (sup-01) to back receiving gates.",
            "adverse_weather": "Stage water-sealed freight vehicles and deploy heavy recovery tractors along industrial feeder roads.",
        },
    },
    "global": {
        "name": "Peninsular Multi-Tier Electronics Supply Network",
        "cluster": "South Indian Manufacturing Corridor",
        "base_risk": 9.5,
        "base_lead_time": 1.7,
        "base_cost": 13500,
        "actions": {
            "supplier_delay": "Executive Sourcing Consensus: Ration component inventory to high-margin contracts (prod-101), consolidate diesel generator reserves at Sriperumbudur, and invoke force majeure clauses.",
            "demand_spike": "Activate all certified secondary suppliers across peninsular corridor and authorize 3-shift assembly overtime.",
            "transport_failure": "Activate multi-modal contingency routes across road, rail, and coastal feeder networks.",
            "adverse_weather": "Initiate regional severe weather protection protocols and pre-position emergency buffer inventory.",
        },
    },
}

DISRUPTION_MULTIPLIERS = {
    "supplier_delay": {"risk": 1.08, "lead_time": 1.25, "cost": 1.0},
    "demand_spike": {"risk": 1.22, "lead_time": 0.85, "cost": 1.15},
    "transport_failure": {"risk": 1.15, "lead_time": 1.12, "cost": 1.22},
    "adverse_weather": {"risk": 0.95, "lead_time": 1.32, "cost": 1.18},
}

def format_inr(number: int) -> str:
    s = str(abs(number))
    if len(s) <= 3:
        res = s
    else:
        last3 = s[-3:]
        remaining = s[:-3]
        groups = []
        while len(remaining) > 2:
            groups.insert(0, remaining[-2:])
            remaining = remaining[:-2]
        if remaining:
            groups.insert(0, remaining)
        res = ",".join(groups) + "," + last3
    return res

@router.post("/run")
async def run_whatif(req: WhatIfRequest, request: Request, bus=Depends(get_event_bus), redis_client=Depends(get_redis)):
    whatif_id = f"wi-{uuid.uuid4().hex[:8]}"
    trace_id = getattr(request.state, "trace_id", str(uuid.uuid4()))

    scenario_id = req.base_scenario_id or req.scenario_id or "scen-02"
    scen_default = SCENARIO_DEFAULTS.get(
        scenario_id,
        {"target_entity": "sup-01", "disruption_type": "supplier_delay", "severity": 3}
    )

    overrides = req.overrides or {}
    disruption_type = overrides.get("disruption_type") or req.disruption_type or scen_default["disruption_type"]
    target_entity = overrides.get("target_entity") or req.target_entity or scen_default["target_entity"]
    severity = overrides.get("severity") or req.severity or req.severity_override or scen_default["severity"]

    # Dynamic counterfactual simulation computation
    profile = COUNTERFACTUAL_PROFILES.get(target_entity, COUNTERFACTUAL_PROFILES["sup-01"])
    mult = DISRUPTION_MULTIPLIERS.get(disruption_type, DISRUPTION_MULTIPLIERS["supplier_delay"])

    calc_risk = round(severity * profile["base_risk"] * mult["risk"], 1)
    calc_lead = round(severity * profile["base_lead_time"] * mult["lead_time"], 1)
    calc_cost = int(round(severity * profile["base_cost"] * mult["cost"]))
    action = profile["actions"].get(disruption_type, profile["actions"]["supplier_delay"])

    consensus_status = "ESCALATED_TO_HUMAN" if scenario_id in ["scen-12", "scen-24", "scen-25"] else "RESOLVED"

    result_payload = {
        "whatif_id": whatif_id,
        "trace_id": trace_id,
        "scenario_id": scenario_id,
        "target_entity": target_entity,
        "disruption_type": disruption_type,
        "severity": severity,
        "stockout_risk_delta": f"+{calc_risk}%",
        "lead_time_impact": f"+{calc_lead} days",
        "cost_variance": f"+₹{format_inr(calc_cost)}",
        "recommendation": action,
        "consensus_status": consensus_status,
        "status": "COMPLETED",
    }

    context = {
        "scenario_id": scenario_id,
        "disruption_type": disruption_type,
        "target_entity_id": target_entity,
        "severity": severity,
        "run_id": str(uuid.uuid4()),
    }

    # Store computed result in Redis
    await redis_client.setex(f"whatif:{whatif_id}", 86400, json.dumps(result_payload))

    event_id = f"evt-{uuid.uuid4().hex}"
    envelope = {
        "event_id": event_id,
        "event_type": "whatif.requested",
        "schema_version": "1.0.0",
        "producer": "scof-api",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "correlation": {
            "trace_id": trace_id,
            "scenario_id": scenario_id,
            "profile_version": "1.0.0",
            "request_id": getattr(request.state, "request_id", str(uuid.uuid4())),
        },
        "payload": {
            "scenario_context": context,
            "whatif_id": whatif_id,
            "counterfactual_result": result_payload,
        },
    }

    await redis_client.setex(f"published_events:{event_id}", 604800, json.dumps(envelope))
    await bus.publish(TOPIC_WHATIF_REQUESTED, key=whatif_id, envelope=envelope)

    return result_payload

@router.get("/{whatif_id}/result")
async def get_whatif_result(whatif_id: str, redis_client=Depends(get_redis)):
    data = await redis_client.get(f"whatif:{whatif_id}")
    if not data:
        raise HTTPException(status_code=404, detail="What-If simulation not found")

    try:
        parsed = json.loads(data)
        return parsed
    except Exception:
        return {"whatif_id": whatif_id, "status": data}
