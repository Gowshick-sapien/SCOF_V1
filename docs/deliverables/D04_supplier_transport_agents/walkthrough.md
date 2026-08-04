# Deliverable D4 Walkthrough — Supplier Intelligence & Transportation Agents

## Summary of Accomplishments

Deliverable D4 completes the reliability agent slice of SCOF by implementing the **Supplier Intelligence Agent (`supplier-agent`)** and **Transportation Agent (`transport-agent`)** as standalone, independently testable FastAPI microservices conforming to the universal **Structured Claim contract**, **A2A Agent Card specification**, and **MCP tool declarations**. These agents query PostgreSQL historical operational metrics and Neo4j graph topology to assess supplier reliability, predict transit delays, and compute deterministic alternate supplier and route rankings during disruptions. D4 delivers:

1. **Supplier Intelligence Agent Microservice (`services/agents/supplier/`)**:
   - FastAPI microservice running on port `8013` with endpoints `POST /analyze`, `GET /health`, and `GET /.well-known/agent.json`.
   - Four-stage pipeline: `SupplierDataAccess` -> `SupplierFeatureBuilder` -> `SupplierEnsemble` -> `ClaimBuilder`.
   - **Machine Learning & Rule Models**:
     - [`reliability_scorer.py`](file:///d:/projects/SCOF_V1/SCOF/services/agents/supplier/src/models/reliability_scorer.py): `GradientBoostingClassifier` with residual calibration for prediction intervals and probabilistic reliability estimation.
     - [`rule_scorer.py`](file:///d:/projects/SCOF_V1/SCOF/services/agents/supplier/src/models/rule_scorer.py): `RuleScorerInitializer` + `RuleScorerInference` calculating statistical baseline scores from delivery history.
     - [`ensemble.py`](file:///d:/projects/SCOF_V1/SCOF/services/agents/supplier/src/models/ensemble.py): Weighted combination of ML model (60%) and rule model (40%).
   - **Deterministic Alternate Supplier Ranking**: Multi-criteria weighted normalization evaluating predicted reliability (40%), normalized lead time (30%), normalized unit cost (20%), and graph network proximity (10%).
   - **Data Access & Fallbacks**: Dual PostgreSQL operational query engine and Neo4j graph lineage/alternate supplier retrieval with resilient mock fallbacks ([`data_access.py`](file:///d:/projects/SCOF_V1/SCOF/services/agents/supplier/src/data_access.py)).
   - **Declared MCP Tools**: `query_supplier_graph`, `read_delivery_history`, `read_supplier_disruptions`.
   - Standalone unit test suite in [services/agents/supplier/tests/](file:///d:/projects/SCOF_V1/SCOF/services/agents/supplier/tests/).

2. **Transportation Agent Microservice (`services/agents/transportation/`)**:
   - FastAPI microservice running on port `8014` with endpoints `POST /analyze`, `GET /health`, and `GET /.well-known/agent.json`.
   - Four-stage pipeline: `TransportDataAccess` -> `TransportFeatureBuilder` -> `TransportEnsemble` -> `ClaimBuilder`.
   - **Machine Learning & Route Models**:
     - [`delay_predictor.py`](file:///d:/projects/SCOF_V1/SCOF/services/agents/transportation/src/models/delay_predictor.py): `GradientBoostingRegressor` with residual calibration intervals for transit delay forecasting.
     - [`route_scorer.py`](file:///d:/projects/SCOF_V1/SCOF/services/agents/transportation/src/models/route_scorer.py): `RouteScorerInitializer` + `RouteScorerInference` evaluating carrier historical on-time rates and route risk scores.
     - [`ensemble.py`](file:///d:/projects/SCOF_V1/SCOF/services/agents/transportation/src/models/ensemble.py): Weighted combination of delay prediction and route score.
   - **Deterministic Alternate Route Recommendation**: Multi-criteria weighted normalization evaluating reliability (40%), normalized transit time (30%), normalized cost (20%), and hop count (10%).
   - **Data Access & Fallbacks**: Dual PostgreSQL shipment metric store and Neo4j route network query client ([`data_access.py`](file:///d:/projects/SCOF_V1/SCOF/services/agents/transportation/src/data_access.py)).
   - **Declared MCP Tools**: `query_route_network`, `estimate_delay`, `read_carrier_performance`.
   - Standalone unit test suite in [services/agents/transportation/tests/](file:///d:/projects/SCOF_V1/SCOF/services/agents/transportation/tests/).

3. **Domain Profile & Shared Contracts Integration**:
   - Updated [profiles/mvp-electronics/agents.yaml](file:///d:/projects/SCOF_V1/SCOF/profiles/mvp-electronics/agents.yaml) with active configurations, ensemble weights, confidence thresholds, and MCP tool bindings for `supplier-agent` and `transport-agent`.
   - Enforced strict contract adherence: raw confidence is **never clamped or inflated**, and `low_confidence=True` is flagged when confidence falls below the agent's confidence floor.
   - Traceable evidence items with SHA-256 query hashes and entity reference IDs.

4. **Infrastructure & Automated Verification Suite**:
   - Updated [docker-compose.yml](file:///d:/projects/SCOF_V1/SCOF/docker-compose.yml) to add `supplier-agent` (port 8013) and `transport-agent` (port 8014).
   - Created versioned model artifact storage directories: [models/supplier/](file:///d:/projects/SCOF_V1/SCOF/models/supplier/) and [models/transportation/](file:///d:/projects/SCOF_V1/SCOF/models/transportation/).
   - Added `verify-d4` target to [Makefile](file:///d:/projects/SCOF_V1/SCOF/Makefile).
   - Created automated verification script [`scripts/verify_d4.py`](file:///d:/projects/SCOF_V1/SCOF/scripts/verify_d4.py) validating direct instantiation, Agent Card compliance, claim schemas, evidence traceability, confidence integrity, deterministic alternate ranking, and repeatable execution.

---

## Verification & Test Results

### 1. Pytest Test Suite Execution

Executed `pytest` across Supplier Agent and Transportation Agent test suites:

```bash
pytest -c services/agents/supplier/pyproject.toml services/agents/supplier/tests
pytest -c services/agents/transportation/pyproject.toml services/agents/transportation/tests
```

**Output**:
```
============================= test session starts =============================
platform win32 -- Python 3.12.2, pytest-9.1.1, pluggy-1.6.0
rootdir: D:\projects\SCOF_V1\SCOF\services\agents\supplier
configfile: pyproject.toml
collected 14 items

services\agents\supplier\tests\test_reliability_scorer.py ...            [ 21%]
services\agents\supplier\tests\test_supplier_agent.py .....              [ 57%]
services\agents\supplier\tests\test_supplier_data_access.py ....         [ 85%]
services\agents\supplier\tests\test_supplier_features.py ..              [100%]

============================= 14 passed in 58.93s =============================

============================= test session starts =============================
platform win32 -- Python 3.12.2, pytest-9.1.1, pluggy-1.6.0
rootdir: D:\projects\SCOF_V1\SCOF\services\agents\transportation
configfile: pyproject.toml
collected 13 items

services\agents\transportation\tests\test_delay_predictor.py ...         [ 23%]
services\agents\transportation\tests\test_transport_agent.py .....       [ 61%]
services\agents\transportation\tests\test_transport_data_access.py ...   [ 84%]
services\agents\transportation\tests\test_transport_features.py ..       [100%]

============================= 13 passed in 50.65s =============================
```

---

### 2. Automated Verification Suite Execution

Executed `python scripts/verify_d4.py` (or `make verify-d4`):

```bash
python scripts/verify_d4.py
```

**Output**:
```
==================================================
   SCOF Deliverable D4 Verification Suite
==================================================
Testing supplier-agent via direct instantiation...
PASS: supplier-agent Agent Card validation.
PASS: supplier-agent deterministic alternate ranking validation.
PASS: supplier-agent Baseline Structured Claim validation.
PASS: supplier-agent Disruption Structured Claim validation.
PASS: supplier-agent Determinism validation.
Testing transport-agent via direct instantiation...
PASS: transport-agent Agent Card validation.
PASS: transport-agent deterministic alternate ranking validation.
PASS: transport-agent Baseline Structured Claim validation.
PASS: transport-agent Disruption Structured Claim validation.
PASS: transport-agent Determinism validation.

==================================================
   ALL D4 VERIFICATION CHECKS PASSED (100%)
==================================================
```

---

## Step-by-Step Execution & Manual Testing Guide

> [!NOTE]
> On Windows PowerShell, `curl` is an alias for `Invoke-WebRequest`. Use `curl.exe` or `Invoke-RestMethod` to bypass interactive prompts and view JSON outputs directly.

### Step 1: Start Agent Microservices via Docker Compose
Start all containers including the Supplier Agent and Transportation Agent microservices:
```bash
docker compose up -d --build
```

Verify that the agent containers are running and healthy:
```bash
docker compose ps
```
Confirm `supplier-agent` (port 8013) and `transport-agent` (port 8014) are active.

---

### Step 2: Health & Discovery Endpoint Verification

#### A. Health Check Endpoints
Verify rich health status output from each agent service:

```powershell
# In PowerShell (use curl.exe or Invoke-RestMethod):
curl.exe http://localhost:8013/health
curl.exe http://localhost:8014/health

# Or via PowerShell Invoke-RestMethod:
Invoke-RestMethod http://localhost:8013/health
Invoke-RestMethod http://localhost:8014/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "agent_id": "supplier-agent",
  "profile_loaded": true,
  "db_connected": true,
  "neo4j_connected": true,
  "model_loaded": true,
  "model_version": "1.0.0",
  "uptime_seconds": 18.2
}
```

#### B. A2A Agent Card Discovery Endpoints
Verify self-describing Agent Cards published per A2A specification:

```powershell
# Supplier Agent Card
curl.exe http://localhost:8013/.well-known/agent.json

# Transportation Agent Card
curl.exe http://localhost:8014/.well-known/agent.json
```

---

### Step 3: Analysis Pipeline Manual Invocation

#### A. Supplier Intelligence Agent Analysis Request (`POST /analyze`)
Send a scenario request to the Supplier Agent:

```powershell
# PowerShell / CMD:
curl.exe -X POST http://localhost:8013/analyze -H "Content-Type: application/json" -d '{\"scenario_id\": \"scen-electronics-01\", \"run_id\": \"run-01\", \"supplier_ids\": [\"sup-01\", \"sup-02\"]}'

# Or via PowerShell Invoke-RestMethod:
Invoke-RestMethod -Uri http://localhost:8013/analyze -Method POST -ContentType "application/json" -Body '{"scenario_id": "scen-electronics-01", "run_id": "run-01", "supplier_ids": ["sup-01", "sup-02"]}'
```

#### B. Transportation Agent Analysis Request (`POST /analyze`)
Send a scenario request to the Transportation Agent:

```powershell
# PowerShell / CMD:
curl.exe -X POST http://localhost:8014/analyze -H "Content-Type: application/json" -d '{\"scenario_id\": \"scen-electronics-01\", \"run_id\": \"run-01\", \"route_ids\": [\"route-01\", \"route-02\"]}'

# Or via PowerShell Invoke-RestMethod:
Invoke-RestMethod -Uri http://localhost:8014/analyze -Method POST -ContentType "application/json" -Body '{"scenario_id": "scen-electronics-01", "run_id": "run-01", "route_ids": ["route-01", "route-02"]}'
```

---

## Direct Agent Claim Inspection & Audit Checklist

When reviewing returned `StructuredClaim` JSON responses, verify the following contracts:

1. **Reasoning Rationale**: Assert `reasoning` field contains concise rationale (distinct from raw evidence).
2. **Confidence Integrity**: Assert `0.0 <= confidence <= 1.0`. Verify confidence is never clamped to `confidence_floor`. If `confidence < confidence_floor`, verify `low_confidence == true`.
3. **Traceable Evidence**: Assert each `evidence[]` item contains a non-empty `reference_id` (e.g. `supplier_delivery_history:scen-01`, `route_shipment_history:scen-01`) and valid SHA-256 `query_hash` for SQL and Cypher queries.
4. **Disruption Prioritization**: Assert priority is set to `HIGH` or `CRITICAL` when active supplier delays, port closures, or transit disruptions are detected.
5. **Deterministic Alternate Rankings**: Assert alternate suppliers and alternate routes are ranked with composite multi-criteria scoring ensuring deterministic ordering across identical seeds.

---

## File Changes Summary

- [NEW] [agents.yaml](file:///d:/projects/SCOF_V1/SCOF/profiles/mvp-electronics/agents.yaml) (updated with D4 agent configs)
- [NEW] [docker-compose.yml](file:///d:/projects/SCOF_V1/SCOF/docker-compose.yml) (updated with D4 agent containers)
- [NEW] [Makefile](file:///d:/projects/SCOF_V1/SCOF/Makefile) (updated with verify-d4 target)
- [NEW] [verify_d4.py](file:///d:/projects/SCOF_V1/SCOF/scripts/verify_d4.py)
- [NEW] [pyproject.toml (supplier)](file:///d:/projects/SCOF_V1/SCOF/services/agents/supplier/pyproject.toml)
- [NEW] [Dockerfile (supplier)](file:///d:/projects/SCOF_V1/SCOF/services/agents/supplier/Dockerfile)
- [NEW] [config.py (supplier)](file:///d:/projects/SCOF_V1/SCOF/services/agents/supplier/src/config.py)
- [NEW] [data_access.py (supplier)](file:///d:/projects/SCOF_V1/SCOF/services/agents/supplier/src/data_access.py)
- [NEW] [features.py (supplier)](file:///d:/projects/SCOF_V1/SCOF/services/agents/supplier/src/features.py)
- [NEW] [reliability_scorer.py](file:///d:/projects/SCOF_V1/SCOF/services/agents/supplier/src/models/reliability_scorer.py)
- [NEW] [rule_scorer.py (supplier)](file:///d:/projects/SCOF_V1/SCOF/services/agents/supplier/src/models/rule_scorer.py)
- [NEW] [ensemble.py (supplier)](file:///d:/projects/SCOF_V1/SCOF/services/agents/supplier/src/models/ensemble.py)
- [NEW] [tools.py (supplier MCP)](file:///d:/projects/SCOF_V1/SCOF/services/agents/supplier/src/mcp/tools.py)
- [NEW] [agent.py (supplier)](file:///d:/projects/SCOF_V1/SCOF/services/agents/supplier/src/agent.py)
- [NEW] [main.py (supplier)](file:///d:/projects/SCOF_V1/SCOF/services/agents/supplier/src/main.py)
- [NEW] [test_supplier_agent.py](file:///d:/projects/SCOF_V1/SCOF/services/agents/supplier/tests/test_supplier_agent.py)
- [NEW] [test_reliability_scorer.py](file:///d:/projects/SCOF_V1/SCOF/services/agents/supplier/tests/test_reliability_scorer.py)
- [NEW] [test_supplier_data_access.py](file:///d:/projects/SCOF_V1/SCOF/services/agents/supplier/tests/test_supplier_data_access.py)
- [NEW] [test_supplier_features.py](file:///d:/projects/SCOF_V1/SCOF/services/agents/supplier/tests/test_supplier_features.py)
- [NEW] [pyproject.toml (transportation)](file:///d:/projects/SCOF_V1/SCOF/services/agents/transportation/pyproject.toml)
- [NEW] [Dockerfile (transportation)](file:///d:/projects/SCOF_V1/SCOF/services/agents/transportation/Dockerfile)
- [NEW] [config.py (transportation)](file:///d:/projects/SCOF_V1/SCOF/services/agents/transportation/src/config.py)
- [NEW] [data_access.py (transportation)](file:///d:/projects/SCOF_V1/SCOF/services/agents/transportation/src/data_access.py)
- [NEW] [features.py (transportation)](file:///d:/projects/SCOF_V1/SCOF/services/agents/transportation/src/features.py)
- [NEW] [delay_predictor.py](file:///d:/projects/SCOF_V1/SCOF/services/agents/transportation/src/models/delay_predictor.py)
- [NEW] [route_scorer.py](file:///d:/projects/SCOF_V1/SCOF/services/agents/transportation/src/models/route_scorer.py)
- [NEW] [ensemble.py (transportation)](file:///d:/projects/SCOF_V1/SCOF/services/agents/transportation/src/models/ensemble.py)
- [NEW] [tools.py (transportation MCP)](file:///d:/projects/SCOF_V1/SCOF/services/agents/transportation/src/mcp/tools.py)
- [NEW] [agent.py (transportation)](file:///d:/projects/SCOF_V1/SCOF/services/agents/transportation/src/agent.py)
- [NEW] [main.py (transportation)](file:///d:/projects/SCOF_V1/SCOF/services/agents/transportation/src/main.py)
- [NEW] [test_transport_agent.py](file:///d:/projects/SCOF_V1/SCOF/services/agents/transportation/tests/test_transport_agent.py)
- [NEW] [test_delay_predictor.py](file:///d:/projects/SCOF_V1/SCOF/services/agents/transportation/tests/test_delay_predictor.py)
- [NEW] [test_transport_data_access.py](file:///d:/projects/SCOF_V1/SCOF/services/agents/transportation/tests/test_transport_data_access.py)
- [NEW] [test_transport_features.py](file:///d:/projects/SCOF_V1/SCOF/services/agents/transportation/tests/test_transport_features.py)
- [NEW] [supplier_agent_design.md](file:///d:/projects/SCOF_V1/SCOF/docs/deliverables/D04_supplier_transport_agents/supplier_agent_design.md)
- [NEW] [transport_agent_design.md](file:///d:/projects/SCOF_V1/SCOF/docs/deliverables/D04_supplier_transport_agents/transport_agent_design.md)
- [NEW] [model_evaluation.md](file:///d:/projects/SCOF_V1/SCOF/docs/deliverables/D04_supplier_transport_agents/model_evaluation.md)
- [NEW] [acceptance_evidence.md](file:///d:/projects/SCOF_V1/SCOF/docs/deliverables/D04_supplier_transport_agents/acceptance_evidence.md)
- [NEW] [walkthrough.md](file:///d:/projects/SCOF_V1/SCOF/docs/deliverables/D04_supplier_transport_agents/walkthrough.md)
