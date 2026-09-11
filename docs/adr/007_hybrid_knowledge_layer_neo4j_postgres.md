# ADR 007: Knowledge Layer Architecture — Hybrid Graph (Neo4j) + Relational/Vector (PostgreSQL) vs. Monolithic Store

---

## 1. Context and Problem Statement

Supply chain operations encompass two distinct data models with opposing computational access patterns:
1. **Topological & Dependency Graphs**: Deep, multi-tier relationship traversals: Bill-of-Materials (BOM) parent-child explosion, multi-echelon warehouse supplier links, and transportation corridors across hubs.
2. **Transactional & Temporal Operational Records**: High-volume tabular histories (orders, purchase logs, shipment status updates, daily buffer levels) and dense vector embeddings for semantic case retrieval.

Attempting to force both data models into a single storage engine introduces severe compromises: relational databases suffer from combinatorial explosion when executing multi-depth graph joins, while graph databases exhibit poor performance on large-scale tabular aggregations and vector similarity indexing.

---

## 2. Decision Drivers

* **Recursive Graph Traversal Performance**: Sub-second queries across 5+ tiers of supplier-to-product dependencies.
* **Transactional ACID Reliability**: Reliable, auditable relational storage for orders, inventory balances, and immutable decision logs.
* **Vector Cosine Search Integration**: Direct indexing of 384-dimension embeddings alongside transactional decision metadata.
* **Declarative ETL Seeding**: Ability to populate both graph and relational stores from a single Domain Profile YAML definition.

---

## 3. Considered Options

* **Option 1: Pure Relational (PostgreSQL Only)**: Recursive Common Table Expressions (CTEs) for graph queries.
* **Option 2: Pure Graph (Neo4j Only)**: Storing all order transactions, inventory snapshots, and embeddings inside Neo4j node properties.
* **Option 3: Hybrid Architecture — Neo4j 5.18 (Graph) + PostgreSQL 16 with pgvector (Relational/Vector)**.

---

## 4. Decision Outcome

**Chosen Option**: **Option 3 — Hybrid Neo4j + PostgreSQL/pgvector**

### Rationale:
1. **Neo4j for Structural Topology & Cascade Detection**:
   * Supply chain disruption impacts propagate topologically. When a tier-2 chip supplier fails, finding all impacted finished goods requires Cypher graph traversals:
     ```cypher
     MATCH (s:Supplier {id: $supplier_id})<-[:SUPPLIED_BY*1..3]-(p:Product)
     RETURN p.name, p.sku
     ```
   * Neo4j executes this traversal in index-free adjacency in $< 2\text{ ms}$, whereas recursive relational SQL CTEs degrade rapidly under scale.
2. **PostgreSQL + pgvector for Transactional Ledger & Semantic RAG**:
   * Order records, safety stock calculations, and the immutable decision ledger (`scof.decision_records`) benefit from mature SQL transactions, indexes, and pgvector cosine distance operations (`<=>`).
3. **Unified Profile Ingestion (ETL)**:
   * The D2 ETL service reads [profiles/mvp-electronics/topology.yaml](file:///d:/projects/SCOF_V1/SCOF/profiles/mvp-electronics/topology.yaml) and seeds both Neo4j nodes/edges and PostgreSQL dimension tables in a single initialization pass (`python -m services.etl.src.main --mode full`).

---

## 5. Pros and Cons of the Selected Option

### Positive Consequences:
* Best-of-breed engine for each data paradigm: native Cypher graph analytics + robust ACID relational vector ledger.
* Clean separation of concerns: Agents query Neo4j for network topology constraints and PostgreSQL for inventory levels.

### Negative Consequences / Trade-offs:
* Requires running two separate database containers (`scof-neo4j` on port 7687 and `scof-postgres` on port 5432).
* Requires dual ETL logic to seed both engines from the active Domain Profile.

---

## 6. Implementation & Compliance Notes

* Neo4j graph schema in [infrastructure/database/neo4j/01_init_graph_schema.cypher](file:///d:/projects/SCOF_V1/SCOF/infrastructure/database/neo4j/01_init_graph_schema.cypher).
* PostgreSQL schema in [infrastructure/database/postgres/01_init_schema.sql](file:///d:/projects/SCOF_V1/SCOF/infrastructure/database/postgres/01_init_schema.sql).
* ETL pipeline in [services/etl/src/main.py](file:///d:/projects/SCOF_V1/SCOF/services/etl/src/main.py).
* Verified via `python scripts/verify_d2.py`.

---

## 7. Related Decisions & Artifacts

* [ADR 003: Vector Database Selection](./003_pgvector_for_semantic_memory.md)
* [ADR 009: Declarative YAML Domain Profiles](./009_declarative_yaml_domain_profiles.md)
* [D2 Knowledge Layer Documentation](file:///d:/projects/SCOF_V1/SCOF/docs/deliverables/D02_knowledge_layer/README.md)
