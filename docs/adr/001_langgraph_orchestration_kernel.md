# ADR 001: Orchestration Kernel Selection — LangGraph vs. CrewAI, AutoGen, and Semantic Kernel

* **Status**: Accepted
* **Date**: 2026-07-28
* **Deciders**: SCOF Core Architecture Team
* **Consulted**: Agent Engineering, Observability Leads
* **Informed**: All Platform Developers

---

## 1. Context and Problem Statement

SCOF requires an autonomous coordinator to orchestrate multiple domain-specific specialist agents (Demand, Inventory, Supplier, and Transportation). The coordinator must ingest multimodal disruption signals, query agent availability, dispatch contextual parameters, collect structured mitigation claims, manage cyclical debate loops when claims conflict, and route the finalized decision to the consensus engine.

Traditional multi-agent frameworks often treat agent execution as linear chains or unstructured autonomous chat loops. For enterprise supply chain operations, unconstrained conversational loops introduce non-determinism, unpredictable execution latencies, risk of runaway token consumption, and an inability to reliably audit the exact stage of decision-making.

---

## 2. Decision Drivers

* **State Determinism**: Ability to define strict, verifiable state schemas where each agent updates predictable state keys.
* **Cyclical Flow Control**: Support for multi-turn negotiation and dispute resolution with explicit loop counters and termination bounds.
* **Granular Observability**: Ability to checkpoint state at every single node transition for auditability and step-level replay.
* **Human-in-the-Loop (HITL) Interruption**: Native capability to pause execution at designated nodes (e.g. `human_escalation`) and resume upon operator feedback without state corruption.
* **Protocol Compatibility**: Seamless mapping to Agent-to-Agent (A2A) protocol message schemas.

---

## 3. Considered Options

* **Option 1: CrewAI** (Role-based autonomous hierarchical agent framework)
* **Option 2: Microsoft AutoGen** (Conversational multi-agent conversation framework)
* **Option 3: Microsoft Semantic Kernel** (Enterprise planner and plugin architecture)
* **Option 4: LangGraph** (Stateful, directed cyclical graph orchestration framework)

---

## 4. Decision Outcome

**Chosen Option**: **Option 4 — LangGraph**

### Rationale:
LangGraph models agent coordination as a formal **StateGraph** (a directed cyclic graph). Unlike CrewAI and AutoGen, which prioritize open-ended conversational debate, LangGraph enforces strict, typed state dictionaries (`CoordinatorState`) passed across discrete computational nodes. 

1. **Deterministic Edge Routing**: Conditional edges (`tools_condition`, `should_continue`, `check_consensus`) inspect structured agent claims and route to arbitration or escalation based on deterministic mathematical criteria.
2. **State Checkpointing**: LangGraph provides built-in state persistence (`MemorySaver` or PostgreSQL checkpoints), allowing complete replayability of how a decision evolved across steps.
3. **Interruptibility**: LangGraph natively supports `interrupt_before` and `interrupt_after` hooks, essential for halting execution when CD²F triggers a `HUMAN_ESCALATION` tier.

---

## 5. Pros and Cons of the Selected Option

### Positive Consequences:
* Complete auditability of state evolution across the 8-stage decision lifecycle.
* Strict prevention of infinite agent debate loops via bounded graph cycles.
* Direct integration with LangSmith and Langfuse for production tracing.
* Clear separation between agent intelligence (nodes) and routing logic (edges).

### Negative Consequences / Trade-offs:
* Higher initial scaffolding overhead compared to lightweight agent wrappers.
* Developers must define explicit Pydantic state models for graph transitions.

---

## 6. Implementation & Compliance Notes

* Implemented in [services/coordinator/src/graph.py](file:///d:/projects/SCOF_V1/SCOF/services/coordinator/src/graph.py) and [services/coordinator/src/nodes.py](file:///d:/projects/SCOF_V1/SCOF/services/coordinator/src/nodes.py).
* State definition: `CoordinatorState` typed dictionary tracking disruption metadata, agent claims, meeting logs, and escalation status.
* Verified via `python scripts/verify_d5.py` and `python scripts/verify_full_loop.py`.

---

## 7. Related Decisions & Artifacts

* [ADR 004: Consensus Arbitration Framework](./004_cd2f_consensus_arbitration.md)
* [ADR 006: Protocol Standardization (MCP & A2A)](./006_mcp_and_a2a_protocol_standardization.md)
* [System Architecture Document](file:///d:/projects/SCOF_V1/SCOF/docs/architecture.md)
