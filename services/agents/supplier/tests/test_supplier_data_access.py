"""Unit tests for SupplierDataAccess."""

from src.data_access import SupplierDataAccess


def test_supplier_delivery_history_mock():
    da = SupplierDataAccess()
    df, qhash = da.get_supplier_delivery_history(supplier_ids=["sup-01", "sup-02"])

    assert not df.empty
    assert "supplier_id" in df.columns
    assert "delay_days" in df.columns
    assert "status" in df.columns
    assert len(qhash) == 64  # SHA-256


def test_supplier_graph_data_mock():
    da = SupplierDataAccess()
    lineage, qhash = da.get_supplier_graph_data(supplier_id="sup-01", product_id="prod-101")

    assert len(lineage) > 0
    assert lineage[0]["supplier_id"] == "sup-01"
    assert len(qhash) == 64


def test_supplier_alternate_suppliers_mock():
    da = SupplierDataAccess()
    # sup-02 should have alternates
    alts, qhash = da.get_alternate_suppliers(supplier_id="sup-02", product_id="prod-101")
    assert len(alts) >= 2
    alt_ids = [a["alt_supplier_id"] for a in alts]
    assert "sup-01" in alt_ids

    # sup-05 has no alternates (disconnected node test)
    alts_05, _ = da.get_alternate_suppliers(supplier_id="sup-05", product_id="prod-103")
    assert len(alts_05) == 0


def test_supplier_hop_count():
    da = SupplierDataAccess()
    hops, qhash = da.get_supplier_hop_count("sup-01", "wh-01")
    assert isinstance(hops, int)
    assert hops >= 1
    assert len(qhash) == 64
