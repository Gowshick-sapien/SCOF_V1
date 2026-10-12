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
                "name": "Automotive Telematics Sensor Demand Surge (Oragadam Hub)",
                "description": "Sudden 45% regional order surge for Automotive Sensor Hubs (prod-102) buffering at Oragadam JIT Warehouse (wh-03).",
                "random_seed": self.random_seed + 200,
            },
            {
                "scenario_id": f"{Prefix.SCENARIO}04",
                "run_id": self.run_id,
                "name": "NH48 Arterial Freight Corridor Monsoon Closure",
                "description": "Severe monsoon waterlogging along the NH48 interstate freight lane halting truck transit from Hosur Buffer Warehouse (wh-01) to Sriperumbudur Assembly Hub (mfg-01).",
                "random_seed": self.random_seed + 300,
            },
            {
                "scenario_id": f"{Prefix.SCENARIO}05",
                "run_id": self.run_id,
                "name": "Cochin Port Deep-Water Terminal Cyclonic Stoppage",
                "description": "Arabian Sea cyclonic disturbance forcing 8-day operational container cranes shutdown at Cochin Vallarpadam International Terminal (dc-02).",
                "random_seed": self.random_seed + 400,
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
        ]

        counter = 1
        for spec in scenario_disruption_specs:
            offset_days = int(history_days * 0.5) + counter * 3
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

