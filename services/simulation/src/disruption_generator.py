"""Disruption Event & Scenario Generator for SCOF.

Reads disruption definitions from DomainProfile to instantiate scenario metadata
and parameterized disruption events bound to run_id.
"""

from datetime import date, timedelta
from typing import Dict, List, Any
import numpy as np
from scof_shared.profile.loader import DomainProfile
from .constants import Prefix, DisruptionStatus


class DisruptionGenerator:
    """Generates scenario definitions and synthetic disruption events."""

    def __init__(
        self,
        run_id: str,
        profile: DomainProfile,
        master_entities: Dict[str, List[Dict[str, Any]]],
        random_seed: int = 42,
    ):
        self.run_id = run_id
        self.profile = profile
        self.master_entities = master_entities
        self.random_seed = random_seed

    def generate_all(self, start_date: date, history_days: int) -> Dict[str, List[Dict[str, Any]]]:
        """Generates baseline and stress test scenarios along with disruption events."""
        np.random.seed(self.random_seed)

        scenarios = [
            # Domain 1: Baseline & Core Proofs
            {
                "scenario_id": f"{Prefix.SCENARIO}01",
                "run_id": self.run_id,
                "name": "Baseline Nominal Operations",
                "description": "Nominal operating baseline across peninsular South Indian corridors with predictable demand and on-time supplier deliveries.",
                "random_seed": self.random_seed,
            },
            {
                "scenario_id": f"{Prefix.SCENARIO}02",
                "run_id": self.run_id,
                "name": "Tier-1 Semiconductor Packaging Delay (SPEL Chennai)",
                "description": "5-day wafer-level chip scale packaging delay at SPEL Semiconductor (sup-01) Maraimalai Nagar fab triggering inventory and dual-sourcing arbitration.",
                "random_seed": self.random_seed + 100,
            },
            {
                "scenario_id": f"{Prefix.SCENARIO}03",
                "run_id": self.run_id,
                "name": "Automotive Sensor Demand Surge (Oragadam Hub)",
                "description": "Sudden 45% regional order surge for Automotive Sensor Hubs (prod-102) buffering at Oragadam JIT Warehouse (wh-03).",
                "random_seed": self.random_seed + 200,
            },
            {
                "scenario_id": f"{Prefix.SCENARIO}04",
                "run_id": self.run_id,
                "name": "NH48 Arterial Freight Corridor Monsoon Inundation",
                "description": "Severe monsoon waterlogging along the NH48 interstate freight lane halting truck transit from Hosur Buffer Warehouse (wh-01) to Sriperumbudur Assembly Hub (mfg-01).",
                "random_seed": self.random_seed + 300,
            },
            {
                "scenario_id": f"{Prefix.SCENARIO}05",
                "run_id": self.run_id,
                "name": "Cochin Port Vallarpadam Terminal Cyclonic Stoppage",
                "description": "Arabian Sea cyclonic disturbance forcing 8-day operational container cranes shutdown at Cochin Vallarpadam International Terminal (dc-02).",
                "random_seed": self.random_seed + 400,
            },

            # Domain 2: Upstream Semiconductor & Component Supplier Shortages
            {
                "scenario_id": f"{Prefix.SCENARIO}06",
                "run_id": self.run_id,
                "name": "Discrete Power Fab Cleanroom Outage (CDIL Bengaluru)",
                "description": "Industrial cleanroom HVAC filtration failure at CDIL Electronic City fab halting discrete power diode and transistor fabrication.",
                "random_seed": self.random_seed + 500,
            },
            {
                "scenario_id": f"{Prefix.SCENARIO}07",
                "run_id": self.run_id,
                "name": "Automotive Telematics SMT Head Failure (Kaynes Mysuru)",
                "description": "High-speed pick-and-place placement head breakdown on primary surface-mount line in Koorgalli creating acute 5-day assembly deficit.",
                "random_seed": self.random_seed + 600,
            },
            {
                "scenario_id": f"{Prefix.SCENARIO}08",
                "run_id": self.run_id,
                "name": "Surface-Mount Solder Defect Lot Quarantine (Syrma Bargur)",
                "description": "Automated X-ray inspection detects BGA solder micro-voiding across 14,000 sub-assembly boards, triggering mandatory quality quarantine.",
                "random_seed": self.random_seed + 700,
            },
            {
                "scenario_id": f"{Prefix.SCENARIO}09",
                "run_id": self.run_id,
                "name": "Aerospace Sub-Module Allocation Rationing (Centum Yelahanka)",
                "description": "Statutory defense and satellite payload contracts preempt 40% of cleanroom capacity, forcing commercial micro-inverter module rationing.",
                "random_seed": self.random_seed + 800,
            },
            {
                "scenario_id": f"{Prefix.SCENARIO}10",
                "run_id": self.run_id,
                "name": "High-Density PCB Copper Laminate Stockout (Sahasra Hyderabad)",
                "description": "Global raw material delays for high-frequency copper-clad laminate halting multi-layer PCB pressing at Shamshabad facility.",
                "random_seed": self.random_seed + 900,
            },

            # Domain 3: Downstream Market Volatility & Demand Shocks
            {
                "scenario_id": f"{Prefix.SCENARIO}11",
                "run_id": self.run_id,
                "name": "Smart Energy IoT Meter Mandate Demand Surge",
                "description": "State electricity board smart meter rollout mandates create sudden 80% demand surge for Smart IoT Telematics Gateways.",
                "random_seed": self.random_seed + 1000,
            },
            {
                "scenario_id": f"{Prefix.SCENARIO}12",
                "run_id": self.run_id,
                "name": "Commercial Fleet EV Powertrain Retrofit Spike",
                "description": "Commercial logistics operator emergency retrofit of 10,000 delivery vans triggering 120% demand spike for power modules.",
                "random_seed": self.random_seed + 1100,
            },
            {
                "scenario_id": f"{Prefix.SCENARIO}13",
                "run_id": self.run_id,
                "name": "Quarter-End Automotive OEM Assembly Ramp-Up",
                "description": "Quarter-end vehicle export push across Chennai automotive assembly plants increasing JIT sensor intake by 35%.",
                "random_seed": self.random_seed + 1200,
            },
            {
                "scenario_id": f"{Prefix.SCENARIO}14",
                "run_id": self.run_id,
                "name": "Coastal Municipal Sensor Network Renewal Push",
                "description": "Smart City municipal sensor renewal tenders pull 25,000 environmental telemetry gateways, creating localized buffer stockout hazards.",
                "random_seed": self.random_seed + 1300,
            },

            # Domain 4: Highway, Freight Corridor & Transport Disruptions
            {
                "scenario_id": f"{Prefix.SCENARIO}15",
                "run_id": self.run_id,
                "name": "Attibele Interstate Border Truck Checkpost Strike",
                "description": "Commercial vehicle operators strike and flash roadblock at Attibele toll plaza on NH44 halting container movements into Hosur.",
                "random_seed": self.random_seed + 1400,
            },
            {
                "scenario_id": f"{Prefix.SCENARIO}16",
                "run_id": self.run_id,
                "name": "Palakkad Gap Western Ghats Landslide Corridor Halt",
                "description": "Western Ghats monsoon mudslide and boulder collapse on NH544 between Walayar and Palakkad severing Kerala-Tamil Nadu transit.",
                "random_seed": self.random_seed + 1500,
            },
            {
                "scenario_id": f"{Prefix.SCENARIO}17",
                "run_id": self.run_id,
                "name": "NH44 Kurnool Bridge Heavy-Axle Weight Embargo",
                "description": "Emergency bridge pier reinforcement near Kurnool on NH44 restricting multi-axle freight trailers exceeding 16 tonnes.",
                "random_seed": self.random_seed + 1600,
            },
            {
                "scenario_id": f"{Prefix.SCENARIO}18",
                "run_id": self.run_id,
                "name": "Chennai Outer Ring Road Heavy Freight Gridlock",
                "description": "Hazardous material spill and highway pileup halting JIT component shuttles between Oragadam industrial hub and Sriperumbudur.",
                "random_seed": self.random_seed + 1700,
            },

            # Domain 5: Warehouse & FTWZ Facility Logistics Shocks
            {
                "scenario_id": f"{Prefix.SCENARIO}19",
                "run_id": self.run_id,
                "name": "Hosur Buffer Automated AS/RS Crane System Fault",
                "description": "High-bay automated storage crane PLC failure and cable derailment locking 45,000 component totes in Hosur Buffer Warehouse.",
                "random_seed": self.random_seed + 1800,
            },
            {
                "scenario_id": f"{Prefix.SCENARIO}20",
                "run_id": self.run_id,
                "name": "Sri City FTWZ Regulatory Customs Audit Clearance Hold",
                "description": "Customs authorities compliance audit placing a 72-hour regulatory hold on duty-free component disbursements at Sri City FTWZ.",
                "random_seed": self.random_seed + 1900,
            },
            {
                "scenario_id": f"{Prefix.SCENARIO}21",
                "run_id": self.run_id,
                "name": "Whitefield Inland Container Depot Rail Rake Deficit",
                "description": "Regional shortage of specialized CONCOR container flatbed rail wagons delaying intermodal movements to Chennai Port.",
                "random_seed": self.random_seed + 2000,
            },

            # Domain 6: Multimodal Seaport & Airport Terminal Bottlenecks
            {
                "scenario_id": f"{Prefix.SCENARIO}22",
                "run_id": self.run_id,
                "name": "Chennai Port Shallow Channel Silting Berth Congestion",
                "description": "Post-monsoon littoral sediment accumulation reducing channel draft at Chennai Port, delaying container vessel discharge by 4 days.",
                "random_seed": self.random_seed + 2100,
            },
            {
                "scenario_id": f"{Prefix.SCENARIO}23",
                "run_id": self.run_id,
                "name": "Shamshabad Aerotropolis Airfreight Cargo Crunch",
                "description": "Scheduled widebody cargo freighter cancellation creating an international airfreight embargo at Hyderabad Airport.",
                "random_seed": self.random_seed + 2200,
            },

            # Domain 7: Compound Catastrophic & Systemic Crises
            {
                "scenario_id": f"{Prefix.SCENARIO}24",
                "run_id": self.run_id,
                "name": "Cyclone Michaung Coromandel Plain Compound Inundation",
                "description": "Category-4 cyclonic storm simultaneously flooding SPEL Semiconductor in Maraimalai Nagar and halting Chennai Port operations.",
                "random_seed": self.random_seed + 2300,
            },
            {
                "scenario_id": f"{Prefix.SCENARIO}25",
                "run_id": self.run_id,
                "name": "Peninsular Grid Blackout Sourcing Crisis",
                "description": "Regional electricity transmission grid failure knocking out industrial power across Tamil Nadu and Karnataka, cutting fab throughput to 40%.",
                "random_seed": self.random_seed + 2400,
            },
        ]

        disruption_events: List[Dict[str, Any]] = []

        scenario_disruption_specs = [
            # scen-02: SPEL Semiconductor Delay
            {
                "scenario_id": f"{Prefix.SCENARIO}02",
                "disruption_type": "supplier_delay",
                "target_entity_type": "supplier",
                "target_entity_id": "sup-01",
                "severity": 4,
                "duration_days": 7,
            },
            # scen-03: Demand Spike at Oragadam JIT Warehouse
            {
                "scenario_id": f"{Prefix.SCENARIO}03",
                "disruption_type": "demand_spike",
                "target_entity_type": "warehouse",
                "target_entity_id": "wh-03",
                "severity": 3,
                "duration_days": 14,
            },
            # scen-04: Transport Failure on NH48 Hosur-Sriperumbudur corridor
            {
                "scenario_id": f"{Prefix.SCENARIO}04",
                "disruption_type": "transport_failure",
                "target_entity_type": "route",
                "target_entity_id": "route-wh-01-mfg-01",
                "severity": 5,
                "duration_days": 4,
            },
            # scen-05: Cyclonic Stoppage at Cochin Port
            {
                "scenario_id": f"{Prefix.SCENARIO}05",
                "disruption_type": "adverse_weather",
                "target_entity_type": "distribution_center",
                "target_entity_id": "dc-02",
                "severity": 4,
                "duration_days": 8,
            },
            # scen-06: Discrete Power Fab Cleanroom Outage at CDIL Bengaluru
            {
                "scenario_id": f"{Prefix.SCENARIO}06",
                "disruption_type": "supplier_delay",
                "target_entity_type": "supplier",
                "target_entity_id": "sup-02",
                "severity": 4,
                "duration_days": 6,
            },
            # scen-07: SMT Head Failure at Kaynes Mysuru
            {
                "scenario_id": f"{Prefix.SCENARIO}07",
                "disruption_type": "supplier_delay",
                "target_entity_type": "supplier",
                "target_entity_id": "sup-03",
                "severity": 3,
                "duration_days": 5,
            },
            # scen-08: Solder Defect Lot Quarantine at Syrma Bargur
            {
                "scenario_id": f"{Prefix.SCENARIO}08",
                "disruption_type": "supplier_delay",
                "target_entity_type": "supplier",
                "target_entity_id": "sup-04",
                "severity": 4,
                "duration_days": 7,
            },
            # scen-09: Defense Allocation Rationing at Centum Yelahanka
            {
                "scenario_id": f"{Prefix.SCENARIO}09",
                "disruption_type": "supplier_delay",
                "target_entity_type": "supplier",
                "target_entity_id": "sup-05",
                "severity": 3,
                "duration_days": 10,
            },
            # scen-10: Copper Laminate Stockout at Sahasra Hyderabad
            {
                "scenario_id": f"{Prefix.SCENARIO}10",
                "disruption_type": "supplier_delay",
                "target_entity_type": "supplier",
                "target_entity_id": "sup-08",
                "severity": 4,
                "duration_days": 8,
            },
            # scen-11: Smart Energy IoT Meter Demand Surge
            {
                "scenario_id": f"{Prefix.SCENARIO}11",
                "disruption_type": "demand_spike",
                "target_entity_type": "warehouse",
                "target_entity_id": "wh-01",
                "severity": 4,
                "duration_days": 21,
            },
            # scen-12: EV Powertrain Retrofit Spike
            {
                "scenario_id": f"{Prefix.SCENARIO}12",
                "disruption_type": "demand_spike",
                "target_entity_type": "warehouse",
                "target_entity_id": "wh-02",
                "severity": 5,
                "duration_days": 28,
            },
            # scen-13: Quarter-End Automotive Assembly Ramp-Up
            {
                "scenario_id": f"{Prefix.SCENARIO}13",
                "disruption_type": "demand_spike",
                "target_entity_type": "warehouse",
                "target_entity_id": "wh-03",
                "severity": 3,
                "duration_days": 10,
            },
            # scen-14: Municipal Sensor Network Renewal Push
            {
                "scenario_id": f"{Prefix.SCENARIO}14",
                "disruption_type": "demand_spike",
                "target_entity_type": "distribution_center",
                "target_entity_id": "dc-01",
                "severity": 3,
                "duration_days": 14,
            },
            # scen-15: Attibele Border Truck Checkpost Strike
            {
                "scenario_id": f"{Prefix.SCENARIO}15",
                "disruption_type": "transport_failure",
                "target_entity_type": "route",
                "target_entity_id": "route-sup-02-wh-01",
                "severity": 4,
                "duration_days": 3,
            },
            # scen-16: Palakkad Gap Landslide Halt
            {
                "scenario_id": f"{Prefix.SCENARIO}16",
                "disruption_type": "transport_failure",
                "target_entity_type": "route",
                "target_entity_id": "route-sup-07-mfg-01",
                "severity": 5,
                "duration_days": 6,
            },
            # scen-17: Kurnool Bridge Heavy-Axle Weight Embargo
            {
                "scenario_id": f"{Prefix.SCENARIO}17",
                "disruption_type": "transport_failure",
                "target_entity_type": "route",
                "target_entity_id": "route-sup-08-wh-04",
                "severity": 3,
                "duration_days": 12,
            },
            # scen-18: Chennai Outer Ring Road Heavy Gridlock
            {
                "scenario_id": f"{Prefix.SCENARIO}18",
                "disruption_type": "transport_failure",
                "target_entity_type": "route",
                "target_entity_id": "route-wh-03-mfg-01",
                "severity": 3,
                "duration_days": 2,
            },
            # scen-19: Hosur Buffer AS/RS Crane System Fault
            {
                "scenario_id": f"{Prefix.SCENARIO}19",
                "disruption_type": "transport_failure",
                "target_entity_type": "warehouse",
                "target_entity_id": "wh-01",
                "severity": 4,
                "duration_days": 4,
            },
            # scen-20: Sri City FTWZ Customs Audit Hold
            {
                "scenario_id": f"{Prefix.SCENARIO}20",
                "disruption_type": "supplier_delay",
                "target_entity_type": "warehouse",
                "target_entity_id": "wh-04",
                "severity": 4,
                "duration_days": 7,
            },
            # scen-21: Whitefield ICD Rail Rake Deficit
            {
                "scenario_id": f"{Prefix.SCENARIO}21",
                "disruption_type": "transport_failure",
                "target_entity_type": "warehouse",
                "target_entity_id": "wh-02",
                "severity": 3,
                "duration_days": 5,
            },
            # scen-22: Chennai Port Channel Silting Congestion
            {
                "scenario_id": f"{Prefix.SCENARIO}22",
                "disruption_type": "transport_failure",
                "target_entity_type": "distribution_center",
                "target_entity_id": "dc-01",
                "severity": 3,
                "duration_days": 6,
            },
            # scen-23: Shamshabad Airfreight Cargo Crunch
            {
                "scenario_id": f"{Prefix.SCENARIO}23",
                "disruption_type": "transport_failure",
                "target_entity_type": "distribution_center",
                "target_entity_id": "dc-03",
                "severity": 4,
                "duration_days": 4,
            },
            # scen-24: Cyclone Michaung Compound Inundation
            {
                "scenario_id": f"{Prefix.SCENARIO}24",
                "disruption_type": "adverse_weather",
                "target_entity_type": "supplier",
                "target_entity_id": "sup-01",
                "severity": 5,
                "duration_days": 10,
            },
            # scen-25: Peninsular Grid Blackout Crisis
            {
                "scenario_id": f"{Prefix.SCENARIO}25",
                "disruption_type": "supplier_delay",
                "target_entity_type": "manufacturer",
                "target_entity_id": "mfg-01",
                "severity": 5,
                "duration_days": 5,
            },
        ]

        counter = 1
        for spec in scenario_disruption_specs:
            offset_days = int(history_days * 0.5) + (counter % 10) * 3
            event_start = start_date + timedelta(days=offset_days)
            event_end = event_start + timedelta(days=spec["duration_days"])
            disrupt_id = f"{Prefix.DISRUPTION}{counter:05d}"
            counter += 1

            disruption_events.append({
                "id": disrupt_id,
                "run_id": self.run_id,
                "scenario_id": spec["scenario_id"],
                "disruption_type": spec["disruption_type"],
                "target_entity_type": spec["target_entity_type"],
                "target_entity_id": spec["target_entity_id"],
                "severity": spec["severity"],
                "start_date": event_start,
                "end_date": event_end,
                "status": DisruptionStatus.ACTIVE,
            })

        return {
            "scenarios": scenarios,
            "disruption_events": disruption_events,
        }
