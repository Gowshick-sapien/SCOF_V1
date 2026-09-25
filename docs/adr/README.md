# SCOF Architecture Decision Records (ADRs)

This directory contains the formal, sequentially tracked **Architecture Decision Records (ADRs)** for the **Supply Chain Cognitive Orchestration Framework (SCOF)**.

Each record documents an architectural choice, problem context, evaluated trade-offs, decision rationale, and operational consequences across the 30-domain, 96-table, 49,616-SKU retail enterprise platform.

---

## Architectural Decision Structure

The decisions are structured into eight cohesive architectural layers, establishing an end-to-end flow from foundational world modeling to authoritative substrates, simulation engines, protocol discovery, cognitive orchestration, consensus arbitration, real-time streaming, and operational interfaces.

Amended architectural decisions retain their base ADR identifier with a structured `b_amendment_` filename indicator to guarantee natural sequential reading and historical provenance.

---

## Architecture Decision Index

### Tier 1: Foundations & World Modeling
Enterprise data fabric, state isolation, domain decoupling, and operational binding profiles.

| ADR ID | Title | Status | Scope | Primary Technology / Pattern |
| :--- | :--- | :--- | :--- | :--- |
| **[ADR 001](./001_enterprise_knowledge_fabric_over_monolithic_generator.md)** | Enterprise Knowledge Fabric over Monolithic Synthetic Generator | **Accepted (Supersedes V1 D01/D02 Toy Generator Scope)** | 30 domains, 96 tables, 165 FKs, reference world | Enterprise Data Fabric & Immutability |
| **[ADR 002](./002_tripartite_state_isolation_for_benchmark_integrity.md)** | Tripartite State Isolation for Benchmark and Simulation Integrity | **Accepted** | Zero cross-scenario contamination | Layer 1 Frozen / Layer 2 Base / Layer 3 Runtime |
| **[ADR 003](./003_decoupling_data_domains_from_agent_roster.md)** | Decoupling Enterprise Data Domains from Multi-Agent Operational Roster | **Accepted** | 30 data domains != 30 agents | 4 Core Operational Specialists |
| **[ADR 004](./004_declarative_yaml_domain_profiles.md)** | Declarative YAML Profiles vs. Hardcoded Business Logic | **Amended by ADR 004 (Amendment)** | Multi-vertical extensibility | Declarative YAML Profile Packages |
| **[ADR 004 (Amendment)](./004b_amendment_declarative_domain_binding_profiles.md)** | Declarative Domain Binding Profiles over Procedural World Generators | **Accepted (Amends ADR 004)** | Operational subset scoping over dataset | Domain Binding Profile Contract |

---

### Tier 2: Authoritative Substrates & Knowledge Layer
PostgreSQL system of record, Neo4j graph topology, durable pgvector semantic memory, and digital twin substrates.

| ADR ID | Title | Status | Scope | Primary Technology / Pattern |
| :--- | :--- | :--- | :--- | :--- |
| **[ADR 005](./005_hybrid_knowledge_layer_neo4j_postgres.md)** | Hybrid Graph (Neo4j) + Relational/Vector (PostgreSQL) vs. Monolithic Store | **Amended by ADR 005 (Amendment)** | Network graph + transactional state | Neo4j 5.18 + PostgreSQL 16 |
| **[ADR 005 (Amendment)](./005b_amendment_materialized_graph_projection_and_bounded_queries.md)** | Materialized Graph Projection and Bounded Query Contracts | **Accepted (Amends ADR 005)** | 3.73M nodes, depth-bounded MCP queries | Read-Only Neo4j Projection |
| **[ADR 006](./006_immutable_neo4j_topology_with_in_memory_scenario_overlays.md)** | Immutable Neo4j Topology with In-Memory Scenario Overlays | **Accepted** | Zero graph pollution, concurrent branching | In-Memory Graph Perturbation Masks |
| **[ADR 007](./007_pgvector_for_semantic_memory.md)** | pgvector vs. Dedicated Vector DBs (Pinecone, Weaviate, Qdrant) | **Amended by ADR 007 (Amendment)** | Semantic embeddings, historical RAG | PostgreSQL 16 + pgvector |
| **[ADR 007 (Amendment)](./007b_amendment_durable_semantic_memory_and_evidence_substrate.md)** | Durable Semantic-Memory and Evidence Substrate | **Accepted (Amends ADR 007 and ADR 005)** | Three-tier pgvector schema, model registry, versioning | pgvector + SemanticMemoryStore |
| **[ADR 008](./008_operational_digital_twin_substrate_layer.md)** | Operational Digital Twin Substrate Layer Above D1 and D2 | **Accepted** | Authoritative cyber-physical state layer | Operational Substrate Above D1/D2 |
| **[ADR 009](./009_cognitive_twin_service_substrate.md)** | Cognitive Twin Service Layer as Programmatic Simulation and Audit Substrate | **Accepted** | Simulation, lineage, 3-way match, ledger | twin_service.py Service Layer |

---

### Tier 3: Simulation Kernel & Concurrency Management
Discrete-event simulation engine, temporal clock advance, and 4-tier bounded worker concurrency.

