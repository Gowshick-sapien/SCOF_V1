"""Feature Engineering Pipeline for Supplier Intelligence Agent."""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd


class SupplierFeatureBuilder:
    """Constructs feature vectors from delivery performance history and Neo4j graph topology."""

    FEATURE_NAMES = [
        "on_time_delivery_rate",
        "avg_delay_days",
        "max_delay_days",
        "order_fulfillment_rate",
        "alternate_supplier_count",
        "supply_chain_hop_count",
        "lead_time_reliability",
        "disruption_severity",
    ]

    def build_features(
        self,
        delivery_df: pd.DataFrame,
        disruptions: Optional[List[Dict[str, Any]]] = None,
        graph_data: Optional[List[Dict[str, Any]]] = None,
        alternates_map: Optional[Dict[str, int]] = None,
        hop_counts_map: Optional[Dict[str, int]] = None,
    ) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """
        Builds feature matrix X and target vector y for suppliers present in delivery_df.
        
        Returns:
            X: np.ndarray of shape (N_samples, N_features)
            y: np.ndarray of shape (N_samples,) containing binary failure indicator (1=failure/high-risk, 0=reliable)
            feature_names: List[str]
        """
        disruptions = disruptions or []
        graph_data = graph_data or []
        alternates_map = alternates_map or {}
        hop_counts_map = hop_counts_map or {}

        # Map active disruptions by target_entity_id
        disruption_sev_by_supplier: Dict[str, float] = {}
        for d in disruptions:
            if d.get("target_entity_type") == "supplier":
                sup_id = str(d.get("target_entity_id", ""))
                sev = float(d.get("severity", 0.0))
                disruption_sev_by_supplier[sup_id] = max(disruption_sev_by_supplier.get(sup_id, 0.0), sev)

        if delivery_df.empty:
            # Return synthetic sample row if dataframe is empty
            X_dummy = np.array([[0.95, 0.2, 1.0, 0.98, 2.0, 2.0, 0.5, 0.0]])
            y_dummy = np.array([0.0])
            return X_dummy, y_dummy, self.FEATURE_NAMES

        suppliers = delivery_df["supplier_id"].unique()
        feature_rows: List[List[float]] = []
        target_labels: List[float] = []

        for sup_id in suppliers:
            sup_orders = delivery_df[delivery_df["supplier_id"] == sup_id]
            total_orders = len(sup_orders)

            if total_orders == 0:
                continue

            # On-time delivery rate
            on_time_mask = sup_orders["delay_days"] <= 0.0
            on_time_rate = float(on_time_mask.sum() / total_orders)

            # Delay metrics
            delays = sup_orders["delay_days"].to_numpy()
            avg_delay = float(np.mean(delays))
            max_delay = float(np.max(delays))

            # Order fulfillment rate
            delivered_mask = sup_orders["status"] == "DELIVERED"
            fulfillment_rate = float(delivered_mask.sum() / total_orders)

            # Alternates & Hops
            alt_count = float(alternates_map.get(sup_id, 2))
            hop_count = float(hop_counts_map.get(sup_id, 2))

            # Lead time consistency (standard deviation of delay)
            lead_time_std = float(np.std(delays)) if total_orders > 1 else 0.5

            # Disruption severity
            disr_sev = float(disruption_sev_by_supplier.get(sup_id, 0.0))

            feature_vec = [
                on_time_rate,
                avg_delay,
                max_delay,
                fulfillment_rate,
                alt_count,
                hop_count,
                lead_time_std,
                disr_sev,
            ]
            feature_rows.append(feature_vec)

            # Target label: 1 if failure/unreliable, 0 if healthy
            is_failure = 1.0 if (on_time_rate < 0.75 or avg_delay > 2.0 or disr_sev >= 3.0) else 0.0
            target_labels.append(is_failure)

        if not feature_rows:
            X_dummy = np.array([[0.95, 0.2, 1.0, 0.98, 2.0, 2.0, 0.5, 0.0]])
            y_dummy = np.array([0.0])
            return X_dummy, y_dummy, self.FEATURE_NAMES

        X = np.array(feature_rows, dtype=float)
        y = np.array(target_labels, dtype=float)
        return X, y, self.FEATURE_NAMES
