import pytest
from services.etl.src.transform import DataTransformer

def test_data_transformer_graph_payloads():
    raw_data = {
        "manufacturers": [{"id": "mfg-01", "name": "Apex", "latitude": 22.5, "longitude": 114.0}],
        "products": [{"id": "prod-101", "name": "IoT Controller", "sku": "SKU-101", "manufacturer_id": "mfg-01"}],
        "suppliers": [{"id": "sup-01", "name": "Semico", "reliability_profile": "high", "base_lead_time_days": 7, "latitude": 24.1, "longitude": 120.6}],
        "supplier_products": [{"supplier_id": "sup-01", "product_id": "prod-101", "is_preferred_supplier": True, "unit_cost": 45.0, "minimum_order_qty": 100, "lead_time_override_days": 7}],
        "warehouses": [{"id": "wh-01", "name": "Transit Hub", "capacity_units": 50000, "latitude": 22.3, "longitude": 114.1}],
        "distribution_centers": [{"id": "dc-01", "name": "Central Hub", "latitude": 25.0, "longitude": 121.5}],
        "routes": [{"id": "route-sup01-wh01", "origin_type": "supplier", "origin_id": "sup-01", "destination_type": "warehouse", "destination_id": "wh-01", "mode": "ocean", "distance_km": 750.0, "standard_transit_days": 5}]
    }

    transformer = DataTransformer()
    transformed = transformer.transform_graph_payloads(raw_data)

    assert len(transformed["manufacturers"]) == 1
    assert len(transformed["products"]) == 1
    assert len(transformed["suppliers"]) == 1
    assert len(transformed["supplies_edges"]) == 1
    assert transformed["supplies_edges"][0]["unit_cost"] == 45.0
    assert transformed["supplies_edges"][0]["lead_time_days"] == 7
    assert len(transformed["ships_via_edges"]) == 1
    assert transformed["ships_via_edges"][0]["mode"] == "ocean"

def test_data_transformer_vector_payloads():
    raw_data = {
        "disruptions": [{
            "id": "disrupt-00001",
            "run_id": "run-001",
            "scenario_id": "scen-01",
            "disruption_type": "SUPPLIER_DELAY",
            "target_entity_type": "supplier",
            "target_entity_id": "sup-01",
            "severity": 4,
            "start_date": "2026-07-01",
            "end_date": "2026-07-15",
            "status": "ACTIVE"
        }]
    }

    transformer = DataTransformer()
    vector_payload = transformer.transform_vector_payloads(raw_data)

    assert len(vector_payload["decisions"]) == 1
    assert len(vector_payload["evidence_snippets"]) == 1
    assert len(vector_payload["embedding_items"]) == 2
    assert vector_payload["decisions"][0]["decision_type"] == "REROUTE"
    assert vector_payload["decisions"][0]["created_by"] == "SupplierAgent"