| ADR ID | Title | Status | Scope | Primary Technology / Pattern |
| :--- | :--- | :--- | :--- | :--- |
| **[ADR 010](./010_event_stepped_simulation_kernel_over_fixed_tick_daemon.md)** | Event-Stepped Simulation Kernel Over Fixed-Tick Daemon | **Accepted** | Discrete-event clock advance, 100% replay | Event-Stepped DES Engine |
| **[ADR 011](./011_minimalist_bounded_worker_concurrency.md)** | Minimalist Bounded Worker Concurrency Model | **Accepted** | Resource containment, predictable latency | 4-Tier Priority Queue + Worker Pool |

---

### Tier 4: Protocol Standardization & Dynamic Capabilities
Model Context Protocol (MCP), Agent-to-Agent (A2A), and declarative Dynamic Capability Registry.

| ADR ID | Title | Status | Scope | Primary Technology / Pattern |
| :--- | :--- | :--- | :--- | :--- |
| **[ADR 012](./012_mcp_and_a2a_protocol_standardization.md)** | Model Context Protocol (MCP) and Agent-to-Agent (A2A) vs. Proprietary REST/RPC | **Amended by ADR 012 (Amendment)** | Tool interfaces and agent discovery | Model Context Protocol & A2A |
| **[ADR 012 (Amendment)](./012b_amendment_dynamic_capability_registry_over_static_mcp.md)** | Dynamic Capability Registry Over Static MCP Endpoints | **Accepted (Amends ADR 012)** | Dynamic discovery, bounded MCP binding | Declarative Capability Cards |

---

### Tier 5: Query Routing & Multi-Agent Orchestration
Tri-zone cognitive query routing and LangGraph StateGraph coordinator.

| ADR ID | Title | Status | Scope | Primary Technology / Pattern |
| :--- | :--- | :--- | :--- | :--- |
| **[ADR 013](./013_tri_zone_query_routing_and_deeper_resolver.md)** | Tri-Zone Query Routing and Deeper Resolver Pipeline | **Accepted** | Cognitive routing, intent disambiguation | Fast-Path + Deeper Resolver + Fallback |
| **[ADR 014](./014_langgraph_orchestration_kernel.md)** | LangGraph vs. CrewAI, AutoGen, and Semantic Kernel | **Accepted** | Multi-agent coordination, state machines | LangGraph StateGraph |

---

### Tier 6: Consensus, Arbitration & Actuation Boundaries
CD2F continuous arbitration, dual-path execution gating, and five-tier state actuation boundaries.

| ADR ID | Title | Status | Scope | Primary Technology / Pattern |
| :--- | :--- | :--- | :--- | :--- |
| **[ADR 015](./015_cd2f_consensus_arbitration.md)** | CD2F Dynamic Continuous Weighting vs. Majority Voting & LLM-as-a-Judge | **Accepted** | Claim weighting, deadlock elimination | CD2F Dynamic Arbitration Engine |
| **[ADR 016](./016_dual_path_execution_routing.md)** | Dual-Path Gating (Fast-Path vs. Slow-Path / Human Escalation) | **Accepted** | Sub-second SLA vs. risk guardrails | Fast-Path vs. Slow-Path / HITL |
| **[ADR 017](./017_five_tier_state_hierarchy_and_actuation_boundaries.md)** | Five-Tier State Hierarchy and Actuation Boundaries | **Accepted** | Strict separation of facts vs simulations | 5 Tiers + Gated HITL Actuation |

---

### Tier 7: Event Streaming & Real-Time Caching
Apache Kafka disruption streaming, event replay, and Redis WebSocket state caching.

| ADR ID | Title | Status | Scope | Primary Technology / Pattern |
| :--- | :--- | :--- | :--- | :--- |
| **[ADR 018](./018_apache_kafka_event_streaming.md)** | Apache Kafka vs. RabbitMQ and Redis Pub/Sub | **Accepted** | Disruption distribution, replay | Apache Kafka (KRaft) |
| **[ADR 019](./019_redis_realtime_state_caching.md)** | Redis vs. Direct PostgreSQL Polling | **Accepted** | Ephemeral state, WebSocket streaming | Redis 7 Alpine |

---

### Tier 8: Presentation, Packaging & Empirical Validation
Tauri v2 native desktop console, polyglot microservice fleet, and Cohen's Kappa ground-truth evaluation.

| ADR ID | Title | Status | Scope | Primary Technology / Pattern |
| :--- | :--- | :--- | :--- | :--- |
| **[ADR 020](./020_tauri_v2_desktop_operations_console.md)** | Tauri v2 + React 19 + Apple HIG vs. Electron and Pure Web App | **Accepted** | Native control room desktop shell | Tauri v2 + React 19 + Apple HIG |
| **[ADR 021](./021_containerized_polyglot_microservices.md)** | Polyglot Containerized Microservices vs. Monolithic Deployment | **Accepted** | Boundary isolation, local deployment | Docker Compose Microservices Fleet |
| **[ADR 022](./022_empirical_evaluation_cohens_kappa.md)** | Cohen's Kappa & Ground Truth vs. Subjective LLM-as-a-Judge | **Accepted** | Statistical reliability vs. grading | Cohen's Kappa + Benchmark Suite |

---

## Template

All future architectural decisions and amendments must follow the standard [ADR Template](./template.md).
