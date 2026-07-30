# Deliverable D2 Implementation Plan — Knowledge & Data Layer

## Goal Description
Deliverable D2 builds the persistent Knowledge and Data Layer for SCOF before any specialist AI agents or coordinator services are implemented. It provides a structured graph and vector environment to query operational topology, multi-echelon supply chain relationships, and historical decision context. D2 delivers:
1. **Neo4j Graph Store Schema & Cypher Scripts** (`infrastructure/database/neo4j/01_init_graph_schema.cypher`) modeling Manufacturers, Suppliers, Products, Warehouses, Distribution Centers, and Polymorphic Routes with explicit edge properties (`lead_time_days`, `cost`, `minimum_order`, `capacity`, `preferred`, `risk_score`, `contract_id`) and indexes on all node primary keys and attributes.
2. **pgvector Schema Initialization** (`infrastructure/database/postgres/02_init_vector_schema.sql`) creating `scof.decision_records`, `scof.evidence_snippets`, `scof.embeddings`, and `scof.schema_version` with embedding model metadata (`embedding_model`, `embedding_version`, `embedding_dimension`), expanded decision metadata (`decision_type`, `created_by`, `simulation_tick`, `outcome`), and HNSW vector indexing (`vector_cosine_ops`).
3. **Modular Python ETL Pipeline Architecture** (`services/etl/src/`) cleanly decoupled into Extract (`extract.py`), Transform (`transform.py`), Cypher Graph Loading (`load_graph.py`), Vector Store Loading (`load_vector.py`), Standalone Embedding Service (`embedding_service.py`), and Pipeline Orchestrator (`pipeline.py`). Supports `--mode full` and `--mode incremental` execution modes, UNWIND Cypher batching, `executemany()` vector batching, and retry logic with exponential backoff.
4. **Shared Knowledge Access Library** (`shared/scof_shared/knowledge/`) providing reusable Graph RAG and pgvector query abstractions for downstream agents (D3 Demand/Inventory, D4 Supplier/Transport, D6 Consensus Engine).
5. **Automated Health & Invariant Verification Script** (`scripts/verify_d2.py`) callable via `make verify-d2` to validate Neo4j graph integrity, Cypher shortest-path traversals, graph domain invariants (sourcing, storage, and route connectivity checks), pgvector table row counts, deterministic synthetic vector similarity search, and ETL idempotency.

---

## Prerequisites Check

> [!NOTE]
> - **Prerequisite Deliverables**: Deliverable D1 (Simulation Environment & Synthetic Data Foundation) is complete. PostgreSQL (+ pgvector), Neo4j, Redis, and Kafka containers are online, and D1 synthetic data is populated.
> - **Domain Profile**: [`profiles/mvp-electronics/`](../../../profiles/mvp-electronics/) is complete with `topology.yaml` and `disruptions.yaml`.
> - **Repository Structure**: Monorepo scaffolding, `shared/` library, and `docs/deliverables/D02_knowledge_layer/` documentation structure are established.

---

## User Review Required & Design Refinements Incorporated

