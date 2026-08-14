"""Unit tests for TransportDataAccess layer."""

import pandas as pd
from services.agents.transportation.src.data_access import TransportDataAccess


def test_transport_shipment_history_mock():
    da = TransportDataAccess()
    # Fast failover so it uses fallback mock
    da._postgres_available = False

    df, qhash = da.get_shipment_delivery_history(carrier_ids=["PacificFreight", "ApexLogistics"])
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "delay_days" in df.columns
    assert "carrier_id" in df.columns
    assert len(qhash) == 64


def test_transport_route_graph_mock():
    da = TransportDataAccess()
    da._neo4j_available = False

    routes, qhash = da.get_route_graph_data(origin="sup-01", destination="wh-01")
    assert isinstance(routes, list)
    assert len(routes) >= 1
    assert "transit_time_days" in routes[0]
    assert len(qhash) == 64


def test_transport_alternate_routes_mock():
    da = TransportDataAccess()
    da._neo4j_available = False

    alts, qhash = da.get_alternate_routes(disrupted_route_id="route-sea-01")
    assert isinstance(alts, list)
    assert len(alts) >= 1
    assert "alt_route_id" in alts[0]
    assert "alt_mode" in alts[0]
    assert len(qhash) == 64
