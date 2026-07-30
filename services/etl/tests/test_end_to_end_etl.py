import pytest
from services.etl.src.extract import DataExtractor
from services.etl.src.transform import DataTransformer
from services.etl.src.embedding_service import EmbeddingService

def test_pipeline_transformation_flow():
    extractor = DataExtractor()
    transformer = DataTransformer()
    embedding_svc = EmbeddingService()

    # Mock raw data
    raw_data = {
        "manufacturers": [{"id": "mfg-01", "name": "Apex", "latitude": 22.5, "longitude": 114.0}],
        "products": [{"id": "prod-101", "name": "Smart Controller", "sku": "SKU-101", "manufacturer_id": "mfg-01"}],
        "suppliers": [{"id": "sup-01", "name": "Semico", "reliability_profile": "high", "base_lead_time_days": 7, "latitude": 24.1, "longitude": 120.6}],
        "supplier_products": [{"supplier_id": "sup-01", "product_id": "prod-101", "is_preferred_supplier": True, "unit_cost": 50.0, "minimum_order_qty": 10, "lead_time_override_days": 7}],
        "warehouses": [{"id": "wh-01", "name": "Transit Hub", "capacity_units": 50000, "latitude": 22.3, "longitude": 114.1}],
        "distribution_centers": [{"id": "dc-01", "name": "Central Hub", "latitude": 25.0, "longitude": 121.5}],
        "routes": [{"id": "route-sup01-wh01", "origin_type": "supplier", "origin_id": "sup-01", "destination_type": "warehouse", "destination_id": "wh-01", "mode": "ocean", "distance_km": 750.0, "standard_transit_days": 5}],
        "disruptions": [{"id": "disrupt-00001", "run_id": "run-001", "scenario_id": "scen-01", "disruption_type": "SUPPLIER_DELAY", "target_entity_type": "supplier", "target_entity_id": "sup-01", "severity": 3, "start_date": "2026-07-01", "end_date": "2026-07-15", "status": "ACTIVE"}]
    }

    graph_payload = transformer.transform_graph_payloads(raw_data)
    vector_payload = transformer.transform_vector_payloads(raw_data)

    assert len(graph_payload["suppliers"]) == 1
    assert len(vector_payload["decisions"]) == 1

    for item in vector_payload["embedding_items"]:
        vec = embedding_svc.generate_embedding(item["content_text"])
        assert len(vec) == 384
