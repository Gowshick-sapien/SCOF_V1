"""Feature engineering pipeline for Demand Agent."""

from typing import Any, Dict, List, Tuple
import numpy as np
import pandas as pd


class DemandFeatureBuilder:
    """Transforms raw time-series demand data into ML feature matrices."""

    def build_features(
        self,
        demand_df: pd.DataFrame,
        disruptions: List[Dict[str, Any]],
    ) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """Constructs feature matrix X and target y for model training/inference.

        Features created:
        - day_of_week (0-6)
        - rolling_7d_mean
        - rolling_14d_mean
        - rolling_30d_mean
        - lag_1
        - lag_7
        - disruption_severity_exogenous
        """
        if demand_df.empty:
            # Generate default synthetic feature set for zero-state
            X = np.zeros((30, 7), dtype=float)
            y = np.full(30, 100.0, dtype=float)
            feature_names = [
                "day_of_week",
                "rolling_7d_mean",
                "rolling_14d_mean",
                "rolling_30d_mean",
                "lag_1",
                "lag_7",
                "disruption_severity",
            ]
            return X, y, feature_names

        df = demand_df.copy()
        if "daily_demand" not in df.columns:
            df["daily_demand"] = 100.0

        series = np.asarray(df["daily_demand"].values, dtype=float)
        n = len(series)

        # Day of week
        dow = np.arange(n) % 7

        # Rolling statistics
        r7 = np.asarray(pd.Series(series).rolling(7, min_periods=1).mean().values, dtype=float)  # type: ignore
        r14 = np.asarray(pd.Series(series).rolling(14, min_periods=1).mean().values, dtype=float)  # type: ignore
        r30 = np.asarray(pd.Series(series).rolling(30, min_periods=1).mean().values, dtype=float)  # type: ignore

        # Lags
        lag1 = np.roll(series, 1)
        lag1[0] = series[0]
        lag7 = np.roll(series, 7)
        lag7[:7] = series[0]

        # Disruption exogenous feature
        disr_sev = np.zeros(n, dtype=float)
        for d in disruptions:
            if d.get("disruption_type") == "demand_spike":
                disr_sev += float(d.get("severity", 5))

        X = np.column_stack([dow, r7, r14, r30, lag1, lag7, disr_sev])
        y = series.astype(float)

        feature_names = [
            "day_of_week",
            "rolling_7d_mean",
            "rolling_14d_mean",
            "rolling_30d_mean",
            "lag_1",
            "lag_7",
            "disruption_severity",
        ]

        return X, y, feature_names
