# Deliverable D02 -- Design Decisions: Enterprise Knowledge & Data Fabric

## 1. Context & Architectural Motivation

In SCOF V1, data storage was simplified: a single PostgreSQL database stored simulation logs alongside a naive flat vector table, while Neo4j had minimal constraints and was vulnerable to unbounded Cypher traversals.

In SCOF V2, scaling to 30 business domains, 49,616 SKUs, 3.73 million graph nodes, and concurrent multi-agent LangGraph workflows requires a disciplined, production-grade Knowledge & Data Fabric. This document details the architectural decisions governing storage separation, graph read-only immutability, bounded MCP tools, semantic memory decoupling, and service encapsulation.

---

## 2. Key Design Decisions

### Decision 1: Relational Primacy over Direct Graph Mutation
- **Choice**: Designate PostgreSQL as the sole transactional System of Record (SoR) ([ADR 001](file:///d:/projects/SCOF_V1/SCOF/docs/adr/001_enterprise_knowledge_fabric_over_monolithic_generator.md)). Neo4j functions strictly as a downstream topological projection derived from the relational database.
- **Rationale**: Graph databases lack robust declarative support for complex multi-table check constraints, double-entry financial ledger validation, and temporal snapshot partitioning. Using the relational schema as the single source of truth guarantees referential integrity, while the graph handles high-performance multi-hop pathfinding.

### Decision 2: Graph Read-Only Immutability with Scenario Masking
- **Choice**: Enforce a strict read-only policy on the Neo4j database during simulation runs ([ADR 006](file:///d:/projects/SCOF_V1/SCOF/docs/adr/006_immutable_neo4j_topology_with_in_memory_scenario_overlays.md)). Disruptions such as severed transport lanes or decommissioned warehouses are never applied via `DELETE` or `SET` Cypher mutations. Instead, queries receive dynamic parameter masks (`$disabled_nodes`, `$disabled_edges`).
- **Rationale**: Mutating the graph during scenario simulations introduces state contamination across concurrent counterfactual branches, invalidates baseline topological caches, and necessitates expensive database rollbacks. Parameter-based masking allows multiple agents to evaluate distinct disruption branches simultaneously over the identical read-only graph.

### Decision 3: Bounded Parameterized MCP Traversal Tools
- **Choice**: Restrict agent access to depth-bounded, parameterized Model Context Protocol (MCP) tools rather than granting arbitrary Cypher execution privileges ([ADR 005b (Amendment)](file:///d:/projects/SCOF_V1/SCOF/docs/adr/005b_amendment_materialized_graph_projection_and_bounded_queries.md)).
- **Rationale**: Over a graph containing 3,728,199 nodes and 2,104,514 edges, an unconstrained LLM-generated Cypher query (such as `MATCH (a)-[*]->(b)`) causes Cartesian explosions, exhausting database memory and hanging the coordination loop. Depth-bounded tools (capped at depth $\le 3$, or $\le 4$ for merchandise hierarchies) guarantee response latencies under $500\text{ ms}$.

### Decision 4: Non-Vectorization of Pure Numerical State
- **Choice**: Strictly prohibit the embedding of dynamic numerical metrics (such as current stock levels, daily sales quantities, unit costs, or GPS coordinates) into the vector store ([ADR 007b (Amendment)](file:///d:/projects/SCOF_V1/SCOF/docs/adr/007b_amendment_durable_semantic_memory_and_evidence_substrate.md)).
- **Rationale**: Vector similarity search is fundamentally unsuitable for exact scalar filtering, threshold checks ($Q \le ROP$), or arithmetic aggregations. Dense vector representations of rapidly fluctuating numbers lead to stale context and hallucinated decisions. Relational SQL queries handle numerical facts; pgvector is reserved exclusively for qualitative knowledge.

### Decision 5: Three-Tier Decoupled Semantic Memory Architecture
- **Choice**: Structure the pgvector schema into three decoupled tables:
  1. `scof.embedding_model`: Model registry tracking model name, dimension (384), and distance metric.
  2. `scof.semantic_document`: Document metadata, canonical text, SHA-256 hash, and provenance IDs.
  3. `scof.semantic_embedding`: Exact vector values linked to model ID and document ID with composite uniqueness.
- **Rationale**: Monolithic schemas that embed vector columns directly in entity tables make model migrations catastrophic, requiring table rewrites. The three-tier model allows multiple embedding models (e.g. `all-MiniLM-L6-v2` alongside specialized models) to coexist and enables re-embedding without data loss.

### Decision 6: Explicit Relational Provenance Linkage
- **Choice**: Require every operational document stored in semantic memory to reference a valid primary key in the relational System of Record (`source_entity_type`, `source_entity_id`).
- **Rationale**: Ungrounded vector databases allow hallucinated memory snippets to propagate unchecked through cognitive agent loops. Enforcing provenance validation (verified in Gate P4) ensures that every retrieved historical precedent is tied to a real historical entity.

### Decision 7: Service Encapsulation via `SemanticMemoryStore`
- **Choice**: Encapsulate all pgvector connections, query formatting, cosine distance operators, and text normalization inside [`SemanticMemoryStore`](file:///d:/projects/SCOF_V1/SCOF/shared/scof_shared/knowledge/semantic_memory_store.py).
- **Rationale**: Direct instantiation of `psycopg` database cursors or raw SQL strings inside cognitive agents violates software layering principles, creates SQL injection vulnerabilities, and couples agent logic to specific database drivers.

### Decision 8: Cypher Batch Staging & Bulk Ingestion Optimization
- **Choice**: Materialize graph data by exporting relational records into 93 specialized CSV files and loading them via Cypher `LOAD CSV WITH HEADERS ... CALL { ... } IN TRANSACTIONS OF 10000 ROWS` ([`import_neo4j_graph.cql`](file:///d:/projects/SCOF_V1/SCOF/datasets/neo4j_graph/import_neo4j_graph.cql)).
- **Rationale**: Ingesting 3.73 million nodes and 2.10 million edges via single-record transactional APIs results in JVM OutOfMemory errors and hours of execution time. Transactional batching processes the entire enterprise graph within minutes while respecting heap constraints.
