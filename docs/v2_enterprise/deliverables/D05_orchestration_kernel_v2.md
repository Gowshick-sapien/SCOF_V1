# Deliverable D05 (V2): Orchestration & Protocol Kernel

## 1. Overview & Objectives

Deliverable D05 elevates the sequential LangGraph runner of V1 into the **Enterprise Multi-Agent Orchestration & Protocol Kernel**. It provides the deterministic runtime environment, communication protocol, and state machine that coordinates parallel agent deliberation during supply chain disruptions.

The kernel enforces strict Service Level Agreements (SLAs), manages asynchronous fan-out/fan-in agent rounds, guards against infinite deliberation loops, and guarantees zero mutation of baseline state ([ADR 015](file:///d:/projects/SCOF_V1/SCOF/docs/adr/015_tripartite_state_isolation_for_benchmark_integrity.md)).

### Subsystem Boundaries:
* **LangGraph Kernel Owns:** Cognitive workflow state machine, agent scheduling, parallel fan-out/fan-in, query routing via Tri-Zone router, dynamic MCP tool mounting via Capability Registry, and claim collating.
* **LangGraph Kernel Does NOT Own:** Physics simulation (owned by Twin), consensus arbitration (owned by CD²F), enterprise master data (owned by D2), or physical ERP writes (owned by Execution Adapters).

---

## 2. Deliberation State Machine Architecture

The orchestration engine is structured as a cyclical LangGraph state graph with five deterministic phases:

```text
                  ┌────────────────────────────────────────┐
                  │ 1. Ingestion, Routing & Framing        │
                  │    - Tri-Zone Cognitive Router         │
                  │    - Dynamic Capability Registry Tool  │
                  │      Binding (3-5 Bounded Tools)       │
                  └──────────────────┬─────────────────────┘
                                     │
                                     ▼
                  ┌────────────────────────────────────────┐
                  │ 2. Concurrent Proposal Generation      │
                  │    - Parallel Fan-Out (850ms SLA)      │
                  │    - Demand, Inventory, Supplier,      │
                  │      Transportation Specialists        │
                  └──────────────────┬─────────────────────┘
                                     │
                                     ▼
                  ┌────────────────────────────────────────┐
                  │ 3. Cross-Examination & Critique        │
                  │    - Conflict detection & trade-offs   │
                  └──────────────────┬─────────────────────┘
                                     │
                                     ▼
                  ┌────────────────────────────────────────┐
                  │ 4. Consensus & Decision Hand-Off       │ ──► [D06: CD²F Engine]
                  └──────────────────┬─────────────────────┘
                                     │
                                     ▼
                  ┌────────────────────────────────────────┐
                  │ 5. Execution & Twin Sandbox Commit     │ ──► [twin_service.py Layer 3]
                  └────────────────────────────────────────┘
```

### 2.1 State Graph Phases
1. **Phase 1: Ingestion, Routing & Framing:** Ingests the disruption event (from API/Kafka in D08 or scenario runner in D01), scopes affected SKUs, facilities, and corridors via the Knowledge Fabric, invokes the [Cognitive Query Router](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/architecture/02_cognitive_query_routing_and_resolution_pipeline.md) and Deeper Resolver, and binds 3–5 bounded MCP tools dynamically via the [Dynamic Capability Registry](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/architecture/03_dynamic_capability_registry.md).
2. **Phase 2: Concurrent Proposal Generation:** Asynchronously invokes all four specialist agents (`demand`, `inventory`, `supplier`, `transport`) with an 850 ms deadline. Each agent emits a candidate `StructuredClaimV2`.
3. **Phase 3: Cross-Examination & Critique:** Agents inspect peer claims to identify cross-domain conflicts (e.g., Inventory ordering stock from a carrier route that Transport flagged as blocked). Agents emit formal critique tuples.
4. **Phase 4: Consensus Hand-Off:** The set of claims and critiques is submitted to the CD²F Consensus Engine (D06) for weighted multi-factor arbitration.
5. **Phase 5: Execution & Twin Commit:** The resolved consensus action is applied to the Layer 3 ephemeral simulation state via `twin_service.py`, updating physical metrics and producing verified execution receipts.

---

## 3. Deliberation State Schema

The shared graph state is typed and validated across every transition:

```python
class DeliberationState(TypedDict):
    scenario_id: str
    sim_run_id: str
    cycle_index: int
    disruption_event: dict
    active_claims: dict[str, StructuredClaimV2]
    critiques: list[AgentCritique]
    transcript: list[DeliberationMessage]
    consensus_decision: Optional[ConsensusOutcome]
    execution_status: str
```

---

## 4. Resilience & Fallback Controls

1. **Strict Execution Budget:** Every agent invocation is bounded by an 850 ms wall-clock timeout. If an agent fails to return within the window, the kernel falls back to the agent's pre-configured deterministic rule baseline.
2. **Cycle Termination Gating:** Deliberation is strictly limited to a maximum of 3 rounds. If consensus is not reached within 3 cycles, the kernel automatically escalates to Tier-2 heuristic arbitration (D06).
3. **Audit Ledger:** Every state transition emits an immutable log entry containing token consumption, agent latencies, and verbatim message payloads for Deliverable D07.

---

## 5. Acceptance Criteria & Verification Evidence

1. **Cycle Latency Gate:** Complete 4-agent deliberation loop terminates in $\le 3.5\text{ s}$.
2. **Determinism Gate:** Replaying the identical scenario with the same seed produces the identical deliberation trace and state progression.
3. **Resilience Gate:** Simulating a total LLM timeout on one agent causes graceful fallback to heuristic mode with zero orchestrator crash.
4. **State Isolation Gate:** All database mutations during deliberation are verified to target Layer 3 only.
