ADR 006: Immutable Neo4j Topology with In-Memory Scenario Overlays

* **Status**: Accepted

---


## 1. Context and Problem Statement

The SCOF Enterprise Reference World includes a Neo4j property graph containing **3,732,388 nodes and 2,104,188 edges**.

During scenario simulation, agents must evaluate structural network disruptions:
* A major transport corridor is closed due to a weather disaster (severed edge).
* A regional distribution center is offline due to a facility strike (disabled node).
* A carrier transit lane suffers severe congestion (modified edge weight).

If these scenario modifications are written directly to the database (`DELETE edge`, `SET status = 'offline'`), the database suffers dirty writes, cross-scenario state pollution, lock contention, and loss of the Day-0 ground truth topology. Conversely, cloning a 3.73M-node database per scenario is completely unviable.

---

## 2. Decision Drivers

* **Zero Graph Pollution:** Guaranteed 100% preservation of the clean Day-0 enterprise topology.
* **Concurrent Scenario Scalability:** Allowing multiple concurrent scenarios to evaluate conflicting topological perturbations simultaneously.
* **Sub-50ms Graph Traversal SLA:** Bounded graph traversals must remain lightning fast without database lock contention.
* **Storage & Memory Efficiency:** Eliminating heavy disk cloning or database replication.

---

## 3. Considered Options

* **Option 1 -- Direct Neo4j Graph Mutations:** Mutate the graph directly via Cypher during scenario simulation and attempt to rollback changes upon scenario teardown.
* **Option 2 -- Physical Neo4j Database Cloning:** Duplicate the Neo4j database or create separate graph databases per scenario.
* **Option 3 -- Immutable Neo4j Topology with In-Memory Scenario Overlays:** Treat the Neo4j database as 100% read-only. Scenario network perturbations are captured as lightweight in-memory overlay filters in the active `ScenarioContext`. Bounded Cypher queries apply parameter masks over the immutable baseline graph.

---

## 4. Decision Outcome

**Chosen Option**: **Option 3 -- Immutable Neo4j Topology with In-Memory Scenario Overlays**

### Rationale:
1. **Absolute Immutability:** No Cypher `CREATE`, `SET`, or `DELETE` statement is ever executed against the Neo4j database during scenario runs or agent deliberation.
2. **Lightweight Overlays:** A scenario perturbation requires only a few bytes in memory:
   - `disabled_nodes: set[str]`
   - `disabled_edges: set[str]`
   - `edge_weight_modifiers: dict[str, float]`
3. **Query-Time Bounded Masking:** Standard bounded MCP graph traversal queries accept `$disabled_nodes` and `$disabled_edges` as parameters, dynamically masking blocked corridors during traversal:
   ```cypher
   MATCH path = (origin:Facility)-[:CONNECTS_TO*1..3]->(dest:Facility)
   WHERE NONE(node IN nodes(path) WHERE node.facility_id IN $disabled_nodes)
     AND NONE(edge IN relationships(path) WHERE edge.lane_id IN $disabled_edges)
   RETURN path
   ```
4. **Infinite Concurrent Isolation:** A hundred simultaneous scenarios can simulate conflicting road closures without interfering with each other or locking the database.

---

## 5. Pros and Cons of the Selected Option

### Positive Consequences:
* Eliminates the risk of dirty database writes or corrupted topology baselines.
* Zero storage overhead; instant scenario creation and teardown ($< 1\text{ ms}$).
* Enables non-blocking, highly parallel Cypher read queries.
* Maintains strict compliance with ADR ADR 002 Tripartite State Isolation.

### Negative Consequences / Trade-offs:
* All MCP Cypher traversal queries must adhere to the standardized overlay filtering contract.
* Enforced via centralized parameter injection in the Knowledge Fabric MCP gateway.

---

## 6. Implementation & Compliance Notes

* Architectural specification in [State Isolation & Evidence Fabric Architecture](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/architecture/05_state_isolation_and_evidence_fabric.md).
* Integrated into graph query templates in Deliverable [D02](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/deliverables/D02_knowledge_fabric.md).
* Verified by graph isolation tests ensuring zero graph mutation during disruption runs in Deliverable [D10](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/deliverables/D10_benchmarking_evaluation_v2.md).

---

## 7. Related Decisions & Artifacts

* [ADR ADR 005: Hybrid Knowledge Layer Neo4j Postgres](file:///d:/projects/SCOF_V1/SCOF/docs/adr/005_hybrid_knowledge_layer_neo4j_postgres.md)
* [ADR ADR 005 (Amendment): Materialized Graph Projection and Bounded Query Contracts](file:///d:/projects/SCOF_V1/SCOF/docs/adr/005b_amendment_materialized_graph_projection_and_bounded_queries.md)
* [ADR ADR 002: Tripartite State Isolation for Benchmark Integrity](file:///d:/projects/SCOF_V1/SCOF/docs/adr/002_tripartite_state_isolation_for_benchmark_integrity.md)
* [State Isolation Architecture Specification](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/architecture/05_state_isolation_and_evidence_fabric.md)
