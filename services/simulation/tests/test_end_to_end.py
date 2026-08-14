"""End-to-End Pipeline Unit Test."""

from pathlib import Path
# type: ignore
from services.simulation.src.main import run_pipeline


def test_full_simulation_pipeline():
    manifest = run_pipeline(db_persist=False)

    assert manifest["profile_name"] == "mvp-electronics"
    assert manifest["profile_version"] == "1.0.0"
    assert len(manifest["profile_hash"]) == 64
    assert manifest["total_entities_generated"] > 0
    assert manifest["total_orders_generated"] > 0
    assert manifest["total_shipments_generated"] > 0
    assert manifest["total_inventory_rows"] > 0
    assert manifest["total_disruptions_generated"] > 0

    counts = manifest["row_counts"]
    assert counts["manufacturers"] == 1
    assert counts["products"] == 3
    assert counts["suppliers"] == 5
    assert counts["supplier_products"] == 6
    assert counts["warehouses"] == 2
    assert counts["distribution_centers"] == 1
    assert counts["routes"] > 0
    assert counts["purchase_orders"] > 0
    assert counts["inventory_levels"] > 0

    assert Path("generation_manifest.json").exists()
