"""Feature engineering pipeline for Inventory Agent."""

from typing import Any, Dict, List, Tuple
import numpy as np
import pandas as pd


class InventoryFeatureBuilder:
    """Transforms raw inventory level data into ML feature matrices."""

    def build_features(
        self,
        inventory_df: pd.DataFrame,
        disruptions: List[Dict[str, Any]],
    ) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """Constructs feature matrix X and target y (projected stock level).

        Features created:
        - current_stock
        - depletion_rate_7d
        - days_of_supply
        - safety_stock_proximity
        - reorder_point_proximity
        - disruption_severity
        """
        if inventory_df.empty:
            X = np.zeros((30, 6), dtype=float)
            y = np.full(30, 100.0, dtype=float)
            feature_names = [
                "current_stock",
                "depletion_rate_7d",
                "days_of_supply",
                "safety_stock_proximity",
                "reorder_point_proximity",
                "disruption_severity",
            ]
            return X, y, feature_names

        df = inventory_df.copy()
        if "quantity_on_hand" not in df.columns:
            df["quantity_on_hand"] = 500.0
        if "reorder_point" not in df.columns:
            df["reorder_point"] = 150.0
        if "safety_stock" not in df.columns:
            df["safety_stock"] = 80.0

        stock = np.asarray(df["quantity_on_hand"].values, dtype=float)
        n = len(stock)

        # Depletion rate calculation (diff)
        diffs = np.diff(stock, prepend=stock[0])
        depletion_rate = np.maximum(0.1, -np.asarray(pd.Series(diffs).rolling(7, min_periods=1).mean().values, dtype=float))  # type: ignore

        days_of_supply = stock / depletion_rate
        safety_prox = stock - np.asarray(df["safety_stock"].values, dtype=float)
        reorder_prox = stock - np.asarray(df["reorder_point"].values, dtype=float)

        # Disruption severity feature
        disr_sev = np.zeros(n, dtype=float)
        for d in disruptions:
            if d.get("disruption_type") in ("supplier_delay", "port_closure", "route_blocked"):
                disr_sev += float(d.get("severity", 5))

        X = np.column_stack([stock, depletion_rate, days_of_supply, safety_prox, reorder_prox, disr_sev])
        y = stock.astype(float)

        feature_names = [
            "current_stock",
            "depletion_rate_7d",
            "days_of_supply",
            "safety_stock_proximity",
            "reorder_point_proximity",
            "disruption_severity",
        ]

        return X, y, feature_names
