# Deliverable D02 Implementation Plan -- Enterprise Knowledge & Data Fabric

## 1. Goal Description

Deliverable D02 builds the persistent, tri-store Knowledge & Data Fabric for SCOF V2. Moving away from monolithic or toy databases, D02 establishes three specialized data engines configured for distinct access paradigms:
1. **PostgreSQL System of Record**: Transactional truth, foreign key referential integrity, and ACID audit history across 30 domains and 96 tables.
2. **Neo4j Topological Projection**: Read-only graph database optimized for multi-echelon supply network traversals, dependency tracing, and corridor reachability over 3.73M nodes and 2.10M edges.
3. **pgvector Semantic Memory Substrate**: Decoupled 3-tier vector storage enabling cognitive agents to perform semantic similarity search over historical disruptions, agent rationales, and CD2F arbitration logs.

---

## 2. Technical Architecture & Phasing Roadmap

The implementation is executed across three coordinated engineering tracks:

```text
Track 3A: PostgreSQL System of Record
  ├── Deploy schema DDL (96 tables, 165 FKs)
  └── Execute high-throughput SQLite-to-PostgreSQL ETL loader
Track 3B: Neo4j Topological Projection
  ├── Export 93 node and relationship CSV files from relational SoR
  ├── Execute Cypher DDL (59 uniqueness constraints & indexes)
  ├── Load 3,728,199 nodes and 2,104,514 edges via LOAD CSV
  └── Implement 4 bounded traversal MCP tools with scenario masking
Track 3C: pgvector Semantic Memory Substrate
  ├── Deploy 3-tier vector schema (embedding_model, semantic_document, semantic_embedding)
  ├── Configure 384d SentenceTransformers embedding provider (all-MiniLM-L6-v2)
  ├── Generate enterprise memory seed corpus with 100% relational provenance
  └── Encapsulate memory operations behind SemanticMemoryStore API
```

---

## 3. Detailed Track Breakdown

### Track 3A: PostgreSQL System of Record Staging

