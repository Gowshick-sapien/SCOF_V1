"""Unit tests for TransportFeatureBuilder."""

import numpy as np
import pandas as pd
from src.features import TransportFeatureBuilder


def test_build_transport_features_nominal():
    fb = TransportFeatureBuilder()
    shipment_df = pd.DataFrame([
        {"shipment_id": "s1", "carrier_id": "PacificFreight", "delay_days": 0.0, "shipping_cost": 1200.0},
        {"shipment_id": "s2", "carrier_id": "PacificFreight", "delay_days": 2.0, "shipping_cost": 1250.0},
        {"shipment_id": "s3", "carrier_id": "ApexLogistics", "delay_days": 0.0, "shipping_cost": 850.0},
    ])
    disruptions = [{"disruption_type": "weather_delay", "severity": 4, "target_entity_id": "PacificFreight"}]
    route_details = [
        {"route_id": "PacificFreight", "transit_time_days": 14.0, "cost": 1200.0, "hop_count": 2},
        {"route_id": "ApexLogistics", "transit_time_days": 3.0, "cost": 850.0, "hop_count": 1},
    ]

    X, y, f_names = fb.build_features(
        shipment_df=shipment_df,
        disruptions=disruptions,
        route_details=route_details,
    )

    assert X.ndim == 2
    assert X.shape[1] == 8
    assert len(f_names) == 8
    assert len(y) == X.shape[0]
    assert np.all(y >= 0.0)


def test_build_transport_features_empty_df():
    fb = TransportFeatureBuilder()
    X, y, f_names = fb.build_features(shipment_df=pd.DataFrame())

    assert X.shape == (1, 8)
    assert len(y) == 1
    assert len(f_names) == 8