> [!IMPORTANT]
> **Key Refinements Incorporated for D2 (Architectural Enhancements)**:
> 1. **Modular ETL Pipeline Architecture (`services/etl/src/`)**: Decoupled into `extract.py`, `transform.py`, `load_graph.py`, `load_vector.py`, `embedding_service.py`, and `pipeline.py`.
> 2. **Standalone Embedding Service (`embedding_service.py`)**: Separates text embedding generation from database loaders. Enables swapping models (`MiniLM` -> `BGE` -> `OpenAI` -> `Voyage` -> `Instructor`) without modifying ETL load logic.
> 3. **Embedding Model Metadata Tracking**: `scof.embeddings` table includes `embedding_model`, `embedding_version`, `embedding_dimension`, and `created_at` to prevent future model migration friction.
> 4. **Model-Independent Configurable Embedding Dimensions**: `EMBEDDING_DIMENSION` and `EMBEDDING_MODEL` defined centrally in `services/etl/src/config.py`.
> 5. **Strict PK Alignment**: Neo4j node `id` properties strictly equal PostgreSQL primary key strings (e.g. `mfg-01`, `sup-01`, `prod-101`, `wh-01`, `dc-01`, `route-sup01-wh01`).
> 6. **Standardized Relationship Edge Properties**:
>    - `SUPPLIES`: `lead_time_days`, `cost`, `minimum_order`, `capacity`, `preferred`, `contract_id`
>    - `SHIPS_VIA`: `mode`, `transit_days`, `cost`, `risk_score`
>    - `PRODUCES`: `created_at`, `production_capacity_units`
>    - `STORED_IN`: `max_storage_units`, `storage_cost_per_unit`
>    - `DELIVERS_TO`: `service_level_agreement_days`
>    - `ALTERNATE_FOR`: `cost_delta_pct`, `lead_time_delta_days`
> 7. **Comprehensive Node Indexing**: Indexes explicitly created for `:Manufacturer(id)`, `:Supplier(id)`, `:Product(id)`, `:Warehouse(id)`, `:DistributionCenter(id)`, `:Route(id)`, `:Supplier(reliability_profile)`, and `:Route(mode)`.
> 8. **Expanded Decision Records Schema**: Added `decision_type`, `created_by`, `simulation_tick`, `scenario_id`, `confidence`, and `outcome` fields to support historical decision evaluation by D6.
> 9. **Incremental & Full Loading Interface**: CLI supports `--mode full` and `--mode incremental`.
> 10. **Domain Invariant Verification**: Verification checks supply chain invariants (every Product has ≥1 Supplier, every Warehouse stores ≥1 Product, every Route connects valid facilities).
> 11. **Deterministic Synthetic Embeddings**: Hashing algorithm ensures `verify_d2` vector tests produce identical embeddings across runs.
> 12. **High-Performance Batching & Retries**: Uses Neo4j Cypher `UNWIND` batching, Postgres `executemany()` vector batching, and exponential backoff retry logic.
> 13. **Schema Versioning**: `scof.schema_version` table and Neo4j `:SchemaVersion` node track database migrations.

---

## Open Questions

> [!NOTE]
> None. All 13 architectural enhancements are incorporated and ready for implementation.

---

## Proposed Changes

### Infrastructure (`infrastructure/database/`)

#### [NEW] [01_init_graph_schema.cypher](../../../infrastructure/database/neo4j/01_init_graph_schema.cypher)
- Cypher DDL script creating unique node property constraints on `:Manufacturer(id)`, `:Supplier(id)`, `:Product(id)`, `:Warehouse(id)`, `:DistributionCenter(id)`, and `:Route(id)`. Creates indexes on node IDs, `:Supplier(reliability_profile)`, `:Route(mode)`, and initializes `:SchemaVersion(version='2.0.0')`.

#### [NEW] [02_init_vector_schema.sql](../../../infrastructure/database/postgres/02_init_vector_schema.sql)
- PostgreSQL DDL script creating `scof.decision_records` (with `decision_type`, `created_by`, `simulation_tick`, `outcome`), `scof.evidence_snippets`, `scof.embeddings` (with `embedding_model`, `embedding_version`, `embedding_dimension`), and `scof.schema_version` tables with HNSW cosine similarity index (`idx_embeddings_hnsw`).

---

### Shared Library (`shared/scof_shared/knowledge/`)

#### [NEW] [graph_client.py](../../../shared/scof_shared/knowledge/graph_client.py)
- Reusable Neo4j client providing connection pooling, retry logic, session management, and helper methods for standard graph queries (shortest path, supplier upstream lineage, alternate suppliers, route traversals).

#### [NEW] [vector_client.py](../../../shared/scof_shared/knowledge/vector_client.py)
- Reusable pgvector client providing vector insertion, metadata-aware similarity search (`ORDER BY embedding <=> query_vector LIMIT K`), and decision/evidence snippet retrieval.

