# Digital Twin Service API Specification (V2 Contract)

## 1. Overview & Protocol Standard

This document establishes the formal API contract for the **SCOF V2 Digital Twin Service**.

All request and response payloads adhere to strict Pydantic v2 / OpenAPI 3.1 schema definitions. The service exposes both high-performance Python in-process bindings (for local orchestration) and asynchronous REST/JSON endpoints (for microservice deployment).

---

## 2. Core Data Models (Pydantic Schemas)

### 2.1 Scenario Lifecycle Models
```python
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field, UUID4

class ScenarioContext(BaseModel):
    scenario_id: str = Field(..., description="Unique scenario identifier (e.g. 'scen-disruption-sup-042')")
    baseline_id: str = Field("master_day0_baseline", description="Underlying Layer 2 baseline state ID")
    sim_run_id: str = Field(..., description="Unique execution run identifier")
    random_seed: int = Field(42, description="Random seed for deterministic replay")
    status: Literal["created", "running", "paused", "completed", "failed"] = Field("created")
    current_sim_step: int = Field(0, description="Current discrete-event simulation step")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    state_version: int = Field(1, description="Monotonically increasing state version")
    disabled_entities: Dict[str, List[str]] = Field(
        default_factory=lambda: {"nodes": [], "edges": []},
        description="Topological masks applied over Neo4j baseline"
    )
    parameter_overrides: Dict[str, Any] = Field(
        default_factory=dict,
        description="In-memory scenario state overrides"
    )
    provenance_hash: str = Field(..., description="Cryptographic SHA-256 state digest")

class CreateScenarioRequest(BaseModel):
    baseline_id: str = "master_day0_baseline"
    scenario_type: Literal["supplier_delay", "asset_downtime", "route_closure", "demand_shock"]
    parameters: Dict[str, Any]
    seed: int = 42

class ForkScenarioRequest(BaseModel):
    branch_name: str = Field(..., description="Name of the counterfactual branch (e.g. 'branch_air_freight')")
    candidate_interventions: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
```

### 2.2 Simulation & Stepping Models
```python
class DisruptionEvent(BaseModel):
    disruption_id: str = Field(..., description="Unique disruption identifier")
    disruption_type: str = Field(...)
    target_entity_type: Literal["supplier", "facility", "asset", "transport_lane", "sku"]
    target_entity_id: str = Field(...)
    parameters: Dict[str, Any]
    scheduled_step: int = Field(..., ge=0)

class SimulateRequest(BaseModel):
    horizon_steps: int = Field(..., ge=1, le=100, description="Number of discrete steps to advance")
    disruptions: List[DisruptionEvent] = Field(default_factory=list)

class SimulationResult(BaseModel):
    scenario_id: str
    sim_run_id: str
    steps_advanced: int
    final_step: int
    stockouts_count: int
    fill_rate_percentage: float
    revenue_at_risk_usd: float
    total_spoilage_cost_usd: float
    invariants_passed: bool
    state_hash: str

class StepRequest(BaseModel):
    step_delta: int = Field(1, ge=1, le=10)

class StepResult(BaseModel):
    scenario_id: str
    current_step: int
    events_processed: int
    active_stockouts: int
    invariants_passed: bool
```

### 2.3 Counterfactual Evaluation Models
```python
class InterventionAction(BaseModel):
    action_id: str
    action_type: Literal["reroute_freight", "alternate_supplier", "reallocate_inventory", "expedite_po"]
    target_entity_id: str
    parameters: Dict[str, Any]
    projected_cost_usd: float

class CounterfactualEvaluationRequest(BaseModel):
    branch_name: str
    interventions: List[InterventionAction]

class CounterfactualDelta(BaseModel):
    branch_scenario_id: str
    parent_scenario_id: str
    fill_rate_delta: float
    stockout_delta_units: int
    cost_delta_usd: float
    revenue_preservation_usd: float
    net_economic_benefit_usd: float
    invariant_violations: List[str]
```

