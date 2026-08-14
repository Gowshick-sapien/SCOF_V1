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
                "name": "Baseline Normal Operations",
                "description": "Standard operational baseline with no active systemic disruptions.",
                "random_seed": self.random_seed,
            },
            {
                "scenario_id": f"{Prefix.SCENARIO}02",
                "run_id": self.run_id,
                "name": "Multi-Disruption Stress Test",
                "description": "Stress test scenario injecting supplier lead time delay and route failures.",
                "random_seed": self.random_seed + 100,
            },
        ]

        disruption_events: List[Dict[str, Any]] = []
        counter = 1

        disruption_types = self.profile.disruptions.disruption_types

        # For scenario 2, create 3-4 realistic disruption events
        target_suppliers = self.master_entities["suppliers"]
        target_routes = self.master_entities["routes"]
        target_products = self.master_entities["products"]

        for d_type in disruption_types:
            dtype_id = d_type.id
            target_kind = d_type.target_entity

            # Pick target entity ID based on kind
            if target_kind == "supplier" and target_suppliers:
                entity_id = target_suppliers[0]["id"]
            elif target_kind == "route" and target_routes:
                entity_id = target_routes[0]["id"]
            elif target_kind == "product" and target_products:
                entity_id = target_products[0]["id"]
            else:
                continue

            sev = int(np.random.randint(d_type.severity_range[0], d_type.severity_range[1] + 1))
            dur = d_type.default_duration_days

            # Set start date in the middle of simulation history
            offset_days = int(history_days * 0.4) + counter * 5
            event_start = start_date + timedelta(days=offset_days)
            event_end = event_start + timedelta(days=dur)

            disrupt_id = f"{Prefix.DISRUPTION}{counter:05d}"
            counter += 1

            disruption_events.append({
                "id": disrupt_id,
                "run_id": self.run_id,
                "scenario_id": f"{Prefix.SCENARIO}02",
                "disruption_type": dtype_id,
                "target_entity_type": target_kind,
                "target_entity_id": entity_id,
                "severity": sev,
                "start_date": event_start,
                "end_date": event_end,
                "status": DisruptionStatus.RESOLVED if event_end < (start_date + timedelta(days=history_days)) else DisruptionStatus.ACTIVE,
            })

        return {
            "scenarios": scenarios,
            "disruption_events": disruption_events,
        }
