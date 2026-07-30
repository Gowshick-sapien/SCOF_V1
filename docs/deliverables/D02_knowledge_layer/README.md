# Deliverable D2 — Knowledge & Data Layer

## Overview & Purpose
Deliverable D2 builds the persistent Knowledge and Data Layer for SCOF before any specialist AI agents or coordinator services are implemented. It provides a structured graph store (Neo4j) for multi-echelon supply chain network topology traversals and a vector store (PostgreSQL `pgvector`) for decision record retrieval, evidence snippet context, and model metadata tracking.

---

## Requirements Summary (from SRS)
- **FR-2.1**: Define a Neo4j schema modeling supplier, product, warehouse, distribution center, manufacturer, and route nodes and relationships (`PRODUCES`, `SUPPLIES`, `STORED_IN`, `SHIPS_VIA`, `DELIVERS_TO`, `ALTERNATE_FOR`) with explicit edge properties and comprehensive indexes.
- **FR-2.2**: Define a pgvector schema in Postgres with tables for `decision_records` (with decision types & outcomes), `evidence_snippets`, `embeddings` (with model metadata), and `schema_version` with HNSW vector indexing.
- **FR-2.3**: Provide modular, idempotent ETL scripts (`services/etl/src/`) supporting `--mode full` and `--mode incremental` execution, Cypher `UNWIND` batching, Postgres `executemany()` vector batching, and standalone embedding generation.

---

## Prerequisites & Dependencies
- **Prerequisite Deliverables**: Deliverable D1 (Simulation Environment & Synthetic Data Foundation) is complete. PostgreSQL (+ pgvector), Neo4j, Redis, and Kafka containers are online and healthy.
- **Required System Tools**: Docker (v24+), Python 3.11+, PostgreSQL 16+ (with pgvector), Neo4j 5+.
- **Required Domain Profile Files**:
  - [`profiles/mvp-electronics/topology.yaml`](../../../profiles/mvp-electronics/topology.yaml)
  - [`profiles/mvp-electronics/disruptions.yaml`](../../../profiles/mvp-electronics/disruptions.yaml)

---

## Document Set in this Directory
1. **[`README.md`](./README.md)** (this document): Overview, requirements, prerequisites, document map, and acceptance criteria.
2. **[`implementation_plan.md`](./implementation_plan.md)**: Detailed step-by-step technical implementation plan and verification strategy for Deliverable D2.
3. **[`design_decisions.md`](./design_decisions.md)**: Architectural design decisions for modular ETL layout, embedding decoupling, metadata tracking, strict PK alignment, edge properties, domain invariant checks, and batching.
4. **[`graph_schema.md`](./graph_schema.md)**: Comprehensive Neo4j graph schema, node labels, primary key alignment, relationship edge properties, Cypher DDL, indexes, and sample query patterns.
5. **[`vector_schema.md`](./vector_schema.md)**: Comprehensive PostgreSQL pgvector schema, table DDL with metadata columns, HNSW index strategy, vector dimension specs, and similarity query templates.
6. **[`acceptance_evidence.md`](./acceptance_evidence.md)**: Empirical test logs, Cypher query results, and vector similarity search evidence.
7. **[`walkthrough.md`](./walkthrough.md)**: Complete step-by-step walkthrough guide for running and verifying D2 Knowledge & Data Layer.

---

## Module Structure

```
infrastructure/
    database/
        neo4j/
            01_init_graph_schema.cypher # Neo4j constraints, indexes & schema versioning
        postgres/
            02_init_vector_schema.sql  # pgvector decision_records, evidence_snippets, embeddings, schema_version

shared/
    scof_shared/
        knowledge/
            graph_client.py            # Shared Neo4j Cypher query helper
            vector_client.py           # Shared pgvector similarity search helper

services/
    etl/
        src/
            config.py                  # Neo4j URI, credentials, Postgres connection & embedding model settings
            extract.py                 # Relational & profile data extraction module
            transform.py               # Graph & vector payload transformation module
            load_graph.py              # Cypher UNWIND batch graph loader
            load_vector.py             # Batch vector & decision loader
            embedding_service.py       # Standalone embedding generation service
            pipeline.py                # 5-step ETL pipeline orchestrator (full/incremental)
            main.py                    # Modular ETL execution CLI entry point (--mode full|incremental)

        tests/
            test_extract_transform.py  # Data transformation unit tests
            test_graph_loader.py       # UNWIND Cypher graph loader unit tests
            test_vector_loader.py      # Batch vector loader unit tests
            test_embedding_service.py  # Embedding service unit tests
            test_end_to_end_etl.py     # End-to-end integration test

scripts/
    verify_d2.py                       # Health & domain invariant verification script for D2
```

---

## Standalone Acceptance Criteria ("Definition of Done")
1. Running Neo4j container (`bolt://localhost:7687`) and PostgreSQL (`localhost:5432`) are online with schema constraints and version tracking established.
2. Executing `python -m services.etl.src.main --mode full` runs the modular 5-step ETL pipeline, populating Neo4j graph nodes/edges with explicit edge properties from D1 data using Cypher `UNWIND ... MERGE` statements and seeding pgvector decision records and embeddings with metadata.
3. Running Cypher queries (e.g. shortest path between supplier `sup-01` and warehouse `wh-01`, upstream product sourcing lineage for `prod-101`) returns sane results without any agent code existing.
4. Executing pgvector similarity search (`ORDER BY embedding <=> query_vector LIMIT K`) returns relevant decision records with cosine similarity score > 0.80 and verifies embedding model metadata.
5. Re-running the ETL script (`python -m services.etl.src.main --mode incremental`) is completely idempotent and produces zero duplicate nodes or errors.
6. Running `python scripts/verify_d2.py` or `make verify-d2` passes 100% of automated health, path traversal, and domain invariant checks.
7. Running `pytest services/etl/tests/` passes 100%.
