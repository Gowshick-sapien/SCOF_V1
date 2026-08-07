# Deliverable D05 Implementation Plan -- Agent Orchestration & Protocol Layer

## Goal Description

Deliverable D05 establishes the **Agent Orchestration and Protocol Layer** of the SCOF platform. It wires the four independent specialist AI agents built in D03 and D04 ([Demand Forecast Agent](file:///d:/projects/SCOF_V1/SCOF/services/agents/demand/), [Inventory Agent](file:///d:/projects/SCOF_V1/SCOF/services/agents/inventory/), [Supplier Intelligence Agent](file:///d:/projects/SCOF_V1/SCOF/services/agents/supplier/), and [Transportation Agent](file:///d:/projects/SCOF_V1/SCOF/services/agents/transportation/)) into a coordinated system managed by a **LangGraph Coordinator**.

Per SRS FR-5.1 through FR-5.5 and architectural invariants:
1. The Coordinator dynamically discovers active specialist agents from the active Domain Profile ([profiles/mvp-electronics/agents.yaml](file:///d:/projects/SCOF_V1/SCOF/profiles/mvp-electronics/agents.yaml)), caches their published **A2A Agent Cards** (`GET /.well-known/agent.json`), and maintains agent health and telemetry state in a registry.
2. Specialist agent tool access is formalized using domain-oriented **Model Context Protocol (MCP)** interfaces (`POST /mcp/tools/list`, `POST /mcp/tools/call`).
3. Parallel delegation is executed via a compiled **LangGraph StateGraph** with semaphore-bounded concurrency, granular connect/read timeouts, intelligent retries, and correlation ID propagation (`X-Correlation-ID`, `X-Bundle-ID`, `X-Trace-ID`).
4. The Coordinator aggregates structured claims into an **immutable `ClaimBundle`** containing raw claims, latency metrics, failure diagnostics, and domain profile version lineage.
5. Consistent with D05's scope boundary, **no consensus arbitration logic, agreement checks, or majority voting occurs in D05** -- all arbitration is deferred to Deliverable D06 CD2F.

---

## Prerequisites Check

> [!NOTE]
> - **D01 (Simulation Foundation)**: Operational. Synthetic supply chain data and parameterized disruption events are generated and queryable in PostgreSQL.
> - **D02 (Knowledge & Data Layer)**: Operational. Neo4j graph topology and PostgreSQL schema are populated and validated.
> - **D03 (Forecasting Agents: Demand + Inventory)**: Operational on ports 8011 and 8012. Both agents publish A2A Agent Cards and return valid `StructuredClaim` objects over HTTP `POST /analyze`.
> - **D04 (Reliability Agents: Supplier + Transportation)**: Operational on ports 8013 and 8014. Both agents query Neo4j graph and PostgreSQL data, publish A2A Agent Cards, and return valid `StructuredClaim` objects over HTTP `POST /analyze`.
> - **Domain Profile**: [profiles/mvp-electronics/agents.yaml](file:///d:/projects/SCOF_V1/SCOF/profiles/mvp-electronics/agents.yaml) defines active agents, ports, confidence floors, model configs, and declared MCP tool names.

---

## User Review Required & Architectural Principles

> [!IMPORTANT]
> **Key Architectural Invariants and Decisions for D05**:
>
> 1. **Immutable ClaimBundle with Full Profile Lineage**:
>    - `ClaimBundle` is a **frozen Pydantic model** (`model_config = ConfigDict(frozen=True)`).
>    - Embeds both `profile_name` and `profile_version` to guarantee full deterministic lineage back to the declarative profile configuration.
>    - Once assembled by D05, it cannot be mutated. Downstream D06 consensus creates a distinct `ConsensusBundle` from `ClaimBundle`.
>    - All agreement, unanimous priority, or voting helper methods are strictly excluded from D05 to preserve the consensus boundary.
>
> 2. **Registry Caching with Atomic Copy-on-Write Refresh**:
>    - Active agents are discovered and cached at startup.
>    - Discovery refresh (triggered via `POST /agents/refresh` or profile change) performs an **atomic copy-on-write reference swap**: a new registry snapshot is assembled and atomically assigned, ensuring concurrent orchestrations see an immutable, consistent view without lock contention.
>    - Explicit health-state transition thresholds:
>      - `UNKNOWN`: Initial state before first successful probe.
>      - `HEALTHY`: Successful communication (or recovery from failure).
>      - `DEGRADED`: After 2 consecutive failures or observed latency exceeding threshold (> 5000ms).
>      - `UNHEALTHY`: After 5 consecutive failures.
>
> 3. **Bounded Parallel Dispatch (Semaphore Throttling)**:
>    - Concurrent agent delegation uses an `asyncio.Semaphore(MAX_CONCURRENT_DISPATCH)` (default 8) to guarantee stable latency and prevent socket exhaustion.
>
> 4. **State Architecture Separation**:
>    - **CoordinatorRuntime**: Persistent service runtime state holding profile configuration, atomic A2A registry reference, compiled LangGraph runnable, and aggregate in-memory metrics (with hooks for D07 persistence).
>    - **CoordinatorExecutionState**: Ephemeral TypedDict/Pydantic state scoped strictly to a single LangGraph execution run.
>
> 5. **Zero Concrete Agent Invariants**:
>    - The Coordinator contains **zero hardcoded references** to specific agent names (no `if agent == "demand"` or `if "supplier"`).
>    - Delegation and filtering rely entirely on `AgentCard`, declared `capabilities`, `supported_contexts`, and the profile roster.
>
> 6. **Granular Timeouts, Retries, and Correlation IDs**:
>    - Dispatches separate `connect_timeout_sec` (2.0s) and `read_timeout_sec` (8.0s).
>    - Differentiated retry policy:
>      - Client errors (`4xx` e.g. 404, 422): Do not retry.
>      - Server errors (`5xx`) & connection timeouts: Retry with exponential backoff up to `max_retries` (default 2).
>    - Correlation headers (`X-Scenario-ID`, `X-Bundle-ID`, `X-Trace-ID`, `X-Profile-Version`) propagated across all outgoing HTTP calls.
>
> 7. **Domain-Oriented MCP Business Tools**:
>    - MCP endpoints wrap high-level domain operations (`read_historical_demand`, `query_supplier_reliability`, `estimate_transit_delay`), avoiding low-level generic DB query tools.
>
> 8. **Enriched Graph Topology Metadata**:
>    - `GET /graph` exposes `compiled_graph_hash`, `graph_version`, `node_count`, `edge_count`, and node/edge definitions.

---

## Open Questions

> [!NOTE]
> 1. **Coordinator Service Port**: Allocated on port `8010` (`scof-coordinator`), keeping ports `8011`-`8014` for specialist agents and port `8000` reserved for D08 API.
> 2. **Mock Dispatch Mode**: The A2A client includes a deterministic offline mock dispatch engine allowing full test execution without requiring Docker containers or live network ports.

---

## Proposed Changes

Grouped by component layer and ordered logically.

---

### Component 1: Shared Library Extensions (`shared/scof_shared/`)

#### [NEW] [claim_bundle.py](file:///d:/projects/SCOF_V1/SCOF/shared/scof_shared/schemas/claim_bundle.py)
- Immutable Pydantic model (`frozen=True`) `ClaimBundle`:
  - Fields: `bundle_id: str`, `scenario_id: str`, `trace_id: str`, `timestamp: datetime`, `profile_name: str`, `profile_version: str`, `status: Literal["COMPLETE", "PARTIAL", "FAILED"]`, `participating_agents: List[str]`, `successful_agents: List[str]`, `failed_agents: Dict[str, str]`, `claims: Dict[str, StructuredClaim]`, `total_latency_ms: float`, `agent_latencies_ms: Dict[str, float]`, `metadata: Dict[str, Any]`.
  - Helpers: `to_dict()`, `from_dict()`, `get_claim(agent_id: str) -> Optional[StructuredClaim]`. No voting or agreement logic.

#### [MODIFY] [schemas/\_\_init\_\_.py](file:///d:/projects/SCOF_V1/SCOF/shared/scof_shared/schemas/__init__.py)
- Export `ClaimBundle`.

#### [MODIFY] [agent_card.py](file:///d:/projects/SCOF_V1/SCOF/shared/scof_shared/schemas/agent_card.py)
- Enrich `AgentCard` with explicit versioning fields: `protocol_version: str = "A2A/1.0"`, `agent_version: str = "1.0.0"`, `profile_version: Optional[str] = "1.0.0"`.

#### [NEW] [protocols/\_\_init\_\_.py](file:///d:/projects/SCOF_V1/SCOF/shared/scof_shared/protocols/__init__.py)
- Package marker exporting A2A and MCP protocol components.

#### [NEW] [protocols/a2a_registry.py](file:///d:/projects/SCOF_V1/SCOF/shared/scof_shared/protocols/a2a_registry.py)
- `AgentRegistration`: Dataclass holding `card: AgentCard`, `health_status: Literal["UNKNOWN", "HEALTHY", "DEGRADED", "UNHEALTHY"]`, `last_seen: Optional[datetime]`, `consecutive_failures: int`, `success_count: int`, `average_latency_ms: float`, `endpoint_url: str`.
- `A2ARegistry`:
  - Immutable copy-on-write snapshot support with methods:
    - `register(card: AgentCard, endpoint_url: str)`
    - `update_health(agent_id: str, success: bool, latency_ms: float, error_detail: Optional[str] = None)`
    - Explicit state transitions:
      - Consecutive failures = 0 and success -> `HEALTHY`
      - Consecutive failures in [2, 4] or latency > 5000ms -> `DEGRADED`
      - Consecutive failures >= 5 -> `UNHEALTHY`
    - `get(agent_id: str) -> Optional[AgentRegistration]`
    - `get_card(agent_id: str) -> Optional[AgentCard]`
    - `get_all() -> List[AgentRegistration]`
    - `get_healthy_cards() -> List[AgentCard]`
    - `find_by_capability(capability: str) -> List[AgentCard]`
    - `find_by_context(disruption_type: str) -> List[AgentCard]`
    - `clone() -> A2ARegistry` (for copy-on-write updates)

#### [NEW] [protocols/a2a_client.py](file:///d:/projects/SCOF_V1/SCOF/shared/scof_shared/protocols/a2a_client.py)
- `A2AClient`:
  - Configurable `connect_timeout_sec` (default 2.0s), `read_timeout_sec` (default 8.0s), `max_retries` (default 2), `max_concurrent_dispatch` (default 8).
  - Uses `asyncio.Semaphore` for concurrency throttling.
  - `discover_agent(endpoint_url: str) -> Optional[AgentCard]`: Queries `GET /.well-known/agent.json`.
  - `discover_roster(roster: AgentsRosterModel, host_map: Optional[Dict[str, str]] = None) -> List[AgentCard]`.
  - `delegate_analyze(agent_card: AgentCard, context: ScenarioContext, trace_id: str, bundle_id: str, profile_version: str) -> Tuple[Optional[StructuredClaim], Optional[str], float]`:
    - Handles retry policy: skips retrying 4xx; retries 5xx and timeouts with exponential backoff.
    - Sets headers: `X-Scenario-ID`, `X-Bundle-ID`, `X-Trace-ID`, `X-Profile-Version`, `X-Agent-ID`.
  - `delegate_analyze_parallel(agent_cards: List[AgentCard], context: ScenarioContext, trace_id: str, bundle_id: str, profile_version: str) -> Dict[str, Tuple[Optional[StructuredClaim], Optional[str], float]]`:
    - Runs bounded parallel dispatch under semaphore.
  - Mock dispatch engine for offline deterministic testing.

#### [NEW] [protocols/mcp_server.py](file:///d:/projects/SCOF_V1/SCOF/shared/scof_shared/protocols/mcp_server.py)
- `create_mcp_router`:
  - FastAPI router exposing `POST /mcp/tools/list` and `POST /mcp/tools/call`.
  - Dispatches tool calls only to declared domain-oriented business tools.

#### [NEW] [protocols/mcp_client.py](file:///d:/projects/SCOF_V1/SCOF/shared/scof_shared/protocols/mcp_client.py)
- `MCPClient`:
  - `list_tools(endpoint_url: str) -> List[Dict[str, Any]]`
  - `call_tool(endpoint_url: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]`

---

### Component 2: Coordinator Microservice (`services/coordinator/`)

The Coordinator Agent manages LangGraph-driven multi-agent orchestration, dynamic A2A discovery caching, bounded parallel claim dispatch, and claim bundle collection.

#### [NEW] [pyproject.toml](file:///d:/projects/SCOF_V1/SCOF/services/coordinator/pyproject.toml)
- Package manifest declaring dependencies: `fastapi`, `uvicorn`, `langgraph>=0.2.0`, `langchain-core`, `pydantic>=2.0`, `pyyaml`, `httpx>=0.27.0`, `scof-shared`.
- Setuptools build system and pytest configuration.

#### [NEW] [Dockerfile](file:///d:/projects/SCOF_V1/SCOF/services/coordinator/Dockerfile)
- Python 3.11-slim container. Installs `scof-shared` and coordinator package. Exposes port 8010.

#### [NEW] [src/\_\_init\_\_.py](file:///d:/projects/SCOF_V1/SCOF/services/coordinator/src/__init__.py)
- Package marker.

#### [NEW] [src/config.py](file:///d:/projects/SCOF_V1/SCOF/services/coordinator/src/config.py)
- Coordinator settings:
  - `COORDINATOR_ID = "coordinator-agent"`
  - `COORDINATOR_NAME = "Supply Chain Cognitive Coordinator"`
  - `DEFAULT_PORT = 8010`
  - `SCOF_PROFILE_PATH = Path(os.getenv("SCOF_PROFILE_PATH", "profiles/mvp-electronics"))`
  - `CONNECT_TIMEOUT_SECONDS = float(os.getenv("CONNECT_TIMEOUT_SECONDS", "2.0"))`
  - `READ_TIMEOUT_SECONDS = float(os.getenv("READ_TIMEOUT_SECONDS", "8.0"))`
  - `MAX_RETRIES = int(os.getenv("MAX_RETRIES", "2"))`
  - `MAX_CONCURRENT_DISPATCH = int(os.getenv("MAX_CONCURRENT_DISPATCH", "8"))`

#### [NEW] [src/state.py](file:///d:/projects/SCOF_V1/SCOF/services/coordinator/src/state.py)
- Separation between runtime and execution state:
  - `CoordinatorExecutionState` (TypedDict for LangGraph):
    - `scenario_context: ScenarioContext`
    - `trace_id: str`
    - `bundle_id: str`
    - `profile_name: str`
    - `profile_version: str`
    - `target_agent_cards: List[AgentCard]`
    - `raw_claims: Dict[str, StructuredClaim]`
    - `failed_agents: Dict[str, str]`
    - `agent_latencies_ms: Dict[str, float]`
    - `claim_bundle: Optional[ClaimBundle]`
    - `execution_log: List[str]`
    - `status: str`
    - `start_time: float`
    - `end_time: float`

#### [NEW] [src/runtime.py](file:///d:/projects/SCOF_V1/SCOF/services/coordinator/src/runtime.py)
- `CoordinatorRuntime`:
  - Persistent state holding atomic `A2ARegistry` reference, `A2AClient`, `DomainProfile`, compiled `StateGraph`, and operational metrics counters (`orchestrations_executed`, `orchestrations_successful`, `orchestrations_partial`, `orchestrations_failed`, `average_latency_ms`, `last_discovery_duration_ms`).
  - Methods: `initialize()`, `refresh_discovery()` (atomic copy-on-write swap), `get_metrics()`.

#### [NEW] [src/agent_discovery.py](file:///d:/projects/SCOF_V1/SCOF/services/coordinator/src/agent_discovery.py)
- `AgentDiscoveryService`:
  - Reads `agents.yaml` via `load_agents_config()`.
  - Discovers active agents at startup and caches them into `A2ARegistry`.
  - Performs atomic registry swap on refresh.
  - Selects target agent cards for a scenario based purely on context capability matching without hardcoded agent IDs.

#### [NEW] [src/claim_collector.py](file:///d:/projects/SCOF_V1/SCOF/services/coordinator/src/claim_collector.py)
- `ClaimCollector`:
  - Executes semaphore-bounded parallel dispatch via `A2AClient`.
  - Updates agent registry health metrics with observed latencies and failure statuses.
  - Builds the final immutable `ClaimBundle` with `profile_version`.

#### [NEW] [src/orchestrator.py](file:///d:/projects/SCOF_V1/SCOF/services/coordinator/src/orchestrator.py)
- `CoordinatorOrchestrator`:
  - Compiles LangGraph `StateGraph(CoordinatorExecutionState)`:
    - Nodes: `node_resolve_targets` -> `node_dispatch_parallel` -> `node_collect_bundle`.
    - Edges: `START -> node_resolve_targets -> node_dispatch_parallel -> node_collect_bundle -> END`.
    - Conditional edge handling for empty agent targets.
  - Exposes `get_graph_metadata()` returning `compiled_graph_hash`, `graph_version`, `node_count`, `edge_count`, `nodes`, `edges`.
  - Method `orchestrate(context: ScenarioContext) -> ClaimBundle`.

#### [NEW] [src/main.py](file:///d:/projects/SCOF_V1/SCOF/services/coordinator/src/main.py)
- FastAPI application:
  - `GET /health` -> Health check with `coordinator_id`, `profile_loaded`, `active_agents_count`, `registry_health_summary`, `graph_compiled`, `uptime_seconds`.
  - `GET /metrics` -> Coordinator operational metrics.
  - `GET /.well-known/agent.json` -> Coordinator's self-describing `AgentCard`.
  - `GET /agents` -> List of cached registrations with health status and telemetry.
  - `POST /agents/refresh` -> Forces atomic copy-on-write registry cache refresh from profile.
  - `GET /graph` -> Rich graph topology with hash, version, node and edge counts.
  - `POST /orchestrate` -> Accepts `ScenarioContext`, runs LangGraph orchestration, returns `ClaimBundle`.
  - `POST /analyze` -> Alias for `/orchestrate`.

#### [NEW] [tests/test_state.py](file:///d:/projects/SCOF_V1/SCOF/services/coordinator/tests/test_state.py)
- Unit tests for `CoordinatorExecutionState` and `ClaimBundle` immutability.

#### [NEW] [tests/test_agent_discovery.py](file:///d:/projects/SCOF_V1/SCOF/services/coordinator/tests/test_agent_discovery.py)
- Unit tests for cached discovery, atomic copy-on-write swap, health threshold transitions (`UNKNOWN` -> `HEALTHY` -> `DEGRADED` -> `UNHEALTHY`), and domain-agnostic capability matching.

#### [NEW] [tests/test_claim_collector.py](file:///d:/projects/SCOF_V1/SCOF/services/coordinator/tests/test_claim_collector.py)
- Unit tests for semaphore concurrency, timeout handling, retry policies, and `ClaimBundle` assembly with profile version.

#### [NEW] [tests/test_orchestrator.py](file:///d:/projects/SCOF_V1/SCOF/services/coordinator/tests/test_orchestrator.py)
- Unit tests for LangGraph compilation, graph metadata hash, execution flow, and determinism.

#### [NEW] [tests/test_coordinator_api.py](file:///d:/projects/SCOF_V1/SCOF/services/coordinator/tests/test_coordinator_api.py)
- FastAPI TestClient tests for `/health`, `/metrics`, `/.well-known/agent.json`, `/agents`, `/agents/refresh`, `/graph`, and `/orchestrate`.

---

### Component 3: Specialist Agent MCP Protocol Integration

Mount domain-oriented MCP routers exposing `POST /mcp/tools/list` and `POST /mcp/tools/call` across all four specialist agents.

#### [MODIFY] [services/agents/demand/src/main.py](file:///d:/projects/SCOF_V1/SCOF/services/agents/demand/src/main.py)
- Mount MCP router for `read_historical_demand`, `read_demand_disruptions`, `read_product_catalog`.

#### [MODIFY] [services/agents/inventory/src/main.py](file:///d:/projects/SCOF_V1/SCOF/services/agents/inventory/src/main.py)
- Mount MCP router for `read_stock_levels`, `read_reorder_points`, `read_inbound_shipments`, `read_inventory_disruptions`.

#### [MODIFY] [services/agents/supplier/src/main.py](file:///d:/projects/SCOF_V1/SCOF/services/agents/supplier/src/main.py)
- Mount MCP router for `query_supplier_graph`, `read_delivery_history`, `query_alternate_suppliers`, `read_supplier_disruptions`.

#### [MODIFY] [services/agents/transportation/src/main.py](file:///d:/projects/SCOF_V1/SCOF/services/agents/transportation/src/main.py)
- Mount MCP router for `query_route_network`, `estimate_delay`, `query_alternative_routes`, `read_transport_disruptions`.

---

### Component 4: Infrastructure & Automation (`docker-compose.yml`, `Makefile`, `scripts/`)

#### [MODIFY] [docker-compose.yml](file:///d:/projects/SCOF_V1/SCOF/docker-compose.yml)
- Add `coordinator` service on port `8010` with network dependencies on specialist agents.

#### [MODIFY] [Makefile](file:///d:/projects/SCOF_V1/SCOF/Makefile)
- Add `verify-d5` target to execute `python scripts/verify_d5.py`.

#### [NEW] [scripts/verify_d5.py](file:///d:/projects/SCOF_V1/SCOF/scripts/verify_d5.py)
- Automated D05 verification script verifying:
  1. Dynamic agent roster loading from `agents.yaml` and startup registry caching.
  2. A2A Agent Card retrieval and validation from all active specialist agents.
  3. Domain-oriented MCP tools listing and schema validation across all agents.
  4. LangGraph state graph compilation and topology inspection (`GET /graph` metadata verification with graph hash).
  5. End-to-end orchestration execution across 4 disruption scenarios (`supplier_delay`, `transport_failure`, `demand_spike`, `adverse_weather`).
  6. Immutability and structural integrity of `ClaimBundle` including `profile_version`.
  7. Verification of correlation headers (`X-Scenario-ID`, `X-Bundle-ID`, `X-Trace-ID`, `X-Profile-Version`).
  8. Health transition threshold verification (`UNKNOWN` -> `HEALTHY` -> `DEGRADED` -> `UNHEALTHY`).
  9. Atomic copy-on-write registry swap during concurrent discovery refresh.
  10. Invariant verification: zero hardcoded agent names in orchestrator logic.
  11. Determinism check: identical scenario context produces identical structured claims and bundle structure.

---

### Component 5: Deliverable D05 Documentation (`docs/deliverables/D05_orchestration/`)

#### [MODIFY] [README.md](file:///d:/projects/SCOF_V1/SCOF/docs/deliverables/D05_orchestration/README.md)
- Complete D05 overview, objectives, requirements mapping (FR-5.1 to FR-5.5), architecture overview, prerequisites, document index, module structure, and definition of done.

#### [NEW] [implementation_plan.md](file:///d:/projects/SCOF_V1/SCOF/docs/deliverables/D05_orchestration/implementation_plan.md)
- Persistent technical design and implementation reference document for Deliverable D05.

#### [NEW] [langgraph_design.md](file:///d:/projects/SCOF_V1/SCOF/docs/deliverables/D05_orchestration/langgraph_design.md)
- State schema, runtime vs execution state, graph topology, node execution contracts, edge routing, error handling, parallel dispatch semantics, and graph hash verification.

#### [NEW] [mcp_server_design.md](file:///d:/projects/SCOF_V1/SCOF/docs/deliverables/D05_orchestration/mcp_server_design.md)
- Formal Model Context Protocol (MCP) server specifications: endpoints (`/mcp/tools/list`, `/mcp/tools/call`), schema validation, domain business tools per agent, and error protocols.

#### [NEW] [a2a_protocol_design.md](file:///d:/projects/SCOF_V1/SCOF/docs/deliverables/D05_orchestration/a2a_protocol_design.md)
- Agent-to-Agent (A2A) protocol specification: `AgentCard` schema, registry caching lifecycle with copy-on-write swap, health threshold transitions, capability negotiation, retry/timeout policies, and delegation mechanics.

#### [NEW] [acceptance_evidence.md](file:///d:/projects/SCOF_V1/SCOF/docs/deliverables/D05_orchestration/acceptance_evidence.md)
- Verification log template capturing automated test runs, claim bundle outputs, MCP/A2A contract compliance, and acceptance check results.

---

## Verification Plan

### Automated Tests
1. **Unit & Protocol Tests**:
   - Run pytest across shared protocols and coordinator unit tests:
     ```powershell
     pytest services/coordinator/tests/
     ```
   - Run specialist agent test suites to verify backwards compatibility:
     ```powershell
     pytest services/agents/demand/tests/ services/agents/inventory/tests/ services/agents/supplier/tests/ services/agents/transportation/tests/
     ```

2. **D05 Verification Script**:
   - Run automated verification script validating end-to-end orchestration, A2A discovery, MCP tools, and claim bundle creation:
     ```powershell
     python scripts/verify_d5.py
     ```

3. **Regression Suite**:
   - Run previous deliverable verifications:
     ```powershell
     python scripts/verify_d1.py
     python scripts/verify_d2.py
     python scripts/verify_d3.py
     python scripts/verify_d4.py
     ```

### Manual & Standalone Acceptance Criteria ("Definition of Done")
- [ ] Coordinator container (`scof-coordinator` on port 8010) starts cleanly and reports healthy status.
- [ ] `GET http://localhost:8010/health` returns status `healthy`, with `graph_compiled=True`, `profile_loaded=True`, and active registry summary.
- [ ] `GET http://localhost:8010/metrics` returns operational metrics (`orchestrations_executed`, latencies).
- [ ] `GET http://localhost:8010/.well-known/agent.json` returns valid Coordinator `AgentCard` with protocol/agent/profile versions.
- [ ] `GET http://localhost:8010/agents` returns active specialist agent registrations with telemetry and health states.
- [ ] `GET http://localhost:8010/graph` returns complete LangGraph topology with `compiled_graph_hash`, `graph_version`, node count, and edge count.
- [ ] Each specialist agent (`8011`, `8012`, `8013`, `8014`) responds to `POST /mcp/tools/list` with domain business tool descriptors.
- [ ] `POST http://localhost:8010/orchestrate` with synthetic `ScenarioContext` triggers LangGraph execution and returns an immutable `ClaimBundle` with `profile_version` containing all structured claims and latency breakdown.
- [ ] Outgoing HTTP requests carry `X-Scenario-ID`, `X-Bundle-ID`, `X-Trace-ID`, `X-Profile-Version`.
- [ ] Coordinator contains zero hardcoded concrete agent names in execution and dispatch logic.
- [ ] Changing `agents.yaml` dynamically updates Coordinator discovery upon refresh via copy-on-write atomic swap without modifying orchestration code.
- [ ] 100% of checks in `scripts/verify_d5.py` pass.