- **Step 3A.1 (Schema Initialization)**:
  - Execute [`scripts/schema_ddl.sql`](file:///d:/projects/SCOF_V1/SCOF/scripts/schema_ddl.sql) against PostgreSQL 16 to create the `scof` schema, activate `uuid-ossp` and `vector` extensions, and instantiate all 96 tables with 165 physical foreign keys.
- **Step 3A.2 (Data Ingestion Pipeline)**:
  - Implement [`scripts/load_postgresql_data.py`](file:///d:/projects/SCOF_V1/SCOF/scripts/load_postgresql_data.py) utilizing cursor streaming from [`datasets/scof_relational.db`](file:///d:/projects/SCOF_V1/SCOF/datasets/scof_relational.db) and PostgreSQL `COPY` / `executemany` batch transactions.
  - Verify that all 4,358,100 records ingest without truncation or constraint violations.

### Track 3B: Neo4j Enterprise Graph Projection

- **Step 3B.1 (Graph Extraction & CSV Export)**:
  - Extract topological entities from the relational database into 93 CSV files in [`datasets/neo4j_graph/`](file:///d:/projects/SCOF_V1/SCOF/datasets/neo4j_graph/).
  - Ensure canonical node IDs follow standardized prefixes (`FAC-`, `SUP-`, `SKU-`, `LANE-`, `CAT-`).
- **Step 3B.2 (Cypher DDL & Constraints)**:
  - Execute [`datasets/neo4j_graph/import_neo4j_graph.cql`](file:///d:/projects/SCOF_V1/SCOF/datasets/neo4j_graph/import_neo4j_graph.cql) establishing 59 uniqueness constraints and B-Tree indexes across 50 node labels.
- **Step 3B.3 (Bulk Import & Parity Audit)**:
  - Execute batch `LOAD CSV` commands loading 3,728,199 nodes and 2,104,514 relationships.
  - Run Gate 6 Relational-Graph Parity reconciliation audit, confirming 0 mismatches across all 56 verified node and edge types.
- **Step 3B.4 (Bounded MCP Traversal Tools)**:
  - Implement depth-bounded Cypher queries in [`shared/scof_shared/knowledge/graph_client.py`](file:///d:/projects/SCOF_V1/SCOF/shared/scof_shared/knowledge/graph_client.py):
    - `get_upstream_supply_path(facility_id, max_depth=3)`
    - `get_affected_downstream_facilities(disrupted_facility_id, max_hops=2)`
    - `find_alternate_carrier_routes(origin_id, dest_id, max_transit_days=5)`
    - `get_category_assortment_tree(department_id, max_depth=4)`
  - Integrate parameter-based scenario masking (`$disabled_nodes`, `$disabled_edges`) to preserve graph read-only immutability ([ADR 006](file:///d:/projects/SCOF_V1/SCOF/docs/adr/006_immutable_neo4j_topology_with_in_memory_scenario_overlays.md)).

### Track 3C: pgvector Semantic Memory Substrate

- **Step 3C.1 (Three-Tier Vector Schema)**:
  - Deploy three-tier schema tables in PostgreSQL:
    - `scof.embedding_model`: Registry tracking model names, dimensions (384), and distance metrics (`cosine`).
    - `scof.semantic_document`: Document metadata, canonical text, SHA-256 hash, and relational provenance pointers (`source_entity_type`, `source_entity_id`).
    - `scof.semantic_embedding`: Exact 384-dimensional vector values foreign-keyed to model and document IDs with unique composite constraints.
- **Step 3C.2 (Embedding Providers & Model Registry)**:
  - Implement [`SentenceTransformersProvider`](file:///d:/projects/SCOF_V1/SCOF/shared/scof_shared/knowledge/embedding_provider.py) loading the `all-MiniLM-L6-v2` model.
  - Implement deterministic [`MockEmbeddingProvider`](file:///d:/projects/SCOF_V1/SCOF/shared/scof_shared/knowledge/embedding_provider.py) for lightweight CI/CD unit testing without GPU/Torch overhead.
- **Step 3C.3 (Enterprise Seed Corpus & Provenance Validation)**:
  - Implement [`services/etl/src/seed_semantic_memory.py`](file:///d:/projects/SCOF_V1/SCOF/services/etl/src/seed_semantic_memory.py) generating a controlled corpus of historical supply chain disruptions, agent evidence snippets, and CD2F consensus arbitration logs.
  - Enforce Gate P4: 100% of generated documents must validate against real primary keys in the relational database.
- **Step 3C.4 (Service Encapsulation)**:
  - Implement [`SemanticMemoryStore`](file:///d:/projects/SCOF_V1/SCOF/shared/scof_shared/knowledge/semantic_memory_store.py) encapsulating document insertion, deduplication, canonical text normalization, and similarity search.

---

## 4. Verification & Certification Strategy

Verification of Deliverable D02 is governed by two formal validation suites:

1. **Gate 6 Relational-Graph Parity Audit**:
   - Compares relational table row counts against Neo4j node/edge counts across all 50 entity types.
   - Result: 3,728,199 nodes and 2,104,514 edges verified with 0 discrepancies in [`datasets/neo4j_materialization_audit.json`](file:///d:/projects/SCOF_V1/SCOF/datasets/neo4j_materialization_audit.json).
2. **Automated pgvector 8-Gate Verification Suite (`scripts/verify_pgvector_d2.py`)**:
   - `Gate P1`: PostgreSQL `vector` extension active.
   - `Gate P2`: Schema tables, FK cascades, and unique constraints verified.
   - `Gate P3`: Vector dimension invariant == 384 verified.
   - `Gate P4`: 100% of seeded documents resolve to real relational entities.
   - `Gate P5`: Persistence cycle across disconnect/reconnect boundary.
   - `Gate P6`: Idempotent seeding produces 0 duplicate records.
   - `Gate P7`: Real SentenceTransformers semantic ranking: Target document achieves Rank #1 with separation delta $\ge 0.25$ over distant negatives.
   - `Gate P8`: Service encapsulation invariant: agent interfaces consume `SemanticMemoryStore` without importing raw database drivers.
