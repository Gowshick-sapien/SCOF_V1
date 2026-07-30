# Deliverable D2 — Design Decisions

## 1. Context & Motivation
Deliverable D2 builds the Knowledge and Data Layer for SCOF. Specialist agents (D3/D4) and the Consensus Engine (D6) need structured access to multi-hop supply chain graph topologies and vector search over decision histories. The Knowledge Layer must ingest synthetic data from D1, construct a Neo4j graph, populate PostgreSQL pgvector tables, and provide unified access abstractions.

---

## 2. Key Design Decisions

### Decision 1: Modular Decoupled ETL Architecture
- **Choice**: Structure the ETL service (`services/etl/src/`) into modular components: `extract.py`, `transform.py`, `load_graph.py`, `load_vector.py`, `embedding_service.py`, and `pipeline.py`.
- **Rationale**: Clean separation of extraction, transformation, database loading, and vector generation allows each component to scale independently and simplifies maintenance when adding new data sources.

### Decision 2: Standalone Embedding Service (`embedding_service.py`)
- **Choice**: Isolate text embedding generation into `embedding_service.py` separate from database loader logic.
- **Rationale**: Enables swapping embedding models (`MiniLM` -> `BGE` -> `OpenAI` -> `Voyage` -> `Instructor`) without modifying database insertion pipelines.

### Decision 3: Embedding Model Metadata Tracking
- **Choice**: Include `embedding_model`, `embedding_version`, `embedding_dimension`, and `created_at` in `scof.embeddings`.
- **Rationale**: Prevents friction and data corruption during future model migrations by allowing vector search queries to filter by active model version.

### Decision 4: Configurable Model & Dimensionality Settings
- **Choice**: Centralize `EMBEDDING_MODEL` ("all-MiniLM-L6-v2") and `EMBEDDING_DIMENSION` (384) in `services/etl/src/config.py`.
- **Rationale**: Keeps application code model-independent while supporting fixed vector SQL schemas for MVP.

### Decision 5: Strict Graph-Relational Primary Key Alignment
- **Choice**: Neo4j node `id` properties MUST equal PostgreSQL primary keys (`mfg-01`, `sup-01`, `prod-101`, `wh-01`, `dc-01`, `route-sup01-wh01`).
- **Rationale**: Eliminates synthetic key mapping overhead and simplifies cross-store synchronization across SQL and Cypher queries.

### Decision 6: Standardized Edge Property Models
- **Choice**: Define explicit properties on graph relationships (`SUPPLIES`, `SHIPS_VIA`, `PRODUCES`, `STORED_IN`, `DELIVERS_TO`, `ALTERNATE_FOR`).
- **Rationale**: Enables multi-attribute Graph RAG scoring (e.g. evaluating cost, lead time, and risk score directly on graph paths).

### Decision 7: Comprehensive Graph Indexing
- **Choice**: Create explicit indexes on `:Manufacturer(id)`, `:Supplier(id)`, `:Product(id)`, `:Warehouse(id)`, `:DistributionCenter(id)`, `:Route(id)`, `:Supplier(reliability_profile)`, and `:Route(mode)`.
- **Rationale**: Accelerates graph lookup speed for multi-hop Cypher path traversals.

### Decision 8: Expanded Decision Records Schema
- **Choice**: Include `decision_type`, `created_by`, `simulation_tick`, `scenario_id`, `confidence`, and `outcome` in `scof.decision_records`.
- **Rationale**: Gives D6 Consensus Engine rich historical decision context for consensus evaluation.

### Decision 9: Full and Incremental Pipeline Modes
- **Choice**: Support `--mode full` and `--mode incremental` flags in the ETL CLI (`main.py`).
- **Rationale**: Provides flexible execution modes for complete re-hydration vs lightweight updates.

### Decision 10: Domain Invariant Verification
- **Choice**: Expand `scripts/verify_d2.py` to test supply chain invariants (every Product has ≥1 Supplier, every Warehouse stores ≥1 Product, every Route connects valid facilities).
- **Rationale**: Catches subtle ETL data transformation errors beyond basic table row counts.

### Decision 11: Deterministic Synthetic Vector Embeddings
- **Choice**: Use a seed-based hash vector generator for synthetic text embeddings in verification mode.
- **Rationale**: Guarantees 100% deterministic test execution for `verify_d2` vector similarity checks.

### Decision 12: High-Performance Batching & Exponential Retries
- **Choice**: Implement Cypher `UNWIND` batch inserts, Postgres `executemany()` batch inserts, and exponential backoff retries for Neo4j driver connection attempts.
- **Rationale**: Optimizes ingestion throughput and prevents transient container startup failure.

### Decision 13: Schema Migration Versioning
- **Choice**: Maintain `scof.schema_version` table in Postgres and `:SchemaVersion` node in Neo4j.
- **Rationale**: Tracks schema migration states cleanly without manual resets.