---

### Modular ETL Pipeline Service (`services/etl/`)

#### [NEW] [pyproject.toml](../../../services/etl/pyproject.toml)
- Package manifest declaring dependencies: `neo4j`, `psycopg[binary]`, `pgvector`, `pydantic`, `numpy`, `scof-shared`.

#### [NEW] [Dockerfile](../../../services/etl/Dockerfile)
- Container definition for running the D2 ETL pipeline service.

#### [NEW] [config.py](../../../services/etl/src/config.py)
- Configuration module for Neo4j URI (`bolt://localhost:7687`), Neo4j credentials, PostgreSQL connection parameters, `EMBEDDING_MODEL` ("all-MiniLM-L6-v2"), `EMBEDDING_DIMENSION` (384), and batch size settings.

#### [NEW] [extract.py](../../../services/etl/src/extract.py)
- Extraction module reading D1 operational tables from PostgreSQL and YAML files from Domain Profile (`profiles/mvp-electronics/`).

#### [NEW] [transform.py](../../../services/etl/src/transform.py)
- Transformation module converting raw relational rows into typed graph payload objects and structured decision/evidence records with standardized edge properties.

#### [NEW] [load_graph.py](../../../services/etl/src/load_graph.py)
- High-performance graph loader executing Cypher `UNWIND $batch AS row MERGE ...` queries with retry logic to populate Neo4j nodes and edges idempotently.

#### [NEW] [load_vector.py](../../../services/etl/src/load_vector.py)
- High-performance vector loader executing batch `executemany()` operations to write decision records, evidence snippets, and embeddings to PostgreSQL.

#### [NEW] [embedding_service.py](../../../services/etl/src/embedding_service.py)
- Standalone embedding generation service computing deterministic synthetic embeddings for testing or interfacing with embedding models (`MiniLM`, `BGE`, `OpenAI`).

#### [NEW] [pipeline.py](../../../services/etl/src/pipeline.py)
- Pipeline orchestrator executing the 5-step ETL flow: Extract -> Transform -> Load Graph -> Load Vector -> Generate Embeddings. Supports `--mode full` and `--mode incremental`.

#### [NEW] [main.py](../../../services/etl/src/main.py)
- CLI entrypoint accepting `--mode [full|incremental]` arguments, launching `pipeline.py`, logging stats, and reporting execution results.

---

### Scripts & Makefile (`scripts/`, `Makefile`)

#### [NEW] [verify_d2.py](../../../scripts/verify_d2.py)
- Comprehensive health verification script checking:
  1. Neo4j graph connectivity and unique constraints.
  2. Neo4j node and relationship count non-zero checks.
  3. Cypher shortest-path query execution between suppliers and warehouses.
  4. Cypher upstream product sourcing lineage query execution.
  5. **Domain Invariant Checks**:
     - Every `:Product` has ≥1 `:Supplier`
     - Every `:Warehouse` stores ≥1 `:Product`
     - Every `:Route` connects two valid network facilities
  6. Postgres pgvector extension and table initialization checks.
  7. Deterministic vector similarity search execution with score validation.
  8. Idempotency test (verifying re-running ETL in `--mode full` and `--mode incremental` produces zero duplicate nodes or errors).

#### [MODIFY] [Makefile](../../../Makefile)
- Adding target `verify-d2` to run `python scripts/verify_d2.py`.

---

### Tests (`services/etl/tests/`)

#### [NEW] [test_extract_transform.py](../../../services/etl/tests/test_extract_transform.py)
- Unit tests for relational extraction and graph payload formatting.

#### [NEW] [test_graph_loader.py](../../../services/etl/tests/test_graph_loader.py)
- Unit and integration tests for Cypher `UNWIND` batch execution, retry logic, and Neo4j node creation.

#### [NEW] [test_vector_loader.py](../../../services/etl/tests/test_vector_loader.py)
- Unit and integration tests for decision record insertion, embedding metadata tracking, and pgvector table operations.

