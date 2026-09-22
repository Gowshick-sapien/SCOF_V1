# Deliverable D05 -- LangGraph Orchestration & State Graph Design

## 1. Executive Overview

This document specifies the architecture and technical design of the **LangGraph Orchestration Engine** for Deliverable D05. The Coordinator agent (`services/coordinator/`) uses LangGraph (v0.2+) to manage state transitions, parallel specialist agent dispatch, failure handling, and claim bundle aggregation.

The architecture strictly decouples:
- **`CoordinatorRuntime`**: Persistent service-level state (cached agent registry, compiled graph runnable, operational telemetry metrics).
- **`CoordinatorExecutionState`**: Ephemeral, scenario-scoped LangGraph state passed through the nodes during a single orchestration run.

---

## 2. State Schema Architecture

### 2.1 Ephemeral Execution State (`CoordinatorExecutionState`)

The state schema passed between LangGraph nodes is defined as a typed dictionary conforming to LangGraph state requirements:

```python
from typing import Any, Dict, List, Optional, TypedDict
from scof_shared.schemas.agent_card import AgentCard
from scof_shared.schemas.claim_bundle import ClaimBundle
from scof_shared.schemas.scenario_context import ScenarioContext
from scof_shared.schemas.structured_claim import StructuredClaim


class CoordinatorExecutionState(TypedDict):
    """Ephemeral state scoped to a single orchestration execution run."""

    # Input Scenario Context and Provenance
    scenario_context: ScenarioContext
    trace_id: str
    bundle_id: str
    profile_name: str
    profile_version: str

    # Agent Target Resolution
    target_agent_cards: List[AgentCard]

    # Parallel Dispatch Outputs
    raw_claims: Dict[str, StructuredClaim]
    failed_agents: Dict[str, str]
    agent_latencies_ms: Dict[str, float]

    # Final Aggregation Output
    claim_bundle: Optional[ClaimBundle]

    # Execution Observability Log & Timing
    execution_log: List[str]
    status: str  # "INITIALIZED", "RESOLVED", "DISPATCHED", "COMPLETED", "FAILED"
    start_time: float
    end_time: float
```

### 2.2 Persistent Service Runtime (`CoordinatorRuntime`)

The persistent runtime maintains thread-safe shared resources across multiple orchestration requests:

```python
from dataclasses import dataclass, field
from datetime import datetime, timezone
import time
from typing import Any, Dict, Optional
from scof_shared.protocols.a2a_client import A2AClient
from scof_shared.protocols.a2a_registry import A2ARegistry
from scof_shared.profile.loader import DomainProfile


@dataclass
class CoordinatorMetrics:
    """Coordinator operational telemetry metrics."""
    orchestrations_executed: int = 0
    orchestrations_successful: int = 0
    orchestrations_partial: int = 0
    orchestrations_failed: int = 0
    total_orchestration_latency_ms: float = 0.0
    last_discovery_duration_ms: float = 0.0
    start_time: float = field(default_factory=time.time)

    @property
    def average_latency_ms(self) -> float:
        if self.orchestrations_executed == 0:
            return 0.0
        return round(self.total_orchestration_latency_ms / self.orchestrations_executed, 2)


class CoordinatorRuntime:
    """Thread-safe persistent runtime for the Coordinator service."""

    def __init__(self, profile_path: str):
        self.profile_path = profile_path
        self.profile: Optional[DomainProfile] = None
        self.registry: A2ARegistry = A2ARegistry()
        self.a2a_client: A2AClient = A2AClient()
        self.metrics: CoordinatorMetrics = CoordinatorMetrics()
        self.compiled_graph: Optional[Any] = None
        self.graph_metadata: Dict[str, Any] = {}
```

---

## 3. StateGraph Topology & Node Execution Contracts

```
 +-------------------------+
 |          START          |
 +-------------------------+
              |
              v
 +-------------------------+
 |  node_resolve_targets   |  <--- Matches ScenarioContext against cached A2ARegistry
 +-------------------------+
              |
      [Targets Found?]
       /             \
    (Yes)            (No / Empty)
     /                 \
    v                   v
 +-------------------+  +-------------------------+
 | node_dispatch_    |  |   node_collect_empty    |
 | parallel          |  +-------------------------+
 +-------------------+             |
          |                        |
          v                        |
 +-------------------+             |
 | node_collect_     | <-----------+
 | bundle            |
 +-------------------+
          |
          v
 +-------------------------+
 |           END           |
 +-------------------------+
```

### 3.1 Node Definitions

#### Node 1: `node_resolve_targets(state: CoordinatorExecutionState) -> Dict[str, Any]`
- **Purpose**: Evaluates the input `ScenarioContext` against the active `A2ARegistry` to determine which specialist agents should receive delegation.
- **Matching Logic**:
  1. Inspects `ScenarioContext.disruption_type` (e.g. `supplier_delay`, `transport_failure`, `demand_spike`, `adverse_weather`).
  2. Queries `A2ARegistry.find_by_context(disruption_type)`.
  3. If context matches specific agents, includes them; if baseline/cross-functional or no specific filter matches, defaults to all healthy registered agents to ensure comprehensive supply chain impact visibility.
  4. Appends resolution entries to `execution_log`.
