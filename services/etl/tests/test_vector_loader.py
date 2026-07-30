import pytest
from unittest.mock import MagicMock, patch
from services.etl.src.load_vector import VectorLoader

@patch("services.etl.src.load_vector.VectorLoader._get_connection")
def test_vector_loader_batch_insert(mock_get_conn):
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cur
    mock_get_conn.return_value.__enter__.return_value = mock_conn

    loader = VectorLoader(db_url="postgresql://test:test@localhost/test")

    decisions = [{
        "id": "dec-00001",
        "scenario_id": "scen-01",
        "run_id": "run-001",
        "disruption_id": "disrupt-00001",
        "decision_type": "REROUTE",
        "recommendation": "Reroute shipment",
        "confidence": 0.95,
        "priority": "HIGH",
        "impact_summary": "Impact summary text",
        "created_by": "SupplierAgent",
        "simulation_tick": 10,
        "outcome": "APPROVED",
        "status": "ACTIVE"
    }]

    loader.load_decisions(decisions)
    assert mock_cur.executemany.called
