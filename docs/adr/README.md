# SCOF Architecture Decision Records (ADRs)

This directory contains the formal, sequentially tracked **Architecture Decision Records (ADRs)** for the **Supply Chain Cognitive Orchestration Framework (SCOF)**. Each document captures a critical architectural choice, problem context, considered options, decision rationale, and operational consequences.

---

## Architecture Decision Index

### Track 1: V1 MVP Baseline Decisions (001 – 012)
These decisions governed the initial proof-of-concept multi-agent consensus system over the 5-supplier electronics profile.

| ADR ID | Title | Status | Scope | Primary Technology / Pattern |
| :--- | :--- | :--- | :--- | :--- |
| **[ADR 001](./001_langgraph_orchestration_kernel.md)** | Orchestration Kernel Selection | **Accepted** | Multi-agent coordination, state machines | LangGraph StateGraph |
| **[ADR 002](./002_apache_kafka_event_streaming.md)** | Message Streaming Bus Selection | **Accepted** | Disruption distribution, replay | Apache Kafka (KRaft) |
| **[ADR 003](./003_pgvector_for_semantic_memory.md)** | Vector Database Selection | **Accepted** | Semantic embeddings, historical RAG | PostgreSQL 16 + pgvector |
| **[ADR 004](./004_cd2f_consensus_arbitration.md)** | Consensus Arbitration Framework | **Accepted** | Claim weighting, deadlock elimination | CD²F Dynamic Arbitration Engine |
| **[ADR 005](./005_dual_path_execution_routing.md)** | Execution Routing Strategy | **Accepted** | Sub-second SLA vs. risk guardrails | Fast-Path vs. Slow-Path / HITL |
| **[ADR 006](./006_mcp_and_a2a_protocol_standardization.md)** | Protocol Standardization | **Accepted** | Tool interfaces and agent discovery | Model Context Protocol & A2A |
| **[ADR 007](./007_hybrid_knowledge_layer_neo4j_postgres.md)** | Hybrid Knowledge Layer Architecture | **Amended** | Network graph + transactional state | Neo4j 5.18 + PostgreSQL 16 |
| **[ADR 008](./008_tauri_v2_desktop_operations_console.md)** | Desktop Console Architecture | **Accepted** | Native control room desktop shell | Tauri v2 + React 19 + Apple HIG |
| **[ADR 009](./009_declarative_yaml_domain_profiles.md)** | Domain Profile Architecture | **Amended** | Multi-vertical extensibility | YAML Profile Configurations |
| **[ADR 010](./010_redis_realtime_state_caching.md)** | State Caching & WebSockets | **Accepted** | Ephemeral state, WebSocket streaming | Redis 7 Alpine |
| **[ADR 011](./011_empirical_evaluation_cohens_kappa.md)** | Empirical Evaluation & Calibration | **Accepted** | Statistical reliability vs. grading | Cohen's Kappa + Benchmark Suite |
| **[ADR 012](./012_containerized_polyglot_microservices.md)** | Service Fleet Isolation & Packaging | **Accepted** | Boundary isolation, local deployment | Docker Compose Microservices Fleet |

---

### Track 2: V2 Enterprise Cognitive Twin Decisions (013 – 018+)
These decisions govern the industrial-scale expansion over the 30-domain, 49.6K SKU enterprise dataset.

| ADR ID | Title | Status | Scope | Primary Technology / Pattern |
| :--- | :--- | :--- | :--- | :--- |
| **[ADR 013](./013_enterprise_knowledge_fabric_over_monolithic_generator.md)** | Enterprise Knowledge Fabric | **Accepted** | 30 domains, 96 tables, 165 FKs | Persisted Enterprise Data Fabric |
| **[ADR 014](./014_materialized_graph_projection_and_bounded_query_contracts.md)** | Materialized Graph Projection & Bounded Queries | **Accepted** | 3.73M nodes, depth-bounded MCP queries | Read-Only Neo4j Projection |
| **[ADR 015](./015_tripartite_state_isolation_for_benchmark_integrity.md)** | Tripartite State Isolation | **Accepted** | Zero cross-scenario contamination | Layer 1 Frozen / Layer 2 Base / Layer 3 Runtime |
| **[ADR 016](./016_declarative_domain_binding_profiles.md)** | Declarative Domain Binding Profiles | **Accepted** | Operational subset scoping over dataset | Domain Binding Profile Contract |
| **[ADR 017](./017_decoupling_data_domains_from_agent_roster.md)** | Decoupling Data Domains from Agent Roster | **Accepted** | 30 data domains $\ne$ 30 agents | 4 Core Operational Specialists |
| **[ADR 018](./018_cognitive_twin_service_substrate.md)** | Cognitive Twin Service Substrate | **Accepted** | Simulation, lineage, 3-way match, ledger | `twin_service.py` Service Layer |
| **[ADR 019](./019_operational_digital_twin_substrate_layer.md)** | Operational Digital Twin Substrate Layer | **Accepted** | Authoritative cyber-physical state layer | Operational Substrate Above D1/D2 |
| **[ADR 020](./020_tri_zone_query_routing_and_deeper_resolver.md)** | Tri-Zone Query Routing & Deeper Resolver | **Accepted** | Cognitive routing, intent disambiguation | Fast-Path + Deeper Resolver + Fallback |
| **[ADR 021](./021_dynamic_capability_registry_over_static_mcp_endpoints.md)** | Dynamic Capability Registry Over Static MCP | **Accepted** | Dynamic discovery, bounded MCP binding | Declarative Capability Cards |
| **[ADR 022](./022_minimalist_bounded_worker_concurrency.md)** | Minimalist Bounded Worker Concurrency | **Accepted** | Resource containment, predictable latency | 4-Tier Priority Queue + Worker Pool |
| **[ADR 023](./023_event_stepped_simulation_kernel_over_fixed_tick_daemon.md)** | Event-Stepped Simulation Kernel | **Accepted** | Discrete-event clock advance, 100% replay | Event-Stepped DES Engine |
| **[ADR 024](./024_immutable_neo4j_topology_with_in_memory_scenario_overlays.md)** | Immutable Neo4j Topology with Overlays | **Accepted** | Zero graph pollution, concurrent branching | In-Memory Graph Perturbation Masks |
| **[ADR 025](./025_five_tier_state_hierarchy_and_actuation_boundaries.md)** | Five-Tier State Hierarchy & Actuation | **Accepted** | Strict separation of facts vs simulations | 5 Tiers + Gated HITL Actuation |

---

## Template

All future architectural changes should follow the standard [ADR Template](./template.md).

