"""Unit tests for Database Persistence Writer (DBWriter)."""

from unittest.mock import MagicMock, patch
import pytest
from src.db_writer import DBWriter


@pytest.fixture
def mock_dataset():
    run_metadata = {
        "run_id": "run-001",
        "random_seed": 42,
        "profile_name": "mvp-electronics",
        "profile_version": "1.0.0",
        "profile_hash": "hash123",
        "history_days": 30,
        "total_entities_generated": 10,
        "total_orders_generated": 5,
        "total_shipments_generated": 5,
        "total_inventory_rows": 60,
        "total_disruptions_generated": 1,
        "execution_time_ms": 150,
        "generator_version": "1.0.0",
    }
    master_entities = {
        "manufacturers": [
            {"id": "mfg-01", "name": "Mfg Spec", "latitude": 22.5, "longitude": 114.0}
        ],
        "products": [
            {"id": "prod-01", "name": "Display", "sku": "DISP-01", "manufacturer_id": "mfg-01"}
        ],
        "suppliers": [
            {
                "id": "sup-01",
                "name": "Supplier A",
                "reliability_profile": "high",
                "base_lead_time_days": 5,
                "latitude": 22.3,
                "longitude": 114.1,
            }
        ],
        "supplier_products": [
            {
                "supplier_id": "sup-01",
                "product_id": "prod-01",
                "is_preferred_supplier": True,
                "unit_cost": 100.0,
                "minimum_order_qty": 10,
                "lead_time_override_days": 5,
            }
        ],
        "warehouses": [
            {"id": "wh-01", "name": "Central WH", "capacity_units": 10000, "latitude": 22.4, "longitude": 114.0}
        ],
        "distribution_centers": [
            {"id": "dc-01", "name": "Shenzhen DC", "latitude": 22.5, "longitude": 114.1}
        ],
        "routes": [
            {
                "id": "route-01",
                "origin_type": "supplier",
                "origin_id": "sup-01",
                "destination_type": "warehouse",
                "destination_id": "wh-01",
                "mode": "truck",
                "distance_km": 50.0,
                "standard_transit_days": 1,
            }
        ],
    }
    operational_logs = {
        "purchase_orders": [
            {
                "id": "po-01",
                "run_id": "run-001",
                "supplier_id": "sup-01",
                "destination_warehouse_id": "wh-01",
                "order_date": "2026-01-01",
                "expected_delivery_date": "2026-01-06",
                "actual_delivery_date": "2026-01-06",
                "status": "DELIVERED",
            }
        ],
        "order_items": [
            {"order_id": "po-01", "product_id": "prod-01", "quantity": 100, "unit_cost": 100.0}
        ],
        "shipments": [
            {
                "id": "ship-01",
                "run_id": "run-001",
                "order_id": "po-01",
                "route_id": "route-01",
                "departure_date": "2026-01-01",
                "estimated_arrival": "2026-01-02",
                "actual_arrival": "2026-01-02",
                "status": "DELIVERED",
            }
        ],
        "inventory_levels": [
            {
                "run_id": "run-001",
                "warehouse_id": "wh-01",
                "product_id": "prod-01",
                "date": "2026-01-01",
                "stock_on_hand": 500,
                "safety_stock_threshold": 100,
                "reorder_point": 200,
                "units_in_transit": 0,
            }
        ],
    }
    disruption_data = {
        "scenarios": [
            {
                "scenario_id": "scen-01",
                "run_id": "run-001",
                "name": "Typhoon Disruption",
                "description": "Port delay",
                "random_seed": 42,
            }
        ],
        "disruption_events": [
            {
                "id": "dis-01",
                "run_id": "run-001",
                "scenario_id": "scen-01",
                "disruption_type": "supplier_delay",
                "target_entity_type": "supplier",
                "target_entity_id": "sup-01",
                "severity": 0.5,
                "start_date": "2026-01-10",
                "end_date": "2026-01-15",
                "status": "RESOLVED",
            }
        ],
    }
    return run_metadata, master_entities, operational_logs, disruption_data


def test_db_writer_initialization():
    writer = DBWriter("postgresql://user:pass@localhost:5432/scof")
    assert writer.dsn == "postgresql://user:pass@localhost:5432/scof"


@patch("psycopg.connect")
def test_write_simulation_dataset(mock_connect, mock_dataset):
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_connect.return_value.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cur

    run_meta, master_ent, ops_logs, disrupt = mock_dataset
    writer = DBWriter("postgresql://user:pass@localhost:5432/scof")

    writer.write_simulation_dataset(run_meta, master_ent, ops_logs, disrupt)

    assert mock_connect.called
    assert mock_cur.execute.called
    assert mock_cur.executemany.called
    assert mock_conn.commit.called