### 2.4 Evidence Pack & Provenance Models
```python
class StateSnapshotItem(BaseModel):
    entity_type: str
    entity_id: str
    metric: str
    value: Any
    source_table: str

class DeterministicEvidencePack(BaseModel):
    evidence_pack_id: str
    scenario_id: str
    sim_run_id: str
    timestamp: datetime
    provenance_hash: str
    state_snapshots: List[StateSnapshotItem]
    causal_trace: List[str]
```

---

## 3. REST API Endpoint Specifications

### 3.1 Scenario Lifecycle Management
* **`POST /api/v2/twin/scenarios`**
  - **Description:** Initializes a new isolated Layer 3 execution sandbox.
  - **Request:** `CreateScenarioRequest`
  - **Response:** `ScenarioContext` (HTTP 201)
* **`POST /api/v2/twin/scenarios/{scenario_id}/fork`**
  - **Description:** Forks an active scenario into an isolated counterfactual sandbox branch.
  - **Request:** `ForkScenarioRequest`
  - **Response:** `ScenarioContext` (HTTP 201)
* **`GET /api/v2/twin/scenarios/{scenario_id}`**
  - **Description:** Retrieves current lifecycle and state status of a scenario.
  - **Response:** `ScenarioContext` (HTTP 200)
* **`DELETE /api/v2/twin/scenarios/{scenario_id}`**
  - **Description:** Tears down ephemeral Layer 3 sandbox state and releases memory overlays.
  - **Response:** `{"status": "closed", "scenario_id": str}` (HTTP 200)

### 3.2 Simulation Execution
* **`POST /api/v2/twin/scenarios/{scenario_id}/simulate`**
  - **Description:** Runs forward propagation across specified horizon.
  - **Request:** `SimulateRequest`
  - **Response:** `SimulationResult` (HTTP 200)
* **`POST /api/v2/twin/scenarios/{scenario_id}/advance`**
  - **Description:** Advances the discrete simulation clock by $k$ discrete steps.
  - **Request:** `StepRequest`
  - **Response:** `StepResult` (HTTP 200)
* **`POST /api/v2/twin/scenarios/{scenario_id}/counterfactual`**
  - **Description:** Applies candidate interventions in an isolated sandbox branch and computes state deltas.
  - **Request:** `CounterfactualEvaluationRequest`
  - **Response:** `CounterfactualDelta` (HTTP 200)

### 3.3 State Inspection & Evidence
* **`GET /api/v2/twin/scenarios/{scenario_id}/state/{entity_type}/{entity_id}`**
  - **Description:** Retrieves authoritative runtime state for an entity inside the scenario sandbox.
  - **Response:** `{"entity_id": str, "runtime_state": dict}` (HTTP 200)
* **`POST /api/v2/twin/scenarios/{scenario_id}/actions`**
  - **Description:** Applies an arbitrated, CD²F-approved action to the scenario runtime state.
  - **Request:** `{"decision_id": str, "action": InterventionAction}`
  - **Response:** `{"receipt_id": str, "status": "committed", "new_state_version": int}` (HTTP 200)
* **`GET /api/v2/twin/scenarios/{scenario_id}/evidence/{claim_id}`**
  - **Description:** Generates a deterministic evidence pack supporting an agent claim.
  - **Response:** `DeterministicEvidencePack` (HTTP 200)

---

## 4. SLA & Performance Standards

* **In-Memory Operations:** `get_operational_state`, `advance` execute in $< 10\text{ ms}$.
* **Forward Propagation:** 30-step forward simulation of retail network executes in $< 250\text{ ms}$.
* **Counterfactual Fork & Diff:** Evaluates branch interventions in $< 400\text{ ms}$.
* **Concurrency SLA:** Priority Queue dispatches P0 within $5\text{ ms}$ and P1 within $20\text{ ms}$.
