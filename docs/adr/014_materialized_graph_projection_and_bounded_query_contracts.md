# ADR 014: Materialized Graph Projection and Bounded Query Contracts

* **Status**: Accepted (Amends ADR 007)
* **Date**: 2026-09-22
* **Deciders**: SCOF Core Architecture Team
* **Consulted**: Knowledge Graph Engineers, Agent Framework Specialists
* **Informed**: Engineering Organization

---

## 1. Context and Problem Statement

In ADR 007, SCOF established a hybrid knowledge layer combining PostgreSQL (relational) and Neo4j (property graph). In V1, the graph contained approximately 20 nodes, making unconstrained Cypher queries trivial.

In V2, the materialized Neo4j property graph scales to **3,732,388 nodes and 2,104,188 edges** across 59 schema constraints. If autonomous LLM agents (D3/D4) are granted direct, unconstrained Cypher query capabilities, multi-hop traversals with unbounded depth (e.g., `MATCH (s:Store)-[*1..5]-(x) RETURN x`) will cause query timeouts, exhaust graph server RAM, and violate SCOF's sub-second ($< 500\text{ ms}$) decision SLA. Furthermore, treating Neo4j as an independent read-write operational store introduces dual-master consistency drift between relational tables and graph entities.

---

## 2. Decision Drivers

* **Sub-Second SLA Guarantee:** Prevent autonomous LLM agents from issuing pathological or unconstrained Cypher traversals.
* **Single Source of Truth:** Guarantee that relational PostgreSQL/SQLite remains the authoritative system of record for all transactional facts and states.
* **Query Safety & Determinism:** Expose safe, parameterized, depth-bounded retrieval tools to specialist agents via Model Context Protocol (MCP).

---

## 3. Considered Options

* **Option 1 (Unconstrained Agent Cypher Execution):** Provide agents with direct Cypher execution tools and let LLMs construct dynamic graph queries.
* **Option 2 (Dual Master Relational & Graph):** Treat Neo4j as an independent operational database where agents write graph state directly.
* **Option 3 (Materialized Graph Projection with Bounded MCP Contracts):** Enforce that Neo4j is strictly a unidirectional, read-only materialized projection of the relational world, and restrict all agent access to parameterized, depth-bounded MCP query functions.

---

## 4. Decision Outcome

**Chosen Option**: **Option 3: Materialized Graph Projection with Bounded MCP Contracts**

### Rationale:
* **Relational Primacy:** PostgreSQL/SQLite owns all transactional facts, inventory balances, purchase orders, receipts, and timestamps. Neo4j materializes strictly from the relational tables.
* **Bounded Query Governance:** Agents are **never** permitted to execute arbitrary Cypher strings. Instead, the D2 Knowledge Fabric exposes bounded, high-performance traversal tools:
  * `get_upstream_supply_path(sku_id, store_id, max_depth=3)`
  * `get_affected_downstream_facilities(facility_id, max_hops=2)`
  * `find_alternate_carrier_routes(origin_id, dest_id, max_transit_days=5)`
* **Pre-Compiled Indexing:** Traversals execute strictly against indexed primary keys and foreign keys backed by 51 core Cypher uniqueness constraints, guaranteeing sub-50ms graph response times.

---

## 5. Pros and Cons of the Selected Option

### Positive Consequences:
* Eliminates the risk of catastrophic unconstrained graph traversals and memory exhaustion.
* Guarantees zero consistency drift between relational tables and graph projections.
* Simplifies agent prompt context; agents invoke high-level domain tools rather than needing to reason about complex Cypher syntax.

### Negative Consequences / Trade-offs:
* Requires maintaining explicit MCP wrapper functions for new graph traversal patterns.
* Graph mutations during simulation must be staged via relational state snapshots rather than in-place graph writes.

---

## 6. Implementation & Compliance Notes

* **Graph Materialization:** Executed via `scripts/materialize_neo4j_graph.py` and governed by `scripts/neo4j_schema_ddl.cql`.
* **Graph Specification:** Documented in `docs/v2_enterprise/ontology/SCOF_Neo4j_Graph_Specification.md`.
* **MCP Bounded Tool Contracts:** Defined in `docs/v2_enterprise/contracts/bounded_mcp_tools_spec.md`.
