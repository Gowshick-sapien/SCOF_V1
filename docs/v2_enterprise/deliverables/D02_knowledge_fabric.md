# Deliverable D02 (V2): Enterprise Knowledge & Data Fabric

## 1. Overview & Objectives

Deliverable D02 establishes the **Enterprise Knowledge & Data Fabric**, defining the authoritative data contracts, topological graph projections, and semantic memory layers for the SCOF platform.

Its primary responsibilities are:
1. **System of Record (PostgreSQL):** Housing the authoritative 30 business domains across 96 tables with 165 physical foreign keys and 4.36M relational rows. (SQLite serves as the dedicated local development and smoke-test harness).
2. **Materialized Topology Projection (Neo4j):** Serving structural dependency traversals over 3,728,199 materialized nodes, 2,104,514 relationships, and 59 schema constraints.
3. **Semantic Memory Substrate (pgvector):** Storing 384-dimensional embeddings of historical disruption scenarios, agent evidence claims, decision rationales, CD2F consensus explanations, and dynamic capability cards.
4. **Bounded Query Governance (ADR ADR 005 (Amendment)):** Providing agents with depth-bounded, parameterized MCP traversal tools rather than unconstrained Cypher execution.
5. **Graph Immutability Invariant (ADR ADR 006):** Guaranteeing Neo4j remains 100% read-only during scenario simulations, applying topological perturbations via in-memory scenario overlays.
6. **Class A Direct Query Resolution:** Fulfilling read-only operational facts directly to agents in $< 50\text{ ms}$, bypassing the simulation engine.
7. **Safe Service Encapsulation (ADR ADR 007 (Amendment)):** Providing specialist agents with [SemanticMemoryStore](file:///d:/projects/SCOF_V1/SCOF/shared/scof_shared/knowledge/semantic_memory_store.py) to prevent raw SQL or vector parameter handling in cognitive agents.

---

## 2. Component Separation of Concerns

```text
                           DELIVERABLE D02
                     ENTERPRISE KNOWLEDGE FABRIC
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
        ▼                         ▼                         ▼
   PostgreSQL                   Neo4j                    pgvector
SYSTEM OF RECORD          TOPOLOGICAL PROJECTION     SEMANTIC MEMORY SUBSTRATE
"WHAT IS TRUE?"           "HOW ARE CONNECTED?"      "WHAT IS SIMILAR?"
- 30 Business Domains     - 3,728,199 Nodes          - 384d Cosine Similarity
- 96 Relational Tables    - 2,104,514 Edges          - Immutable Model Identity
- 165 Foreign Keys        - 59 Schema Constraints    - Multi-run Provenance
- 4.36M Relational Rows   - Bounded path tools (<=3) - Exact Nearest Neighbor
- Transactional truth     - Read-only baseline       - SemanticMemoryStore
```

---

## 3. Bounded Query Contracts & Scenario Masking

To protect the sub-second ($< 500\text{ ms}$) SLA and prevent server memory exhaustion over 3.73M nodes, all graph interactions are governed by bounded contracts:

| Bounded Tool | Maximum Bound | What It Traverses | Primary Consumer |
| :--- | :--- | :--- | :--- |
| `get_upstream_supply_path` | `max_depth = 3` | `(:Store) <-[:SERVICED_BY]- (:DC) <-[:SUPPLIED_BY]- (:Supplier)` | Transport Agent, Supplier Agent |
| `get_affected_downstream_facilities` | `max_hops = 2` | `(:DisruptedFacility) -[:SHIPS_TO]-> (:Store)` | Inventory Agent, Coordinator |
| `find_alternate_carrier_routes` | `max_transit_days = 5` | Alternate `(:TransportLane)` connecting origin to destination | Transport Agent |
| `get_category_assortment_tree` | `max_depth = 4` | `(:Department) -> (:Category) -> (:Subcategory) -> (:Family)` | Demand Agent |

### Scenario Overlay Masking Contract
When a scenario injects severed corridors or disabled facilities, queries pass `$disabled_nodes` and `$disabled_edges` into Cypher parameters without mutating the underlying database ([ADR ADR 006](file:///d:/projects/SCOF_V1/SCOF/docs/adr/006_immutable_neo4j_topology_with_in_memory_scenario_overlays.md)):
```cypher
MATCH path = (origin:Facility)-[:CONNECTS_TO*1..3]->(dest:Facility)
WHERE NONE(node IN nodes(path) WHERE node.facility_id IN $disabled_nodes)
  AND NONE(edge IN relationships(path) WHERE edge.lane_id IN $disabled_edges)
RETURN path
```

---

## 4. Semantic Memory Substrate Specification (ADR ADR 007 (Amendment))

### 4.1 Schema Architecture
* **`scof.embedding_model`:** Immutable registry (`model_id` formatted as `model_name@version`). Frozen to 384 dimensions and cosine metric.
* **`scof.semantic_document`:** Stable composite identity (`SD-{type[:3]}-{hash[:12]}`) incorporating `run_id`, `scenario_id`, `source_entity_type`, `source_entity_id`, and `agent_id`. Decoupled from `content_hash`.
* **`scof.semantic_embedding`:** Versioned vectors (`vector(384)`) with `embedding_version`, `is_current`, and row-locking concurrency protection.

### 4.2 Non-Vectorization Invariant
The 96 relational tables (4.36M rows) remain strictly structured. Only high-entropy contextual artifacts (scenarios, evidence claims, decision rationales, consensus explanations, capability cards) are indexed into the semantic vector substrate.

---

## 5. Acceptance Criteria & Verification Evidence

### Relational & Graph Gates
1. **Referential Integrity Gate:** 165 physical foreign keys verified with 0 orphan records (Passed 100%).
2. **Graph Materialization Gate:** Exactly 59 Cypher constraints verified covering 50 core enterprise labels with 0 constraint violations across 3,728,199 nodes and 2,104,514 edges.
3. **Query Latency Gate:** All bounded MCP traversal queries execute in $< 50\text{ ms}$.
4. **Dual-Master Drift Prevention:** Neo4j materializes strictly via unidirectional synchronization from relational seed.
5. **Graph Immutability Gate:** Re-running simulation scenarios produces 0 node or edge modifications in the Neo4j database.

### Semantic Memory Gates (Scripts: `verify_pgvector_d2.py`, `test_semantic_memory.py`)
6. **Gate P3 (Dimension Invariant):** Vector dimensionality physically verified at 384d.
7. **Gate P4 (Provenance Linkage):** 100% of operational evidence records resolve to real relational entities (`supplier_profile`, `facility`, `purchase_order`, `scenario`).
8. **Gate P7 (Semantic Retrieval Quality):** Benchmark query retrieves Target artifact at Rank #1, strictly exceeding hard negative alternatives and beating distant negative by margin $\delta \ge 0.25$.
9. **Gate P8 (Encapsulation):** Specialist agents interact 100% through [SemanticMemoryStore](file:///d:/projects/SCOF_V1/SCOF/shared/scof_shared/knowledge/semantic_memory_store.py).
