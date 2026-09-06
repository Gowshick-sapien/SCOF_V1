# SCOF Architecture Decision Records (ADRs)

This directory contains the formal **Architecture Decision Records (ADRs)** for the **Supply Chain Cognitive Orchestration Framework (SCOF)**. Each document captures a critical architectural choice, the problem context, considered alternatives, selection rationale, and operational consequences.

---

## Architecture Decision Index

| ADR ID | Title | Status | Scope | Primary Technology / Pattern |
| :--- | :--- | :--- | :--- | :--- |
| **[ADR 001](./001_langgraph_orchestration_kernel.md)** | Orchestration Kernel Selection | **Accepted** | Multi-agent coordination, state machines, cyclic loops | LangGraph StateGraph |
| **[ADR 002](./002_apache_kafka_event_streaming.md)** | Message Streaming Bus Selection | **Accepted** | Disruption event distribution, audit logs, replay | Apache Kafka (KRaft) |
| **[ADR 003](./003_pgvector_for_semantic_memory.md)** | Vector Database Selection | **Accepted** | Semantic embeddings, historical RAG retrieval | PostgreSQL 16 + pgvector |
| **[ADR 004](./004_cd2f_consensus_arbitration.md)** | Consensus Arbitration Framework | **Accepted** | Multi-agent claim weighting, deadlock elimination | CD²F Dynamic Arbitration Engine |
| **[ADR 005](./005_dual_path_execution_routing.md)** | Execution Routing Strategy | **Accepted** | Sub-second SLA vs. high-risk safety guardrails | Fast-Path vs. Slow-Path / HITL Gating |
| **[ADR 006](./006_mcp_and_a2a_protocol_standardization.md)** | Protocol Standardization | **Accepted** | Tool interfaces and inter-agent discovery | Model Context Protocol (MCP) & A2A |
| **[ADR 007](./007_hybrid_knowledge_layer_neo4j_postgres.md)** | Hybrid Knowledge Layer Architecture | **Accepted** | Multi-tier network graph + transactional state | Neo4j 5.18 + PostgreSQL 16 |
| **[ADR 008](./008_tauri_v2_desktop_operations_console.md)** | Desktop Operations Console Architecture | **Accepted** | Native control room desktop shell and UI | Tauri v2 + React 19 + Apple HIG |
| **[ADR 009](./009_declarative_yaml_domain_profiles.md)** | Declarative Domain Profile Architecture | **Accepted** | Domain-agnostic multi-vertical extensibility | YAML Profile Configurations (`profiles/`) |
| **[ADR 010](./010_redis_realtime_state_caching.md)** | Real-Time State Caching & WebSockets | **Accepted** | Ephemeral dashboard state, WebSocket streaming | Redis 7 Alpine |
| **[ADR 011](./011_empirical_evaluation_cohens_kappa.md)** | Empirical Evaluation & Calibration | **Accepted** | Statistical reliability vs. subjective grading | Cohen's Kappa ($\kappa$) + Benchmark Suite |
| **[ADR 012](./012_containerized_polyglot_microservices.md)** | Service Fleet Isolation & Packaging | **Accepted** | Process boundary isolation, local deployment | Docker Compose Microservices Fleet |

---

## Template

All future architectural changes should follow the standard [ADR Template](./template.md).
