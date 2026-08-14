"""Unit tests for Inventory Feature Builder."""

import sys
from pathlib import Path

pkg_root = Path(__file__).resolve().parents[1]
workspace_root = Path(__file__).resolve().parents[4]
if str(workspace_root) not in sys.path:
    sys.path.insert(0, str(workspace_root))

import pandas as pd
import numpy as np
from services.agents.inventory.src.features import InventoryFeatureBuilder


def test_inventory_feature_builder_empty():
    builder = InventoryFeatureBuilder()
    X, y, feature_names = builder.build_features(pd.DataFrame(), [])

    assert X.shape[0] == 30
    assert len(y) == 30
    assert "current_stock" in feature_names
    assert "disruption_severity" in feature_names


def test_inventory_feature_builder_valid():
    builder = InventoryFeatureBuilder()
    df = pd.DataFrame({
        "quantity_on_hand": [500.0, 480.0, 460.0, 440.0],
        "reorder_point": [150.0, 150.0, 150.0, 150.0],
        "safety_stock": [80.0, 80.0, 80.0, 80.0],
    })
    disruptions = [{"disruption_type": "supplier_delay", "severity": 7}]

    X, y, feature_names = builder.build_features(df, disruptions)

    assert X.shape[0] == 4
    assert X.shape[1] == len(feature_names)
    assert X[-1, -1] == 7.0
