# Deliverable D05 -- Agent Orchestration & Protocol Layer

## Overview & Purpose

Deliverable D05 implements the **Agent Orchestration and Protocol Layer** of the SCOF platform. It wires the four independent specialist AI agents built in D03 and D04 ([Demand Forecast Agent](file:///d:/projects/SCOF_V1/SCOF/services/agents/demand/), [Inventory Agent](file:///d:/projects/SCOF_V1/SCOF/services/agents/inventory/), [Supplier Intelligence Agent](file:///d:/projects/SCOF_V1/SCOF/services/agents/supplier/), and [Transportation Agent](file:///d:/projects/SCOF_V1/SCOF/services/agents/transportation/)) into a coordinated cognitive system managed by a **LangGraph Coordinator** microservice (`services/coordinator/`).

Crucially, the Coordinator enforces domain independence and protocol-driven communication:
1. **Dynamic A2A Discovery & Registry Caching**: The Coordinator dynamically discovers active specialist agents at startup by parsing the active Domain Profile ([profiles/mvp-electronics/agents.yaml](file:///d:/projects/SCOF_V1/SCOF/profiles/mvp-electronics/agents.yaml)) and resolving their published **A2A Agent Cards** (`GET /.well-known/agent.json`). Cached registries are refreshed via atomic copy-on-write reference swaps without blocking active orchestrations.
2. **Domain-Oriented MCP Server Protocol**: Specialist agent tool access is formalized through standard **Model Context Protocol (MCP)** endpoints (`POST /mcp/tools/list`, `POST /mcp/tools/call`), exposing high-level domain tools rather than generic database primitives.
3. **LangGraph StateGraph Execution**: Orchestration is driven by a compiled `StateGraph(CoordinatorExecutionState)` that executes parallel specialist agent delegation with semaphore-bounded concurrency, granular timeouts, intelligent retries, and correlation ID tracing.
4. **Immutable ClaimBundle Contract**: The Coordinator collects raw structured claims from all participating agents into an immutable `ClaimBundle` annotated with execution latency, status diagnostics, and domain profile version lineage.
5. **Consensus Boundary Invariant**: Consistent with SRS FR-5.4, D05 strictly aggregates raw claims without applying consensus arbitration or voting logic (arbitration is deferred to Deliverable D06 CD2F).

---

## Requirements Summary (from SRS)

- **FR-5.1**: Implement a LangGraph state graph connecting specialist agents to a Coordinator node.
- **FR-5.2**: Formalize MCP servers wrapping agent tool/data access.
- **FR-5.3**: Implement an A2A layer where agents publish Agent Cards for dynamic Coordinator discovery and delegation.
- **FR-5.4**: The Coordinator collects claim bundles without applying arbitration logic yet (arbitration deferred to D6).
- **FR-5.5**: Active agent roster read dynamically from the active Domain Profile (`agents.yaml`).

---

## Prerequisites & Dependencies

- **Prerequisite Deliverables**:
  - [D01_simulation_data](file:///d:/projects/SCOF_V1/SCOF/docs/deliverables/D01_simulation_data/README.md) -- Synthetic supply chain operational and disruption data populated in PostgreSQL.
  - [D02_knowledge_layer](file:///d:/projects/SCOF_V1/SCOF/docs/deliverables/D02_knowledge_layer/README.md) -- Neo4j graph topology and PostgreSQL schema operational.
  - [D03_demand_inventory_agents](file:///d:/projects/SCOF_V1/SCOF/docs/deliverables/D03_demand_inventory_agents/README.md) -- Demand (port 8011) and Inventory (port 8012) specialist agents operational.
  - [D04_supplier_transport_agents](file:///d:/projects/SCOF_V1/SCOF/docs/deliverables/D04_supplier_transport_agents/README.md) -- Supplier (port 8013) and Transportation (port 8014) specialist agents operational.
- **Required System Tools**: Docker (v24+), Python 3.11+, LangGraph (v0.2+).
- **Required Domain Profile**:
  - [profiles/mvp-electronics/agents.yaml](file:///d:/projects/SCOF_V1/SCOF/profiles/mvp-electronics/agents.yaml) -- Configures active agent roster, ports, confidence floors, and declared MCP tools.

---

## Document Set in this Directory

1. [README.md](file:///d:/projects/SCOF_V1/SCOF/docs/deliverables/D05_orchestration/README.md) (this document): Overview, SRS requirements mapping, architecture, prerequisites, document index, module structure, and definition of done.
2. [implementation_plan.md](file:///d:/projects/SCOF_V1/SCOF/docs/deliverables/D05_orchestration/implementation_plan.md): Detailed technical implementation plan, architectural invariants, proposed code changes, and verification harness.
3. [langgraph_design.md](file:///d:/projects/SCOF_V1/SCOF/docs/deliverables/D05_orchestration/langgraph_design.md): State graph topology, state schema (`CoordinatorRuntime` vs `CoordinatorExecutionState`), node execution semantics, edge routing, semaphore throttling, and graph hash verification.
4. [mcp_server_design.md](file:///d:/projects/SCOF_V1/SCOF/docs/deliverables/D05_orchestration/mcp_server_design.md): Formal Model Context Protocol (MCP) server specifications: endpoints (`/mcp/tools/list`, `/mcp/tools/call`), schema validation, domain business tools per agent, and error protocols.
5. [a2a_protocol_design.md](file:///d:/projects/SCOF_V1/SCOF/docs/deliverables/D05_orchestration/a2a_protocol_design.md): Agent-to-Agent (A2A) protocol specification: `AgentCard` schema, registry caching lifecycle with copy-on-write swap, health threshold transitions, capability negotiation, retry/timeout policies, and delegation mechanics.
6. [acceptance_evidence.md](file:///d:/projects/SCOF_V1/SCOF/docs/deliverables/D05_orchestration/acceptance_evidence.md): Evidence verification log template for D05 acceptance criteria.

---

## Module Structure

```
services/
    coordinator/
        Dockerfile
        pyproject.toml
        src/
            __init__.py
            config.py                   # Port 8010, timeouts, retry policy, concurrency limits
            main.py                     # FastAPI app: /orchestrate, /agents, /health, /metrics, /graph
            state.py                    # CoordinatorExecutionState TypedDict for LangGraph
            runtime.py                  # CoordinatorRuntime persistent state, registry cache, metrics
            agent_discovery.py          # Dynamic discovery from agents.yaml, copy-on-write registry
            claim_collector.py          # Semaphore-bounded parallel dispatch & ClaimBundle builder
            orchestrator.py             # LangGraph StateGraph builder, node definitions, runnable
        tests/
            test_state.py
            test_agent_discovery.py
            test_claim_collector.py
            test_orchestrator.py
            test_coordinator_api.py

shared/
    scof_shared/
        schemas/
            claim_bundle.py             # Immutable ClaimBundle schema (frozen Pydantic model)
            agent_card.py               # Enriched AgentCard with protocol/agent/profile versioning
        protocols/
            __init__.py
            a2a_registry.py             # In-memory A2ARegistry, AgentRegistration, health tracking
            a2a_client.py               # A2AClient: discovery, bounded parallel delegation, retries
            mcp_server.py               # create_mcp_router for specialist agent tool exposure
            mcp_client.py               # MCPClient: list_tools, call_tool protocol client

scripts/
    verify_d5.py                        # Automated D05 verification script
```

---

## Definition of Done (Acceptance Criteria)

1. **Coordinator Service Lifecycle**: `scof-coordinator` runs as a FastAPI service on port 8010, starts cleanly, and passes health checks with `graph_compiled=True` and `profile_loaded=True`.
2. **Dynamic A2A Discovery**: Coordinator reads `agents.yaml` dynamically, fetches `GET /.well-known/agent.json` from each agent, caches registrations, and tracks health states (`UNKNOWN` -> `HEALTHY` -> `DEGRADED` -> `UNHEALTHY`).
3. **MCP Tool Compliance**: All four specialist agents expose domain-oriented tools over `POST /mcp/tools/list` and `POST /mcp/tools/call`.
4. **Compiled LangGraph StateGraph**: LangGraph executes `node_resolve_targets -> node_dispatch_parallel -> node_collect_bundle`, exposes verifiable graph topology with hash metadata, and handles empty or failing nodes gracefully.
5. **Immutable ClaimBundle**: Orchestration outputs a frozen `ClaimBundle` containing claims from all active specialist agents, timing breakdown, failure diagnostics, and `profile_version` provenance.
6. **Zero Concrete Agent Invariants**: Coordinator contains zero hardcoded agent names or domain-specific branching logic.
7. **Traceability & Correlation**: All inter-service requests propagate correlation headers (`X-Scenario-ID`, `X-Bundle-ID`, `X-Trace-ID`, `X-Profile-Version`).
8. **Automated Verification**: 100% of checks in `scripts/verify_d5.py` pass and all unit/protocol test suites pass.
