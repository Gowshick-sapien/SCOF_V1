import pytest
from unittest.mock import MagicMock
from services.etl.src.load_graph import GraphLoader

def test_graph_loader_batch_queries():
    mock_client = MagicMock()
    loader = GraphLoader(client=mock_client)

    payload = {
        "manufacturers": [{"id": "mfg-01", "name": "Apex", "latitude": 22.5, "longitude": 114.0}],
        "suppliers": [{"id": "sup-01", "name": "Semico", "reliability_profile": "high", "base_lead_time_days": 7, "latitude": 24.1, "longitude": 120.6}],
        "products": [{"id": "prod-101", "name": "IoT Controller", "sku": "SKU-101"}],
        "warehouses": [{"id": "wh-01", "name": "Transit Hub", "capacity_units": 50000, "latitude": 22.3, "longitude": 114.1}],
        "distribution_centers": [{"id": "dc-01", "name": "Central Hub", "latitude": 25.0, "longitude": 121.5}],
        "routes": [{"id": "route-sup01-wh01", "origin_type": "supplier", "origin_id": "sup-01", "destination_type": "warehouse", "destination_id": "wh-01", "mode": "ocean", "distance_km": 750.0, "standard_transit_days": 5}],
        "produces_edges": [{"manufacturer_id": "mfg-01", "product_id": "prod-101", "production_capacity_units": 10000}],
        "supplies_edges": [{"supplier_id": "sup-01", "product_id": "prod-101", "unit_cost": 45.0, "lead_time_days": 7, "minimum_order_qty": 100, "is_preferred": True, "contract_id": "cnt-01"}]
    }

    loader.load_all(payload)
    assert mock_client.execute_batch.call_count >= 8
