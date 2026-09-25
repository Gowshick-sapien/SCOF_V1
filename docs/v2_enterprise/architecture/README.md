# SCOF V2 Subsystem Architecture Documentation

## 1. Overview & Purpose

This directory contains the authoritative subsystem architecture specifications for the **Supply Chain Cognitive Orchestration Framework (SCOF) V2 Enterprise Cognitive Twin**.

These specifications translate the foundational architectural synthesis established during the enterprise evolution into rigorous, modular, and implementable engineering blueprints. They define the computational boundaries, state models, routing pipelines, concurrency controls, and integration contracts governing all core SCOF subsystems.

---

## 2. Subsystem Architecture Index

| Document | Subsystem Title | Core Responsibility | Primary ADR References |
| :--- | :--- | :--- | :--- |
| [01_digital_twin_service_architecture.md](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/architecture/01_digital_twin_service_architecture.md) | **Digital Twin Service Architecture** | Authoritative state authority, scenario sandbox, discrete-event simulation kernel, invariant enforcement, forward propagation, and counterfactual engine. | [ADR ADR 009](file:///d:/projects/SCOF_V1/SCOF/docs/adr/009_cognitive_twin_service_substrate.md), [ADR ADR 008](file:///d:/projects/SCOF_V1/SCOF/docs/adr/008_operational_digital_twin_substrate_layer.md), [ADR ADR 010](file:///d:/projects/SCOF_V1/SCOF/docs/adr/010_event_stepped_simulation_kernel_over_fixed_tick_daemon.md) |
| [02_cognitive_query_routing_and_resolution_pipeline.md](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/architecture/02_cognitive_query_routing_and_resolution_pipeline.md) | **Cognitive Query Routing & Resolution Pipeline** | Tri-Zone query router, fast-path deterministic evaluator, ambiguous-path Deeper Resolver, parameter synthesis, and operational class segregation. | [ADR ADR 016](file:///d:/projects/SCOF_V1/SCOF/docs/adr/016_dual_path_execution_routing.md), [ADR ADR 013](file:///d:/projects/SCOF_V1/SCOF/docs/adr/013_tri_zone_query_routing_and_deeper_resolver.md) |
| [03_dynamic_capability_registry.md](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/architecture/03_dynamic_capability_registry.md) | **Dynamic Capability Registry** | Declarative capability discovery, provider registration, semantic intent matching, and bounded tool synthesis replacing static endpoint explosion. | [ADR ADR 012](file:///d:/projects/SCOF_V1/SCOF/docs/adr/012_mcp_and_a2a_protocol_standardization.md), [ADR ADR 012 (Amendment)](file:///d:/projects/SCOF_V1/SCOF/docs/adr/012b_amendment_dynamic_capability_registry_over_static_mcp.md) |
| [04_minimalist_concurrency_and_worker_pool.md](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/architecture/04_minimalist_concurrency_and_worker_pool.md) | **Minimalist Concurrency & Worker Pool** | 4-tier Priority Queue (P0-P3), bounded worker pool dispatching, FIFO ordering per tier, and non-blocking in-memory scenario branch overlays. | [ADR ADR 021](file:///d:/projects/SCOF_V1/SCOF/docs/adr/021_containerized_polyglot_microservices.md), [ADR ADR 011](file:///d:/projects/SCOF_V1/SCOF/docs/adr/011_minimalist_bounded_worker_concurrency.md) |
| [05_state_isolation_and_evidence_fabric.md](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/architecture/05_state_isolation_and_evidence_fabric.md) | **State Isolation & Evidence Fabric** | 5-tier state hierarchy, tripartite state isolation (Layer 1-3), immutable Neo4j topology projection, and deterministic evidence packs with SHA-256 provenance. | [ADR ADR 005 (Amendment)](file:///d:/projects/SCOF_V1/SCOF/docs/adr/005b_amendment_materialized_graph_projection_and_bounded_queries.md), [ADR ADR 002](file:///d:/projects/SCOF_V1/SCOF/docs/adr/002_tripartite_state_isolation_for_benchmark_integrity.md), [ADR ADR 006](file:///d:/projects/SCOF_V1/SCOF/docs/adr/006_immutable_neo4j_topology_with_in_memory_scenario_overlays.md), [ADR ADR 017](file:///d:/projects/SCOF_V1/SCOF/docs/adr/017_five_tier_state_hierarchy_and_actuation_boundaries.md) |
| [06_subsystem_boundaries_and_orchestration_contracts.md](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/architecture/06_subsystem_boundaries_and_orchestration_contracts.md) | **Subsystem Boundaries & Orchestration Contracts** | Clean decoupling of responsibilities across Twin State Authority, LangGraph Kernel, CD2F Consensus, and ERP Execution Adapters. | [ADR ADR 014](file:///d:/projects/SCOF_V1/SCOF/docs/adr/014_langgraph_orchestration_kernel.md), [ADR ADR 015](file:///d:/projects/SCOF_V1/SCOF/docs/adr/015_cd2f_consensus_arbitration.md), [ADR ADR 003](file:///d:/projects/SCOF_V1/SCOF/docs/adr/003_decoupling_data_domains_from_agent_roster.md) |

---

## 3. High-Level Subsystem Interaction Flow

```text
+-------------------------------------------------------------------------------+
|                             INGRESS CHANNELS                                  |
|   Channel A: IoT / Telemetry   |   Channel B: Human   |   Channel C: Injected |
+----------------------------------------+--------------------------------------+
                                         |
                                         v
+-------------------------------------------------------------------------------+
|                     COGNITIVE QUERY ROUTING PIPELINE                          |
|   1. Fast-Path Deterministic Rule Router (High Confidence >= 0.85)            |
|   2. Deeper Resolver (Ambiguous / Multi-Domain Intent 0.50 <= c < 0.85)       |
|   3. Dynamic Capability Registry Matching                                     |
+----------------------------------------+--------------------------------------+
                                         |
         +-------------------------------+-------------------------------+
         | (Class A: Read-Only)          | (Class B: Analytics)          | (Class C: Simulation)
         v                               v                               v
+------------------+           +-------------------+           +------------------+
|    D2 FABRIC     |           | ANALYTIC SERVICES |           |   TWIN SERVICE   |
| PostgreSQL/Neo4j |           | Forecasting/Stats |           | Scenario State   |
+------------------+           +-------------------+           | DES Kernel       |
                                                               | Causal Rules     |
                                                               | Counterfactuals  |
                                                               +--------+---------+
                                                                        |
                                         +------------------------------+
                                         | Operational Evidence Pack
                                         v
+-------------------------------------------------------------------------------+
|                       LANGGRAPH ORCHESTRATION KERNEL                          |
|   Specialist Agent Deliberation: Demand, Inventory, Supplier, Transport       |
+----------------------------------------+--------------------------------------+
                                         | Structured Claims
                                         v
+-------------------------------------------------------------------------------+
|                       CD2F DYNAMIC CONSENSUS ENGINE                           |
|   Multi-Factor Weighting, Cross-Domain Arbitration, Gated Escalation          |
+----------------------------------------+--------------------------------------+
                                         |
         +-------------------------------+-------------------------------+
         | Approved Scenario Action                                      | High Severity / Low Consensus
         v                                                               v
+------------------+                                           +------------------+
|   TWIN SERVICE   |                                           |  HUMAN-IN-THE-   |
| Sandbox Mutation |                                           |  LOOP (HITL)     |
+------------------+                                           +--------+---------+
                                                                        | Operator Approval
                                                                        v
                                                               +------------------+
                                                               |   ERP ADAPTER    |
                                                               | Physical Orders  |
                                                               +------------------+
```

---

## 4. Architectural Invariants Enforced Across Subsystems

1. **PostgreSQL Single Source of Fact:** All master records, transactional state, and financial ledgers originate and finalize in PostgreSQL.
2. **Immutable Neo4j Topology:** Neo4j represents the authoritative physical and operational network topology. It is never subjected to dirty runtime writes during scenario simulations.
3. **Tripartite State Isolation:** Simulations never mutate Layer 1 (Frozen Ground Truth) or Layer 2 (Clean Baseline). All perturbations exist exclusively within isolated Layer 3 contexts.
4. **Decoupled Ownership:**
   - The Twin does not orchestrate agents.
   - The Twin does not arbitrate consensus.
   - The Twin does not directly execute real-world ERP mutations.
   - Agents do not bypass governance to execute raw database or graph writes.
5. **Deterministic Replayability:** Any operational state, simulation run, or consensus arbitration can be deterministically reproduced given its scenario context, random seed, and initial state vectors.