#### [NEW] [test_embedding_service.py](../../../services/etl/tests/test_embedding_service.py)
- Unit tests for deterministic embedding generation and model decoupling.

#### [NEW] [test_end_to_end_etl.py](../../../services/etl/tests/test_end_to_end_etl.py)
- End-to-end integration test verifying D1 -> D2 data ingestion, domain invariant compliance, graph traversal accuracy, and vector similarity search.

---

### Deliverable Documentation Package (`docs/deliverables/D02_knowledge_layer/`)

#### [MODIFY] [README.md](../../../docs/deliverables/D02_knowledge_layer/README.md)
- Updated overview, requirements summary, prerequisites, document map, module structure, and definition of done.

#### [MODIFY] [implementation_plan.md](../../../docs/deliverables/D02_knowledge_layer/implementation_plan.md)
- Complete technical implementation plan for Deliverable D2.

#### [MODIFY] [graph_schema.md](../../../docs/deliverables/D02_knowledge_layer/graph_schema.md)
- Comprehensive Neo4j graph schema documentation, node labels, properties, relationship edge properties, Cypher DDL, indexes, and sample query patterns.

#### [MODIFY] [vector_schema.md](../../../docs/deliverables/D02_knowledge_layer/vector_schema.md)
- Comprehensive PostgreSQL pgvector schema documentation, table DDL with metadata columns, HNSW index strategy, vector dimension specs, and similarity query templates.

#### [MODIFY] [design_decisions.md](../../../docs/deliverables/D02_knowledge_layer/design_decisions.md)
- Architectural design decisions for D2 (Modular ETL layout, embedding decoupling, metadata tracking, strict PK alignment, edge property specs, domain invariant verification, batching & retries).

#### [MODIFY] [acceptance_evidence.md](../../../docs/deliverables/D02_knowledge_layer/acceptance_evidence.md)
- Evidence log template and test execution outputs for D2 acceptance criteria.

#### [MODIFY] [walkthrough.md](../../../docs/deliverables/D02_knowledge_layer/walkthrough.md)
- Complete step-by-step walkthrough guide for running and verifying D2 Knowledge & Data Layer.

---

## Verification Plan

### Automated Tests
1. **ETL Test Suite**:
   ```bash
   pytest services/etl/tests/
   ```
2. **ETL Pipeline Execution (Full & Incremental Modes)**:
   ```bash
   python -m services.etl.src.main --mode full
   python -m services.etl.src.main --mode incremental
   ```
3. **Automated Health & Invariants Verification Script**:
   ```bash
   make verify-d2
   ```
   or
   ```bash
   python scripts/verify_d2.py
   ```

### Manual Verification
1. **Neo4j Cypher Shell / Browser Verification**:
   Execute Cypher queries against Neo4j (`bolt://localhost:7687`):
   ```cypher
   // Check node counts and schema version
   MATCH (n) RETURN labels(n)[0] AS Label, count(*) AS Count;
   MATCH (v:SchemaVersion) RETURN v.version;

   // Edge property verification
   MATCH (s:Supplier)-[r:SUPPLIES]->(p:Product)
   RETURN s.name, p.name, r.unit_cost, r.lead_time_days, r.is_preferred;

   // Shortest path test
   MATCH p=shortestPath((s:Supplier {id: 'sup-01'})-[*..5]-(w:Warehouse {id: 'wh-01'}))
   RETURN p;
   ```

2. **Direct SQL Vector Query Verification**:
   Query Postgres directly to verify `pgvector` similarity search and metadata tracking:
   ```sql
   SELECT table_name FROM information_schema.tables WHERE table_schema = 'scof';
   SELECT id, embedding_model, embedding_version, embedding_dimension FROM scof.embeddings;
   SELECT id, content_text, 1 - (embedding <=> '[0.01, 0.02, ...]'::vector) AS similarity 
   FROM scof.embeddings 
   ORDER BY embedding <=> '[0.01, 0.02, ...]'::vector 
   LIMIT 3;
   ```
