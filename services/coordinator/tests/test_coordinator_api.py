"""Integration and unit tests for Coordinator REST API endpoints."""

import os
from fastapi.testclient import TestClient
import pytest
from services.coordinator.src.main import app

os.environ["MOCK_MODE"] = "true"


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_health_endpoint(client):
    """Tests GET /health returns healthy status, agent count, and graph info."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["agent_id"] == "coordinator-agent"
    assert data["graph_compiled"] is True
    assert len(data["graph_hash"]) == 64


def test_metrics_endpoint(client):
    """Tests GET /metrics returns telemetry counters."""
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "orchestrations_executed" in data
    assert "average_latency_ms" in data


def test_agent_card_endpoint(client):
    """Tests GET /.well-known/agent.json returns valid A2A AgentCard."""
    response = client.get("/.well-known/agent.json")
    assert response.status_code == 200
    data = response.json()
    assert data["agent_id"] == "coordinator-agent"
    assert "orchestrate" in data["capabilities"]


def test_agents_list_and_refresh_endpoints(client):
    """Tests GET /agents and POST /agents/refresh."""
    response = client.get("/agents")
    assert response.status_code == 200
    data = response.json()
    assert "total_registered" in data
    assert "agents" in data

    refresh_resp = client.post("/agents/refresh", json={})
    assert refresh_resp.status_code == 200
    refresh_data = refresh_resp.json()
    assert refresh_data["status"] == "success"


def test_graph_endpoint(client):
    """Tests GET /graph returns nodes, edges, hash, and Mermaid flowchart."""
    response = client.get("/graph")
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "edges" in data
    assert "graph_hash" in data
    assert "mermaid" in data
    assert len(data["nodes"]) == 4


def test_orchestrate_endpoint(client):
    """Tests POST /orchestrate produces a valid ClaimBundle."""
    payload = {
        "scenario_id": "scen-test-api-01",
        "run_id": "run-api-01",
        "tick": 10,
        "disruption_type": "baseline_assessment",
        "parameters": {},
    }
    headers = {
        "X-Trace-ID": "test-trace-12345",
        "X-Bundle-ID": "test-bundle-99999",
    }
    response = client.post("/orchestrate", json=payload, headers=headers)
    assert response.status_code == 200
    bundle = response.json()
    assert bundle["scenario_id"] == "scen-test-api-01"
    assert bundle["trace_id"] == "test-trace-12345"
    assert bundle["bundle_id"] == "test-bundle-99999"
    assert bundle["status"] in ("COMPLETE", "PARTIAL")
    assert isinstance(bundle["claims"], dict)
    assert bundle["total_latency_ms"] >= 0.0


def test_analyze_alias_endpoint(client):
    """Tests POST /analyze alias behaves identically to /orchestrate."""
    payload = {
        "scenario_id": "scen-alias-01",
        "run_id": "run-alias-01",
        "tick": 1,
        "disruption_type": "supplier_delay",
        "parameters": {},
    }
    response = client.post("/analyze", json=payload)
    assert response.status_code == 200
    bundle = response.json()
    assert bundle["scenario_id"] == "scen-alias-01"
