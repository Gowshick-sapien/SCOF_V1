"""Unit tests for Demand Data Access layer."""

import sys
from pathlib import Path

pkg_root = Path(__file__).resolve().parents[1]
workspace_root = Path(__file__).resolve().parents[4]
if str(workspace_root) not in sys.path:
    sys.path.insert(0, str(workspace_root))

from services.agents.demand.src.data_access import DemandDataAccess


def test_data_access_fallback():
    da = DemandDataAccess(db_config={"host": "invalid_host", "port": 9999})
    df, qhash = da.get_historical_demand(product_ids=["prod-101"])

    assert not df.empty
    assert "daily_demand" in df.columns
    assert len(qhash) == 64


def test_query_hash_determinism():
    da = DemandDataAccess()
    sql = "SELECT * FROM order_items WHERE product_id = %s"
    h1 = da.compute_query_hash(sql, ("prod-101",))
    h2 = da.compute_query_hash(sql, ("prod-101",))

    assert h1 == h2