- **Outputs**: `target_agent_cards`, `status = "RESOLVED"`.

#### Node 2: `node_dispatch_parallel(state: CoordinatorExecutionState) -> Dict[str, Any]`
- **Purpose**: Concurrently delegates the `ScenarioContext` to all resolved `target_agent_cards` via A2A HTTP calls.
- **Concurrency & Throttling**:
  - Uses `asyncio.Semaphore(MAX_CONCURRENT_DISPATCH)` (default 8) inside `A2AClient.delegate_analyze_parallel`.
  - Enforces separated timeouts: `CONNECT_TIMEOUT = 2.0s`, `READ_TIMEOUT = 8.0s`.
  - Applies status-code-aware retry policy (skips 4xx, retries 5xx/network errors with exponential backoff up to 2 retries).
  - Propagates headers: `X-Scenario-ID`, `X-Bundle-ID`, `X-Trace-ID`, `X-Profile-Version`.
- **Health Telemetry Update**:
  - For each agent response (success or failure), updates `A2ARegistry` health metrics (`health_status`, `consecutive_failures`, `average_latency_ms`).
- **Outputs**: `raw_claims`, `failed_agents`, `agent_latencies_ms`, `status = "DISPATCHED"`.

#### Node 3: `node_collect_bundle(state: CoordinatorExecutionState) -> Dict[str, Any]`
- **Purpose**: Validates individual claims and constructs the final immutable `ClaimBundle`.
- **Bundle Assembly**:
  - Calculates `total_latency_ms = (time.time() - state["start_time"]) * 1000`.
  - Determines bundle status:
    - `COMPLETE`: 100% of target agents returned valid `StructuredClaim` objects.
    - `PARTIAL`: At least 1 agent succeeded, but 1 or more agents failed or timed out.
    - `FAILED`: 0 agents returned valid claims.
  - Instantiates immutable `ClaimBundle` with `profile_name` and `profile_version`.
- **Outputs**: `claim_bundle`, `end_time`, `status = "COMPLETED"`.

---

## 4. Conditional Edge & Error Handling Semantics

1. **Zero Discovered/Target Agents**:
   - If `target_agent_cards` is empty, conditional edge bypasses `node_dispatch_parallel` directly to `node_collect_bundle`, producing a `ClaimBundle` with `status = "FAILED"` and `failed_agents = {"coordinator": "No active specialist agents discovered or matched"}`.
2. **Partial Agent Failure**:
   - If one specialist agent times out or returns HTTP 500, the remaining agents complete normally. The bundle captures all successful claims, logs the failure in `failed_agents`, and marks status `PARTIAL`.
3. **Graph Execution Exceptions**:
   - Unhandled exceptions inside any node are caught by the top-level orchestrator wrapper, updating coordinator metrics and returning a diagnostic fallback claim bundle without crashing the coordinator service.

---

## 5. Graph Topology Inspection & Determinism Hashing

The Coordinator compiles the graph and computes a deterministic SHA256 hash of the graph structure at initialization.

### `GET /graph` Response Contract:

```json
{
  "graph_version": "1.0.0",
  "compiled_graph_hash": "a8f5c3b1e94d2f071683...",
  "node_count": 3,
  "edge_count": 3,
  "nodes": [
    {
      "name": "node_resolve_targets",
      "description": "Matches ScenarioContext against cached A2A registry"
    },
    {
      "name": "node_dispatch_parallel",
      "description": "Bounded parallel dispatch via A2A HTTP client under semaphore"
    },
    {
      "name": "node_collect_bundle",
      "description": "Aggregates claims and constructs immutable ClaimBundle"
    }
  ],
  "edges": [
    {"source": "__start__", "target": "node_resolve_targets"},
    {"source": "node_resolve_targets", "target": "node_dispatch_parallel", "conditional": true},
    {"source": "node_dispatch_parallel", "target": "node_collect_bundle"},
    {"source": "node_collect_bundle", "target": "__end__"}
  ]
}
```

---

## 6. Consensus Boundary Invariant (Strict D05/D06 Separation)

Per SRS FR-5.4, the LangGraph Coordinator for D05 **strictly gathers raw claim bundles**.
- **No Weighting**: The Coordinator does not weight claims by confidence or risk.
- **No Majority Voting**: The Coordinator does not resolve conflicting recommendations.
- **No Agreement Analysis**: No agreement metrics or unanimous priority checks exist in D05.
- **Contract Boundary**: D05 produces `ClaimBundle`; D06 consumes `ClaimBundle` to produce `ConsensusBundle`.
