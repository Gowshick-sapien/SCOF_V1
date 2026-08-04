"""Unit tests for Demand Feature Builder."""

import sys
from pathlib import Path

pkg_root = Path(__file__).resolve().parents[1]
if str(pkg_root) not in sys.path:
    sys.path.insert(0, str(pkg_root))

import pandas as pd
import numpy as np
from src.features import DemandFeatureBuilder


def test_feature_builder_empty_dataframe():
    builder = DemandFeatureBuilder()
    X, y, feature_names = builder.build_features(pd.DataFrame(), [])

    assert X.shape[0] == 30
    assert len(y) == 30
    assert "day_of_week" in feature_names
    assert "disruption_severity" in feature_names


def test_feature_builder_valid_dataframe():
    builder = DemandFeatureBuilder()
    df = pd.DataFrame({
        "date": ["2026-01-01", "2026-01-02", "2026-01-03", "2026-01-04"],
        "daily_demand": [100.0, 110.0, 105.0, 120.0],
    })
    disruptions = [{"disruption_type": "demand_spike", "severity": 8}]

    X, y, feature_names = builder.build_features(df, disruptions)

    assert X.shape[0] == 4
    assert X.shape[1] == len(feature_names)
    assert np.array_equal(y, np.array([100.0, 110.0, 105.0, 120.0]))
    assert X[-1, -1] == 8.0
