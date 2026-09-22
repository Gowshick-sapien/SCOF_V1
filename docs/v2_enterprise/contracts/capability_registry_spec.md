# Dynamic Capability Registry Specification (V2 Contract)

## 1. Overview & Protocol Standard

This document establishes the formal contract for the **Dynamic Capability Registry** in SCOF V2.

The registry decouples cognitive agent reasoning from static endpoint maintenance. Internal service providers (D2 Knowledge Fabric, Analytic Services, Twin Substrate) register their computational interfaces via declarative **Capability Cards**. During runtime orchestration, the registry matches task intents against registered capabilities and synthesizes bounded Model Context Protocol (MCP) tool schemas dynamically.

---

## 2. Pydantic Schemas

```python
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field

class AccessPolicy(BaseModel):
    required_role: Literal["operational_specialist", "consensus_engine", "admin", "system"]
    state_isolation_level: Literal["layer_1_readonly", "layer_2_readonly", "layer_3_ephemeral"]
    requires_hitl: bool = Field(False, description="Whether execution requires human confirmation")
    rate_limit_per_minute: int = Field(120, description="Maximum calls per minute per caller")

class CapabilityMetadata(BaseModel):
    display_name: str
    description: str
    domain_scope: List[str] = Field(..., description="Target business domains, e.g. ['inventory', 'network']")
    sla_latency_ms: int = Field(..., description="Target latency SLA in milliseconds")
    owner_subsystem: Literal["d2_fabric", "analytic_services", "digital_twin_service", "external_adapter"]

class CapabilityCard(BaseModel):
    capability_id: str = Field(..., description="Unique dotted identifier, e.g. 'twin.simulation.counterfactual'")
    version: str = Field("2.0.0", description="SemVer capability version")
    operational_class: Literal["Class_A", "Class_B", "Class_C"]
    metadata: CapabilityMetadata
    semantic_intents: List[str] = Field(
        ...,
        description="Natural language phrases used to compute vector embeddings for dynamic intent matching"
    )
    access_policy: AccessPolicy
    input_schema: Dict[str, Any] = Field(..., description="JSON Schema for required invocation parameters")
    output_schema: Dict[str, Any] = Field(..., description="JSON Schema for output response payload")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CapabilityRegistrationRequest(BaseModel):
    capability: CapabilityCard
    provider_auth_token: str

class SemanticMatchRequest(BaseModel):
    task_description: str
    caller_agent_id: str
    domain_filters: Optional[List[str]] = None
    max_capabilities: int = Field(3, ge=1, le=5)
    minimum_similarity_score: float = Field(0.65, ge=0.0, le=1.0)

class BoundMCPTool(BaseModel):
    tool_name: str
    description: str
    input_schema: Dict[str, Any]
    capability_id: str
    operational_class: str
    timeout_ms: int

class SemanticMatchResponse(BaseModel):
    query_id: str
    matched_capabilities: List[CapabilityCard]
    bound_mcp_tools: List[BoundMCPTool]
    resolution_time_ms: float
```

---

## 3. Core Capability Card Definitions

### 3.1 D2 Direct Read-Only Capability (Class A)
```yaml
capability_id: "d2.fabric.inventory_position"
version: "2.0.0"
operational_class: "Class_A"
metadata:
  display_name: "Query Inventory Position"
  description: "Retrieves authoritative Day-0 or current stock on hand across stores and DCs."
  domain_scope: ["inventory", "network"]
  sla_latency_ms: 30
  owner_subsystem: "d2_fabric"
semantic_intents:
  - "check stock level for sku"
  - "retrieve warehouse inventory"
  - "how many units on hand"
  - "store inventory position"
access_policy:
  required_role: "operational_specialist"
  state_isolation_level: "layer_2_readonly"
  requires_hitl: false
  rate_limit_per_minute: 600
input_schema:
  type: "object"
  required: ["facility_id", "sku_id"]
  properties:
    facility_id: { type: "string" }
    sku_id: { type: "string" }
output_schema:
  type: "object"
  required: ["quantity_on_hand", "reorder_point", "safety_stock"]
  properties:
    quantity_on_hand: { type: "integer" }
    reorder_point: { type: "integer" }
    safety_stock: { type: "integer" }
```

### 3.2 Bounded Neo4j Topology Traversal (Class A)
```yaml
capability_id: "d2.graph.upstream_supply_path"
version: "2.0.0"
operational_class: "Class_A"
metadata:
  display_name: "Trace Upstream Supply Path"
  description: "Executes bounded graph traversal in Neo4j to identify supplier-to-store paths."
  domain_scope: ["sourcing", "network", "inventory"]
  sla_latency_ms: 50
  owner_subsystem: "d2_fabric"
semantic_intents:
  - "trace supply path for sku"
  - "find primary supplier and intermediate dc"
  - "upstream dependency network"
access_policy:
  required_role: "operational_specialist"
  state_isolation_level: "layer_2_readonly"
  requires_hitl: false
  rate_limit_per_minute: 300
input_schema:
  type: "object"
  required: ["sku_id", "store_id"]
  properties:
    sku_id: { type: "string" }
    store_id: { type: "string" }
    max_depth: { type: "integer", default: 3, maximum: 4 }
output_schema:
  type: "object"
  required: ["path_nodes", "total_transit_days"]
  properties:
    path_nodes: { type: "array", items: { type: "string" } }
    total_transit_days: { type: "number" }
```

### 3.3 Counterfactual Scenario Simulation (Class C)
```yaml
capability_id: "twin.simulation.counterfactual"
version: "2.0.0"
operational_class: "Class_C"
metadata:
  display_name: "Evaluate Counterfactual Intervention"
  description: "Forks scenario to simulate alternate operational action and output state deltas."
  domain_scope: ["inventory", "transportation", "sourcing"]
  sla_latency_ms: 400
  owner_subsystem: "digital_twin_service"
semantic_intents:
  - "simulate alternate supplier sourcing"
  - "evaluate expedited air freight"
  - "what if we rebalance inventory"
  - "compare intervention options"
access_policy:
  required_role: "operational_specialist"
  state_isolation_level: "layer_3_ephemeral"
  requires_hitl: false
  rate_limit_per_minute: 60
input_schema:
  type: "object"
  required: ["scenario_id", "candidate_interventions"]
  properties:
    scenario_id: { type: "string" }
    candidate_interventions: { type: "array", items: { type: "object" } }
output_schema:
  type: "object"
  required: ["fill_rate_delta", "cost_delta_usd", "revenue_preservation_usd"]
  properties:
    fill_rate_delta: { type: "number" }
    cost_delta_usd: { type: "number" }
    revenue_preservation_usd: { type: "number" }
```

---

## 4. Integration Invariants

1. **Schema Validation:** Cards must pass strict JSON Schema / Pydantic validation upon registration. Invalid cards are rejected.
2. **Sub-25ms Semantic Discovery:** Semantic intent indexing is backed by pgvector (384-dimensional cosine similarity). Discovery must return matching tools in $< 25\text{ ms}$.
3. **Bounded Tool Cardinality:** The registry enforces that no agent session receives more than 5 tools concurrently, preserving prompt context integrity.
