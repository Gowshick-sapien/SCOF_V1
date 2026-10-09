# Deliverable D02 -- Enterprise Knowledge & Data Fabric

## Overview & Purpose

Deliverable D02 establishes the **Enterprise Knowledge & Data Fabric** for the Supply Chain Cognitive Orchestration Framework (SCOF) V2. Replacing the toy single-database setup of V1, D02 implements a production-grade tri-store architecture providing:
1. **Relational System of Record (PostgreSQL)**: Transactional ground truth across 30 business domains, 96 tables, 165 physical foreign keys, and 4.36 million relational records.
2. **Materialized Topological Projection (Neo4j)**: High-speed structural graph traversals over 3,728,199 nodes, 2,104,514 relationships, and 59 schema constraints.
3. **Semantic Memory Substrate (pgvector)**: 384-dimensional vector retrieval for historical disruption scenarios, agent evidence claims, decision rationales, CD2F consensus logs, and capability cards.

D02 guarantees that downstream specialist agents (D03, D04), LangGraph orchestration pipelines (D05), and CD2F consensus arbitration (D06) access structured, topological, and qualitative memory with bounded execution latency ($< 500\text{ ms}$).

---

## Requirements Summary

- **ER-2.1 (Tri-Store Separation of Concerns)**: Strictly partition storage concerns: PostgreSQL for transactional facts ("What is true?"), Neo4j for topological network dependencies ("How are entities connected?"), and pgvector for semantic retrieval ("What historical situations are similar?").
- **ER-2.2 (Materialized Enterprise Graph)**: Project the enterprise supply chain network into Neo4j with 50 node labels, 59 schema constraints, and 2.10M relationships across suppliers, DCs, retail stores, lanes, and merchandise taxonomies.
- **ER-2.3 (Read-Only Graph Immutability & Scenario Overlays)**: Enforce the graph immutability invariant ([ADR 006](file:///d:/projects/SCOF_V1/SCOF/docs/adr/006_immutable_neo4j_topology_with_in_memory_scenario_overlays.md)), keeping the Neo4j database strictly read-only and evaluating disruptions via parameter-masked scenario overlays.
- **ER-2.4 (Bounded MCP Traversal Tools)**: Expose depth-bounded, parameterized Model Context Protocol (MCP) tools rather than unconstrained Cypher execution ([ADR 005b (Amendment)](file:///d:/projects/SCOF_V1/SCOF/docs/adr/005b_amendment_materialized_graph_projection_and_bounded_queries.md)) to prevent server memory exhaustion.
- **ER-2.5 (Three-Tier Semantic Memory Schema)**: Implement the decoupled pgvector schema in PostgreSQL (`scof.embedding_model`, `scof.semantic_document`, `scof.semantic_embedding`) supporting 384-dimensional cosine similarity and immutable model versioning.
- **ER-2.6 (Safe Service Encapsulation)**: Encapsulate all semantic retrieval operations within [`SemanticMemoryStore`](file:///d:/projects/SCOF_V1/SCOF/shared/scof_shared/knowledge/semantic_memory_store.py), prohibiting raw SQL or embedding parameter manipulation inside cognitive agents ([ADR 007b (Amendment)](file:///d:/projects/SCOF_V1/SCOF/docs/adr/007b_amendment_durable_semantic_memory_and_evidence_substrate.md)).

---

## Prerequisites & Dependencies

- **Prerequisite Deliverables**: Deliverable D01 (Enterprise World & Simulation Foundation) is complete. Relational datasets in [`datasets/scof_relational.db`](file:///d:/projects/SCOF_V1/SCOF/datasets/scof_relational.db) are validated and certified.
- **Required System Tools**: Python 3.11+, PostgreSQL 16+ (with `pgvector` extension), Neo4j 5+ Community/Enterprise, SQLite 3.40+.
- **Authoritative Dataset & Schema Artifacts**:
  - Relational Database Harness: [`datasets/scof_relational.db`](file:///d:/projects/SCOF_V1/SCOF/datasets/scof_relational.db)
  - Neo4j Import Script: [`datasets/neo4j_graph/import_neo4j_graph.cql`](file:///d:/projects/SCOF_V1/SCOF/datasets/neo4j_graph/import_neo4j_graph.cql)
  - Neo4j Graph CSV Exports: [`datasets/neo4j_graph/`](file:///d:/projects/SCOF_V1/SCOF/datasets/neo4j_graph/) (93 CSV files)
  - Graph Materialization Audit: [`datasets/neo4j_materialization_audit.json`](file:///d:/projects/SCOF_V1/SCOF/datasets/neo4j_materialization_audit.json)
  - pgvector Verification Suite: [`scripts/verify_pgvector_d2.py`](file:///d:/projects/SCOF_V1/SCOF/scripts/verify_pgvector_d2.py)

---

## Document Set in this Directory

1. **[`README.md`](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/deliverables/D02_knowledge_fabric/README.md)** (this document): Overview, requirements, prerequisites, document map, and acceptance criteria.
2. **[`implementation_plan.md`](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/deliverables/D02_knowledge_fabric/implementation_plan.md)**: Phased implementation tracks (PostgreSQL, Neo4j, pgvector substrate), ETL pipelines, and verification strategy.
3. **[`design_decisions.md`](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/deliverables/D02_knowledge_fabric/design_decisions.md)**: Architectural design decisions covering relational primacy, read-only graph projections, bounded MCP tools, non-vectorization invariant, and service encapsulation.
4. **[`graph_schema.md`](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/deliverables/D02_knowledge_fabric/graph_schema.md)**: Comprehensive Neo4j schema specification: 50 node labels, 59 constraints, relationship types, edge properties, and bounded Cypher traversal contracts.
5. **[`vector_schema.md`](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/deliverables/D02_knowledge_fabric/vector_schema.md)**: Comprehensive PostgreSQL pgvector schema: 3-tier DDL, 384d cosine metric, model registry, document canonicalization, and `SemanticMemoryStore` API.
6. **[`acceptance_evidence.md`](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/deliverables/D02_knowledge_fabric/acceptance_evidence.md)**: Empirical test logs, Gate 6 Graph Parity audit, Gates P1-P8 verification matrix, and semantic benchmark results.
7. **[`walkthrough.md`](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/deliverables/D02_knowledge_fabric/walkthrough.md)**: Complete step-by-step walkthrough guide for materializing the graph, running pgvector verification, and testing memory APIs.

---

## Module Structure

```text
shared/scof_shared/
    knowledge/
        embedding_config.py            # Model registry & YAML configuration loader
        embedding_provider.py          # SentenceTransformers & Mock providers (384d)
        semantic_memory_store.py       # High-level SemanticMemoryStore encapsulation API
        graph_client.py                # Bounded Neo4j Cypher traversal client
        vector_client.py               # Low-level PostgreSQL pgvector connection wrapper

services/etl/src/
    load_postgresql_data.py            # High-throughput SQLite-to-PostgreSQL ETL loader
    materialize_neo4j_graph.py         # CSV exporter & Neo4j batch materializer
    seed_semantic_memory.py            # Semantic memory corpus generator & relational validator

datasets/neo4j_graph/
    import_neo4j_graph.cql             # 59 Cypher constraints & LOAD CSV commands
    *.csv                              # 93 node and relationship CSV files (3.73M nodes)

scripts/
    verify_pgvector_d2.py              # Automated 8-gate pgvector verification suite
    validate_operational_gates.py      # Automated 6-gate operational validation harness
```

---

## Acceptance Criteria

- **AC-1 (Tri-Store Separation)**: Physical storage separation established between PostgreSQL (SoR), Neo4j (Topology), and pgvector (Semantic Memory).
- **AC-2 (PostgreSQL Schema Staging)**: 96 tables and 165 foreign keys mapped and ready for production ingest with zero schema discrepancies.
- **AC-3 (Neo4j Topology Materialization)**: 3,728,199 nodes, 2,104,514 edges, and 59 schema constraints materialized with zero parity mismatches.
- **AC-4 (Graph Immutability & Scenario Masking)**: Graph database verified as read-only during scenario execution with parameter-based filtering.
- **AC-5 (Bounded Traversal Contracts)**: MCP traversal tools strictly capped at depth $\le 3$ (or $\le 4$ for merchandise trees) with $< 500\text{ ms}$ response times.
- **AC-6 (pgvector 3-Tier Architecture)**: Active vector extension, 384-dimensional cosine embedding column, and model registry verified.
- **AC-7 (Relational Provenance Linkage)**: 100% of seeded semantic memory documents resolve to valid relational records in the System of Record.
- **AC-8 (Service Encapsulation & Benchmark)**: `SemanticMemoryStore` encapsulates all database operations; semantic benchmark confirms Target rank #1 with separation delta $\ge 0.25$ over distant negatives.
