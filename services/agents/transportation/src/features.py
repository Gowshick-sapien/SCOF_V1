"""Feature engineering for Transportation Agent.

Builds feature vectors from PostgreSQL shipment histories and Neo4j route topology
for DelayPredictor and RouteScorer models.
"""

from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd


class TransportFeatureBuilder:
    """Extracts structured numerical feature matrices for transit delay and route scoring."""

    FEATURE_NAMES = [
        "carrier_on_time_rate",
        "carrier_avg_delay_days",
        "mode_transit_time_days",
        "route_cost",
        "hop_count",
        "carrier_volume_share",
        "weather_severity",
        "port_congestion_severity",
    ]

    def build_features(
        self,
        shipment_df: pd.DataFrame,
        disruptions: Optional[List[Dict[str, Any]]] = None,
        route_details: Optional[List[Dict[str, Any]]] = None,
        hop_counts_map: Optional[Dict[str, int]] = None,
    ) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """Constructs (X, y, feature_names) feature matrix.

        Returns:
            X: np.ndarray of shape (N, 8)
            y: np.ndarray of shape (N,) containing delay_days
            feature_names: List of 8 feature column names
        """
        disruptions = disruptions or []
        route_details = route_details or []
        hop_counts_map = hop_counts_map or {}

        if shipment_df.empty:
            # Return single nominal baseline sample
            X = np.array([[0.92, 0.5, 5.0, 1000.0, 2.0, 0.25, 0.0, 0.0]], dtype=float)
            y = np.array([0.5], dtype=float)
            return X, y, self.FEATURE_NAMES

        # Carrier performance aggregations
        carrier_groups = shipment_df.groupby("carrier_id")
        total_shipments = len(shipment_df)

        carrier_stats = {}
        for c_id, group in carrier_groups:
            on_time_count = (group["delay_days"] <= 0).sum()
            total_c = len(group)
            on_time_rate = float(on_time_count / max(1, total_c))
            avg_delay = float(group["delay_days"].mean())
            volume_share = float(total_c / max(1, total_shipments))
            carrier_stats[c_id] = {
                "on_time_rate": on_time_rate,
                "avg_delay": avg_delay,
                "volume_share": volume_share,
            }

        # Route details lookup
        route_stats = {}
        for r in route_details:
            r_id = r.get("route_id") or r.get("carrier")
            if r_id:
                route_stats[r_id] = {
                    "transit_time": float(r.get("transit_time_days", 5.0)),
                    "cost": float(r.get("cost", 1000.0)),
                    "hop_count": float(r.get("hop_count", 2)),
                }

        # Active disruption extraction
        weather_sev = 0.0
        port_sev = 0.0
        for d in disruptions:
            d_type = d.get("disruption_type", "")
            sev = float(d.get("severity", 0))
            if "weather" in d_type or "storm" in d_type:
                weather_sev = max(weather_sev, sev)
            elif "port" in d_type or "congestion" in d_type or "canal" in d_type:
                port_sev = max(port_sev, sev)

        # Build feature rows per unique carrier/route
        unique_carriers = list(shipment_df["carrier_id"].unique())
        rows = []
        targets = []

        for c_id in unique_carriers:
            c_data = carrier_stats.get(c_id, {"on_time_rate": 0.85, "avg_delay": 1.0, "volume_share": 0.2})
            r_data = route_stats.get(c_id, {"transit_time": 5.0, "cost": 1000.0, "hop_count": 2})

            c_shipments = shipment_df[shipment_df["carrier_id"] == c_id]
            carrier_delay = float(c_shipments["delay_days"].mean()) if not c_shipments.empty else 0.0

            # Disruption boost on target entity
            target_weather = weather_sev if any(d.get("target_entity_id") == c_id for d in disruptions) or weather_sev > 0 else 0.0
            target_port = port_sev if any(d.get("target_entity_id") == c_id for d in disruptions) or port_sev > 0 else 0.0

            hop_cnt = float(hop_counts_map.get(c_id, r_data.get("hop_count", 2)))

            feat = [
                c_data["on_time_rate"],
                c_data["avg_delay"],
                r_data["transit_time"],
                r_data["cost"],
                hop_cnt,
                c_data["volume_share"],
                target_weather,
                target_port,
            ]
            rows.append(feat)
            targets.append(carrier_delay)

        X = np.array(rows, dtype=float)
        y = np.array(targets, dtype=float)

        return X, y, self.FEATURE_NAMES
