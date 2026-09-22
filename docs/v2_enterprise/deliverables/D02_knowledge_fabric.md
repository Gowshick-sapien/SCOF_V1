# Deliverable D02 (V2): Enterprise Knowledge & Data Fabric

## 1. Overview & Objectives

Deliverable D02 transforms from a simple ETL script into the **Enterprise Knowledge & Data Fabric**. It establishes the authoritative data contracts, topological graph projections, and semantic indexing layers for the SCOF platform.

Its primary responsibilities are:
1. **System of Record (PostgreSQL / SQLite):** Housing the authoritative 30 business domains across 96 tables with 165 physical foreign keys.
2. **Materialized Topology Projection (Neo4j):** Serving structural dependency traversals over 3,732,388 nodes and 2,104,188 edges.
3. **Semantic Memory Projection (pgvector):** Storing 384-dimensional embeddings of historical decisions, meeting logs, and precedent cases.
4. **Bounded Query Governance (ADR 014):** Providing agents with depth-bounded, parameterized MCP traversal tools rather than unconstrained Cypher execution.
5. **Graph Immutability Invariant (ADR 024):** Guaranteeing Neo4j remains 100% read-only during scenario simulations, applying topological perturbations via in-memory scenario overlays.
6. **Class A Direct Query Resolution:** Fulfilling read-only operational facts directly to agents in $< 50\text{ ms}$, bypassing the simulation engine.

---

## 2. Component Separation of Concerns

```text
                           DELIVERABLE D02
                     ENTERPRISE KNOWLEDGE FABRIC
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
        ▼                         ▼                         ▼
  PostgreSQL / SQLite           Neo4j                    pgvector
   SYSTEM OF RECORD      TOPOLOGICAL PROJECTION     SEMANTIC PROJECTION
  - Transactional truth  - Bounded graph paths      - Decision similarity
  - Inventory on hand    - Upstream supply lineage  - Case-based reasoning
  - Orders & shipments   - Facility dependencies    - Precedent retrieval
  - General ledgers      - Alternate transit routes - Natural language Q&A
  - Immutable Layer 2    - Read-only baseline       - HNSW indexing
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

### Scenario Overlay Masking Contract:
When a scenario injects severed corridors or disabled facilities, queries pass `$disabled_nodes` and `$disabled_edges` into Cypher parameters without mutating the underlying database ([ADR 024](file:///d:/projects/SCOF_V1/SCOF/docs/adr/024_immutable_neo4j_topology_with_in_memory_scenario_overlays.md)):
```cypher
MATCH path = (origin:Facility)-[:CONNECTS_TO*1..3]->(dest:Facility)
WHERE NONE(node IN nodes(path) WHERE node.facility_id IN $disabled_nodes)
  AND NONE(edge IN relationships(path) WHERE edge.lane_id IN $disabled_edges)
RETURN path
```

---

## 4. Acceptance Criteria & Verification Evidence

1. **Referential Integrity Gate:** 165 physical foreign keys verified with 0 orphan records (Passed 100%).
2. **Graph Materialization Gate:** Exactly 51 Cypher uniqueness constraints verified covering 50 core enterprise labels with 0 constraint violations.
3. **Query Latency Gate:** All bounded MCP traversal queries execute in $< 50\text{ ms}$.
4. **Dual-Master Drift Prevention:** Neo4j materializes strictly via unidirectional synchronization from relational seed.
5. **Graph Immutability Gate:** Re-running simulation scenarios produces 0 node or edge modifications in the Neo4j database.
