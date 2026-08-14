"""Unit tests for SupplierFeatureBuilder."""

import pandas as pd
import numpy as np
from services.agents.supplier.src.features import SupplierFeatureBuilder


def test_build_features_nominal():
    fb = SupplierFeatureBuilder()
    delivery_df = pd.DataFrame([
        {
            "supplier_id": "sup-01",
            "delay_days": 0.0,
            "status": "DELIVERED",
        },
        {
            "supplier_id": "sup-01",
            "delay_days": 0.0,
            "status": "DELIVERED",
        },
        {
            "supplier_id": "sup-02",
            "delay_days": 4.0,
            "status": "DELIVERED",
        },
    ])

    disruptions = [{"target_entity_type": "supplier", "target_entity_id": "sup-02", "severity": 4}]
    X, y, f_names = fb.build_features(
        delivery_df=delivery_df,
        disruptions=disruptions,
        alternates_map={"sup-01": 2, "sup-02": 2},
        hop_counts_map={"sup-01": 2, "sup-02": 3},
    )

    assert X.shape == (2, 8)
    assert len(y) == 2
    assert len(f_names) == 8
    # sup-01 should have on-time rate 1.0, disruption severity 0
    assert X[0, 0] == 1.0
    assert X[0, 7] == 0.0
    assert y[0] == 0.0  # reliable
    # sup-02 has disruption severity 4, delay > 2
    assert X[1, 7] == 4.0
    assert y[1] == 1.0  # failure/risk


def test_build_features_empty_df():
    fb = SupplierFeatureBuilder()
    X, y, f_names = fb.build_features(pd.DataFrame())
    assert X.shape == (1, 8)
    assert len(y) == 1
    assert len(f_names) == 8
